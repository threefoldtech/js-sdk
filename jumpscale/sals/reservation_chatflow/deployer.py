import base64
import re
import uuid
from collections import defaultdict
from decimal import Decimal
from textwrap import dedent
import requests
import random
import gevent
import netaddr
from nacl.public import Box
from contextlib import ContextDecorator
from jumpscale.clients.explorer.models import DiskType, NextAction, WorkloadType, ZDBMode
from jumpscale.core.base import StoredFactory
from jumpscale.loader import j
from jumpscale.packages.tfgrid_solutions.models import PoolConfig
from jumpscale.sals.chatflows.chatflows import StopChatFlow
from jumpscale.sals.zos.zos import Zosv2
from jumpscale.clients.explorer.models import ResourceUnitAmount

GATEWAY_WORKLOAD_TYPES = [
    WorkloadType.Domain_delegate,
    WorkloadType.Gateway4to6,
    WorkloadType.Subdomain,
    WorkloadType.Reverse_proxy,
    WorkloadType.Proxy,
]

pool_factory = StoredFactory(PoolConfig)
pool_factory.always_reload = True

NODE_BLOCKING_WORKLOAD_TYPES = [
    WorkloadType.Container,
    WorkloadType.Network_resource,
    WorkloadType.Volume,
    WorkloadType.Zdb,
]


DOMAINS_DISALLOW_PREFIX = "TFGATEWAY:DOMAINS:DISALLOWED"
DOMAINS_DISALLOW_EXPIRATION = 60 * 60 * 4  # 4 hours
DOMAINS_COUNT_KEY = "TFGATEWAY:DOMAINS:FAILURE_COUNT"


class DeploymentFailed(StopChatFlow):
    def __init__(self, msg=None, solution_uuid=None, wid=None, identity_name=None, **kwargs):
        super().__init__(msg, **kwargs)
        self.solution_uuid = solution_uuid
        self.wid = wid
        self.identity_name = identity_name


class deployment_context(ContextDecorator):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        if exc_type != DeploymentFailed:
            return
        if exc.solution_uuid:
            # cancel related workloads
            j.logger.info(f"canceling workload ids of solution_uuid: {exc.solution_uuid}")
            j.sals.reservation_chatflow.solutions.cancel_solution_by_uuid(exc.solution_uuid, exc.identity_name)
        if exc.wid:
            # block the failed node if the workload is network or container
            zos = j.sals.zos.get(exc.identity_name)
            workload = zos.workloads.get(exc.wid)
            if workload.info.workload_type in NODE_BLOCKING_WORKLOAD_TYPES:
                j.logger.info(f"blocking node {workload.info.node_id} for failed workload {workload.id}")
                j.sals.reservation_chatflow.reservation_chatflow.block_node(workload.info.node_id)


class NetworkView:
    class dry_run_context(ContextDecorator):
        def __init__(self, test_network_name, identity_name=None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.test_network_name = test_network_name
            self.identity_name = identity_name or j.core.identity.me.instance_name

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            network_view = NetworkView(self.test_network_name, identity_name=self.identity_name)
            for workload in network_view.network_workloads:
                j.sals.zos.get(self.identity_name).workloads.decomission(workload.id)

    def __init__(self, name, workloads=None, nodes=None, identity_name=None):
        self.identity_name = identity_name or j.core.identity.me.instance_name
        self.name = name
        identity_tid = j.core.identity.get(self.identity_name).tid
        if not workloads:
            workloads = j.sals.zos.get(self.identity_name).workloads.list(identity_tid, NextAction.DEPLOY)
        self.workloads = workloads
        self.used_ips = []
        self.network_workloads = []
        nodes = nodes or {node.node_id for node in j.sals.zos.get(self.identity_name)._explorer.nodes.list()}
        self._fill_used_ips(self.workloads, nodes)
        self._init_network_workloads(self.workloads, nodes)
        if self.network_workloads:
            self.iprange = self.network_workloads[0].network_iprange
        else:
            self.iprange = "can't be retrieved"

    def _init_network_workloads(self, workloads, nodes=None):
        nodes = nodes or {node.node_id for node in j.sals.zos.get(self.identity_name)._explorer.nodes.list()}
        for workload in workloads:
            if workload.info.node_id not in nodes:
                continue
            if workload.info.next_action != NextAction.DEPLOY:
                continue
            if workload.info.workload_type == WorkloadType.Network_resource and workload.name == self.name:
                self.network_workloads.append(workload)

    def _fill_used_ips(self, workloads, nodes=None):
        nodes = nodes or {node.node_id for node in j.sals.zos.get(self.identity_name)._explorer.nodes.list()}
        for workload in workloads:
            if workload.info.node_id not in nodes:
                continue
            if workload.info.next_action != NextAction.DEPLOY:
                continue
            if workload.info.workload_type == WorkloadType.Kubernetes:
                if workload.network_id == self.name:
                    self.used_ips.append(workload.ipaddress)
            elif workload.info.workload_type == WorkloadType.Container:
                for conn in workload.network_connection:
                    if conn.network_id == self.name:
                        self.used_ips.append(conn.ipaddress)

    def add_node(self, node, pool_id, subnet=""):
        if not subnet:
            used_ip_ranges = set()
            for workload in self.network_workloads:
                if workload.info.node_id == node.node_id:
                    return
                used_ip_ranges.add(workload.iprange)
                for peer in workload.peers:
                    used_ip_ranges.add(peer.iprange)
            else:
                network_range = netaddr.IPNetwork(self.iprange)
                for idx, subnet in enumerate(network_range.subnet(24)):
                    if str(subnet) not in used_ip_ranges:
                        break
                else:
                    raise StopChatFlow("Failed to find free network")
        network = j.sals.zos.get(self.identity_name).network.create(self.iprange, self.name)
        node_workloads = {}
        for net_workload in self.network_workloads:
            node_workloads[net_workload.info.node_id] = net_workload
        network.network_resources = list(node_workloads.values())  # add only latest network resource for each node
        j.sals.zos.get(self.identity_name).network.add_node(network, node.node_id, str(subnet), pool_id)
        return network

    def add_multiple_nodes(self, node_ids, pool_ids):
        used_ip_ranges = set()
        existing_nodes = set()
        for workload in self.network_workloads:
            used_ip_ranges.add(workload.iprange)
            for peer in workload.peers:
                used_ip_ranges.add(peer.iprange)
            if workload.info.node_id in node_ids:
                existing_nodes.add(workload.info.node_id)

        if len(existing_nodes) == len(node_ids):
            return

        node_to_range = {}
        node_to_pool = {}
        for idx, node_id in enumerate(node_ids):
            if node_id in existing_nodes:
                continue
            node_to_pool[node_id] = pool_ids[idx]
            network_range = netaddr.IPNetwork(self.iprange)
            for _, subnet in enumerate(network_range.subnet(24)):
                subnet = str(subnet)
                if subnet not in used_ip_ranges:
                    node_to_range[node_id] = subnet
                    used_ip_ranges.add(subnet)
                    break
            else:
                raise StopChatFlow("Failed to find free network")

        zos = j.sals.zos.get()
        network = zos.network.create(self.iprange, self.name)
        node_workloads = {}
        for net_workload in self.network_workloads:
            node_workloads[net_workload.info.node_id] = net_workload
        network.network_resources = list(node_workloads.values())  # add only latest network resource for each node

        for node_id, node_range in node_to_range.items():
            zos.network.add_node(network, node_id, node_range, node_to_pool[node_id])
        return network

    def add_access(self, node_id=None, use_ipv4=True, pool_id=None):
        if node_id and not pool_id:
            raise StopChatFlow("You must specify the pool id if you specify the node id")
        node_id = node_id or self.network_workloads[0].info.node_id
        pool_id = pool_id or self.network_workloads[0].info.pool_id
        used_ip_ranges = set()
        for workload in self.network_workloads:
            used_ip_ranges.add(workload.iprange)
            for peer in workload.peers:
                used_ip_ranges.add(peer.iprange)
        else:
            network_range = netaddr.IPNetwork(self.iprange)
            for idx, subnet in enumerate(network_range.subnet(24)):
                if str(subnet) not in used_ip_ranges:
                    break
            else:
                raise StopChatFlow("Failed to find free network")
        network = j.sals.zos.get(self.identity_name).network.create(self.iprange, self.name)
        node_workloads = {}
        for net_workload in self.network_workloads:
            node_workloads[net_workload.info.node_id] = net_workload
        network.network_resources = list(node_workloads.values())  # add only latest network resource for each node
        if node_id not in node_workloads:
            j.sals.zos.get(self.identity_name).network.add_node(network, node_id, str(subnet), pool_id=pool_id)
        wg_quick = j.sals.zos.get(self.identity_name).network.add_access(network, node_id, str(subnet), ipv4=use_ipv4)
        return network, wg_quick

    def delete_node(self, node_id):
        zos = j.sals.zos.get(self.identity_name)
        to_delete_wids = []
        network = zos.network.create(self.iprange, self.name)
        for workload in self.network_workloads:
            if workload.info.node_id == node_id:
                to_delete_wids.append(workload.id)
                to_delete_wids.extend(zos.network.delete_node(network, node_id))
        for wid in to_delete_wids:
            zos.workloads.decomission(wid)
        for wid in to_delete_wids:
            ChatflowDeployer().wait_workload_deletion(wid)
        for w in network.network_resources:
            wid = zos.workloads.deploy(w)
            j.logger.info(f"deploying workload {wid}")

    def delete_access(self, ip_range, node_id=None):
        node_id = node_id or self.network_workloads[0].info.node_id
        node_workloads = {}
        for net_workload in self.network_workloads:
            node_workloads[net_workload.info.node_id] = net_workload
        network = j.sals.zos.get(self.identity_name).network.create(self.iprange, self.name)
        network.network_resources = list(node_workloads.values())
        network = j.sals.zos.get(self.identity_name).network.delete_access(network, node_id, ip_range)
        return network

    def get_node_range(self, node):
        for workload in self.network_workloads:
            if workload.info.next_action != NextAction.DEPLOY:
                continue
            if workload.info.node_id == node.node_id:
                return workload.iprange
        raise StopChatFlow(f"Node {node.node_id} is not part of network")

    def copy(self):
        return NetworkView(self.name, identity_name=self.identity_name)

    def get_node_free_ips(self, node):
        ip_range = self.get_node_range(node)
        freeips = []
        hosts = netaddr.IPNetwork(ip_range).iter_hosts()
        next(hosts)  # skip ip used by node
        for host in hosts:
            ip = str(host)
            if ip not in self.used_ips:
                freeips.append(ip)
        return freeips

    def get_free_ip(self, node):
        ip_range = self.get_node_range(node)
        hosts = netaddr.IPNetwork(ip_range).iter_hosts()
        next(hosts)  # skip ip used by node
        for host in hosts:
            ip = str(host)
            if ip not in self.used_ips:
                self.used_ips.append(ip)
                return ip
        return None

    def dry_run(self, test_network_name=None, node_ids=None, pool_ids=None, bot=None, breaking_node_ids=None):
        name = test_network_name or uuid.uuid4().hex
        breaking_node_ids = breaking_node_ids or node_ids
        if bot:
            bot.md_show_update("Starting dry run to check nodes status")
        ip_range = netaddr.IPNetwork("10.10.0.0/16")

        if any([node_ids, pool_ids]) and not all([node_ids, pool_ids]):
            raise StopChatFlow("you must specify both pool ids and node ids together")
        node_pool_dict = {}
        if node_ids:
            for idx, node_id in enumerate(node_ids):
                node_pool_dict[node_id] = pool_ids[idx]
        else:
            for workload in self.network_workloads:
                node_pool_dict[workload.info.node_id] = workload.info.pool_id
            node_ids = list(node_pool_dict.keys())
            pool_ids = list(node_pool_dict.values())

        node_ids = list(set(node_ids))
        network = j.sals.zos.get(self.identity_name).network.create(str(ip_range), name)
        for idx, subnet in enumerate(ip_range.subnet(24)):
            if idx == len(node_ids):
                break
            j.sals.zos.get(self.identity_name).network.add_node(
                network, node_ids[idx], str(subnet), node_pool_dict[node_ids[idx]]
            )
        result = []
        for resource in network.network_resources:
            if bot:
                bot.md_show_update(f"testing deployment on node {resource.info.node_id}")
            try:
                result.append(j.sals.zos.get(self.identity_name).workloads.deploy(resource))
            except Exception as e:
                raise StopChatFlow(
                    f"failed to deploy workload on node {resource.info.node_id} due to" f" error {str(e)}"
                )
        for idx, wid in enumerate(result):
            try:
                deployer.wait_workload(wid, bot, 2)
            except StopChatFlow:
                workload = j.sals.zos.get(self.identity_name).workloads.get(wid)
                # if not a breaking nodes (old node not used for deployment) we can overlook it
                if workload.info.node_id not in breaking_node_ids:
                    continue
                j.sals.reservation_chatflow.reservation_chatflow.block_node(network.network_resources[idx].info.node_id)
                raise DeploymentFailed(
                    "Network nodes dry run failed on node" f" {network.network_resources[idx].info.node_id}", wid=wid
                )


class ChatflowDeployer:
    def __init__(self):
        self.workloads = defaultdict(
            lambda: defaultdict(lambda: defaultdict(list))
        )  # Next Action: workload_type: pool_id: [workloads]

    @property
    def _explorer(self):
        return j.core.identity.me.explorer

    def load_user_workloads(self, next_action=NextAction.DEPLOY):
        all_workloads = j.sals.zos.get().workloads.list(j.core.identity.me.tid, next_action)
        self.workloads.pop(next_action, None)
        for workload in all_workloads:
            if workload.info.metadata:
                workload.info.metadata = self.decrypt_metadata(workload.info.metadata)
                try:
                    j.data.serializers.json.loads(workload.info.metadata)
                except:
                    workload.info.metadata = "{}"
            else:
                workload.info.metadata = "{}"
            self.workloads[workload.info.next_action][workload.info.workload_type][workload.info.pool_id].append(
                workload
            )

    def decrypt_metadata(self, encrypted_metadata, identity_name=None):
        identity_name = identity_name or j.core.identity.me.instance_name
        identity = j.core.identity.get(identity_name)
        try:
            pk = identity.nacl.signing_key.verify_key.to_curve25519_public_key()
            sk = identity.nacl.signing_key.to_curve25519_private_key()
            box = Box(sk, pk)
            return box.decrypt(base64.b85decode(encrypted_metadata.encode())).decode()
        except Exception as e:
            j.logger.warning(f"error when decrypting metadata. {str(e)}")
            return "{}"

    def list_networks(self, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            self.load_user_workloads(next_action=next_action)
        networks = {}  # name: last child network resource
        for pool_id in self.workloads[next_action][WorkloadType.Network_resource]:
            for workload in self.workloads[next_action][WorkloadType.Network_resource][pool_id]:
                networks[workload.name] = workload
        all_workloads = []
        for pools_workloads in self.workloads[next_action].values():
            for pool_id, workload_list in pools_workloads.items():
                all_workloads += workload_list
        network_views = {}
        nodes = {node.node_id for node in j.sals.zos.get()._explorer.nodes.list()}
        for network_name in networks:
            network_views[network_name] = NetworkView(network_name, all_workloads, nodes)
        return network_views

    def _pool_form(self, bot):
        form = bot.new_form()
        cu = form.int_ask("Required Amount of Compute Unit (CU)", required=True, min=0, default=0)
        su = form.int_ask("Required Amount of Storage Unit (SU)", required=True, min=0, default=0)
        ipv4u = form.int_ask("Required Amount of Public IP Unit (IPv4U)", required=True, min=0, default=0)
        time_unit = form.drop_down_choice(
            "Please choose the duration unit", ["Day", "Month", "Year"], required=True, default="Month"
        )
        ttl = form.int_ask("Please specify the pools time-to-live", required=True, min=1, default=0)
        form.ask(
            """- Compute Unit (CU) is the amount of data processing power specified as the number of virtual CPU cores (logical CPUs) and RAM (Random Access Memory).
- Storage Unit (SU) is the size of data storage capacity.

You can get more detail information about cloud units on the wiki: <a href="https://wiki.threefold.io/#/grid_concepts?id=cloud-units-v4" target="_blank">Cloud units details</a>.


The way this form works is you define how much cloud units you want to reserve and define for how long you would like the selected amount of cloud units.
As an example, if you want to be able to run some workloads that consumes `5CU` and `10SU` worth of capacity for `2 month`, you would specify:

- CU: 5
- SU: 10
- Duration unit: Month
- Duration: 2
""",
            md=True,
        )
        ttl = ttl.value
        time_unit = time_unit.value
        if time_unit == "Day":
            days = 1
        elif time_unit == "Month":
            days = 30
        elif time_unit == "Year":
            days = 365
        else:
            raise j.exceptions.Input("Invalid duration unit")

        cu = cu.value * 60 * 60 * 24 * days * ttl
        su = su.value * 60 * 60 * 24 * days * ttl
        ipv4u = ipv4u.value * 60 * 60 * 24 * days * ttl
        return (cu, su, ipv4u, ["TFT"])

    def create_pool(self, bot):
        cu, su, ipv4u, currencies = self._pool_form(bot)
        all_farms = self._explorer.farms.list()
        available_farms = {}
        farms_by_name = {}
        for farm in all_farms:
            if ipv4u and not farm.ipaddresses:
                continue
            farm_assets = [w.asset for w in farm.wallet_addresses]
            if currencies[0] not in farm_assets:
                continue
            res = self.check_farm_capacity(farm.name, currencies)
            available = res[0]
            resources = res[1:]
            if available:
                available_farms[farm.name] = resources
                farms_by_name[farm.name] = farm
        farm_messages = {}
        for farm in available_farms:
            farm_assets = [w.asset for w in farms_by_name[farm].wallet_addresses]
            if currencies[0] not in farm_assets:
                continue
            resources = available_farms[farm]
            farm_obj = farms_by_name[farm]
            location_list = [farm_obj.location.continent, farm_obj.location.country, farm_obj.location.city]
            location = "-".join([info for info in location_list if info])
            if location:
                location = f" location: {location}"
            farm_messages[
                f"{farm.capitalize()}{location}: CRU: {resources[0]} SRU: {resources[1]} HRU: {resources[2]} MRU {resources[3]}"
            ] = farm
        if not farm_messages:
            raise StopChatFlow(
                f"There are no available farms that have enough resources for this deployment: currency: {currencies[0]}, cu: {cu}, su: {su}, ipv4u: {ipv4u} "
            )
        selected_farm = bot.drop_down_choice(
            "Please choose a farm to reserve capacity from. By reserving IT Capacity, you are purchasing the capacity from one of the farms. The available Resource Units (RU): CRU, MRU, HRU, SRU, NRU are displayed for you to make a more-informed decision on farm selection. ",
            list(farm_messages.keys()),
            required=True,
        )
        farm = farm_messages[selected_farm]
        try:
            pool_info = j.sals.zos.get().pools.create(cu, su, ipv4u, farm, currencies)
        except Exception as e:
            raise StopChatFlow(f"failed to reserve pool.\n{str(e)}")
        # Make sure we have amount to pay can set the custom farm prices to 0
        # Or gateways farms which don't require payment
        if pool_info.escrow_information.amount > 0:
            qr_code = self.show_payment(pool_info, bot)
            self.wait_pool_reservation(pool_info.reservation_id, 30, qr_code=qr_code, bot=bot)
        return pool_info

    def extend_pool(self, bot, pool_id):
        cu, su, ipv4u, currencies = self._pool_form(bot)
        currencies = ["TFT"]
        try:
            pool_info = j.sals.zos.get().pools.extend(pool_id, cu, su, ipv4u, currencies=currencies)
        except Exception as e:
            raise StopChatFlow(f"failed to extend pool.\n{str(e)}")
        qr_code = self.show_payment(pool_info, bot)
        pool = j.sals.zos.get().pools.get(pool_id)
        self.wait_pool_reservation(pool_info.reservation_id, 10, qr_code, bot)
        return pool_info

    def check_farm_capacity(self, farm_name, currencies=None, sru=None, cru=None, mru=None, hru=None, ip_version=None):
        zos = j.sals.zos.get()
        node_filter = None
        if j.core.config.get("OVER_PROVISIONING"):
            cru = None
            mru = None
        if ip_version and ip_version not in ["IPv4", "IPv6"]:
            raise j.exceptions.Runtime(f"{ip_version} is not a valid IP Version")
        else:
            if ip_version == "IPv4":
                node_filter = zos.nodes_finder.filter_accessnode_ip4
            elif ip_version == "IPv6":
                node_filter = zos.nodes_finder.filter_accessnode_ip6
        currencies = currencies or []
        farm_nodes = zos.nodes_finder.nodes_search(farm_name=farm_name)
        available_cru = 0
        available_sru = 0
        available_mru = 0
        available_hru = 0
        running_nodes = 0
        blocked_nodes = j.sals.reservation_chatflow.reservation_chatflow.list_blocked_nodes()
        access_node = None
        for node in farm_nodes:
            if "FreeTFT" in currencies and not node.free_to_use:
                continue
            if not zos.nodes_finder.filter_is_up(node):
                continue
            if node.node_id in blocked_nodes:
                continue
            if not access_node and ip_version and node_filter(node):
                access_node = node
            running_nodes += 1
            available_cru += node.total_resources.cru - node.reserved_resources.cru
            available_sru += node.total_resources.sru - node.reserved_resources.sru
            available_mru += node.total_resources.mru - node.reserved_resources.mru
            available_hru += node.total_resources.hru - node.reserved_resources.hru

        farm_id = self._explorer.farms.get(farm_name=farm_name).id
        gateways = [g for g in self._explorer.gateway.list(farm_id) if zos.gateways_finder.filter_is_up(g)]
        running_nodes += len(gateways)

        if not running_nodes:
            return False, available_cru, available_sru, available_mru, available_hru
        if sru and available_sru < sru:
            return False, available_cru, available_sru, available_mru, available_hru
        if cru and available_cru < cru:
            return False, available_cru, available_sru, available_mru, available_hru
        if mru and available_mru < mru:
            return False, available_cru, available_sru, available_mru, available_hru
        if hru and available_hru < hru:
            return False, available_cru, available_sru, available_mru, available_hru
        if ip_version and not access_node:
            return False, available_cru, available_sru, available_mru, available_hru
        return True, available_cru, available_sru, available_mru, available_hru

    def show_payment(self, pool, bot):
        escrow_info = pool.escrow_information
        resv_id = pool.reservation_id
        escrow_address = escrow_info.address
        escrow_asset = escrow_info.asset
        total_amount = escrow_info.amount
        if not total_amount:
            return
        total_amount_dec = Decimal(total_amount) / Decimal(1e7)
        total_amount = "{0:f}".format(total_amount_dec)

        wallets = j.sals.reservation_chatflow.reservation_chatflow.list_wallets()
        wallet_names = []
        for w in wallets.keys():
            wallet = j.clients.stellar.get(w)
            try:
                balances = wallet.get_balance().balances
            except:
                continue
            for balance in balances:
                if balance.asset_code in escrow_asset:
                    if float(balance.balance) > float(total_amount):
                        wallet_names.append(w)
                    else:
                        break
        wallet_names.append("External Wallet (QR Code)")
        self.msg_payment_info, qr_code = self.get_qr_code_payment_info(pool)
        message = f"""
        <h3>Billing details:</h3><br>
        {self.msg_payment_info}
        <br><hr><br>
        <h3> Choose a wallet name to use for payment or proceed with payment through External wallet (QR Code) </h3>
        """
        result = bot.single_choice(message, wallet_names, html=True, required=True)
        if result == "External Wallet (QR Code)":
            msg_text = f"""
            <h3>Make a Payment</h3>
            Scan the QR code with your wallet (do not change the message) or enter the information below manually and proceed with the payment. Make sure to put p-{resv_id} as memo_text value.

            {self.msg_payment_info}

            """
            bot.qrcode_show(data=qr_code, msg=msg_text, scale=4, update=True, html=True)
        else:
            wallet = wallets[result]
            wallet.transfer(
                destination_address=escrow_address, amount=total_amount, asset=escrow_asset, memo_text=f"p-{resv_id}"
            )
            return None
        return qr_code

    def list_pools(self, cu=None, su=None, ipv4u=None):
        all_pools = [p for p in j.sals.zos.get().pools.list() if p.node_ids]

        available_pools = {}
        for pool in all_pools:
            hidden = False
            name = ""
            if f"pool_{pool.pool_id}" in pool_factory.list_all():
                local_config = pool_factory.get(f"pool_{pool.pool_id}")
                hidden = local_config.hidden
                name = local_config.name
            if hidden:
                continue
            res = self.check_pool_capacity(pool, cu, su, ipv4u)
            available = res[0]
            if available:
                resources = res[1:]
                if name:
                    resources += (name,)
                available_pools[pool.pool_id] = resources
        return available_pools

    def check_pool_capacity(self, pool, cu=None, su=None, ipv4u=None):
        available_su = pool.sus
        available_cu = pool.cus
        available_ipv4u = pool.ipv4us
        if pool.empty_at < 0:
            return False, 0, 0
        if cu and available_cu < cu:
            return False, available_cu, available_su, available_ipv4u
        if su and available_su < su:
            return False, available_cu, available_su, available_ipv4u
        if ipv4u and available_ipv4u < ipv4u:
            return False, available_cu, available_su, available_ipv4u
        if (cu or su) and pool.empty_at < j.data.time.now().timestamp:
            return False, 0, 0
        return True, available_cu, available_su, available_ipv4u

    def select_pool(
        self,
        bot,
        cu=None,
        su=None,
        ipv4u=None,
        sru=None,
        mru=None,
        hru=None,
        cru=None,
        available_pools=None,
        workload_name=None,
    ):
        if j.config.get("OVER_PROVISIONING"):
            cru = 0
            mru = 0
        available_pools = available_pools or self.list_pools(cu, su, ipv4u)
        if not available_pools:
            raise StopChatFlow("no available pools with enough capacity for your workload")
        pool_messages = {}
        for pool in available_pools:
            nodes = j.sals.zos.get().nodes_finder.nodes_by_capacity(pool_id=pool, sru=sru, mru=mru, hru=hru, cru=cru)
            if not nodes:
                continue

            pool_cus, pool_sus, pool_ipv4us = available_pools[pool][:3]
            pool_msg = f"Pool: {pool} cu: {pool_cus} su: {pool_sus} ipv4u: {pool_ipv4us}"
            if len(available_pools[pool]) > 3:
                pool_msg += f" Name: {available_pools[pool][3]}"
            pool_messages[pool_msg] = pool
        if not pool_messages:
            raise StopChatFlow("no available resources in the farms bound to your pools")
        msg = "Please select a pool"
        if workload_name:
            msg += f" for {workload_name}"
        pool = bot.drop_down_choice(msg, list(pool_messages.keys()), required=True)
        return pool_messages[pool]

    def get_pool_farm_id(self, pool_id=None, pool=None, identity_name=None):
        zos = j.sals.zos.get(identity_name)
        pool = pool or zos.pools.get(pool_id)
        pool_id = pool.pool_id
        if not pool.node_ids:
            raise StopChatFlow(f"Pool {pool_id} doesn't contain any nodes")
        farm_id = None
        while not farm_id:
            for node_id in pool.node_ids:
                try:
                    node = zos._explorer.nodes.get(node_id)
                    farm_id = node.farm_id
                    break
                except requests.exceptions.HTTPError:
                    continue
            return farm_id or -1

    def ask_name(self, bot, msg=None):
        msg = (
            msg
            or "Please enter a name for your workload (Can be used to prepare domain for you and needed to track your solution on the grid)"
        )
        name = bot.string_ask(msg, required=True, field="name", is_identifier=True)

        return name

    def ask_email(self, bot):
        valid = False
        email = None
        regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        while not valid:
            email = bot.string_ask("Please enter your email address", required=True, field="email")
            valid = re.search(regex, email) is not None
            if not valid:
                bot.md_show("Please enter a valid email address")
        return email

    def ask_ipv6(self, bot, workload_name=None):
        workload_name = workload_name or "your workload"
        ipv6 = bot.single_choice(
            f"Do you want to assign a global IPv6 address to {workload_name}?",
            options=["YES", "NO"],
            default="NO",
            required=True,
        )
        return ipv6 == "YES"

    def encrypt_metadata(self, metadata, identity_name=None):
        if isinstance(metadata, dict):
            metadata = j.data.serializers.json.dumps(metadata)
        identity_name = identity_name or j.core.identity.me.instance_name
        pk = j.core.identity.get(identity_name).nacl.signing_key.verify_key.to_curve25519_public_key()
        sk = j.core.identity.get(identity_name).nacl.signing_key.to_curve25519_private_key()
        box = Box(sk, pk)
        encrypted_metadata = base64.b85encode(box.encrypt(metadata.encode())).decode()
        return encrypted_metadata

    def deploy_network(
        self, name, access_node, ip_range, ip_version, pool_id, identity_name=None, description="", **metadata
    ):
        identity_name = identity_name or j.core.identity.me.instance_name
        network = j.sals.zos.get(identity_name).network.create(ip_range, name)
        node_subnets = netaddr.IPNetwork(ip_range).subnet(24)
        network_config = dict()
        use_ipv4 = ip_version == "IPv4"

        j.sals.zos.get(identity_name).network.add_node(network, access_node.node_id, str(next(node_subnets)), pool_id)
        wg_quick = j.sals.zos.get(identity_name).network.add_access(
            network, access_node.node_id, str(next(node_subnets)), ipv4=use_ipv4
        )
        network_config["wg"] = wg_quick
        wg_dir = j.sals.fs.join_paths(j.core.dirs.CFGDIR, "wireguard")
        j.sals.fs.mkdirs(wg_dir)
        j.sals.fs.write_file(j.sals.fs.join_paths(wg_dir, f"{identity_name}_{name}.conf"), wg_quick)

        ids = []
        parent_id = None
        for workload in network.network_resources:
            metadata["parent_network"] = parent_id
            workload.info.metadata = self.encrypt_metadata(metadata, identity_name)
            workload.info.description = (
                description if description else j.data.serializers.json.dumps({"parent_id": parent_id})
            )
            ids.append(j.sals.zos.get(identity_name).workloads.deploy(workload))
            parent_id = ids[-1]
        network_config["ids"] = ids
        network_config["rid"] = ids[0]
        return network_config

    def add_access(
        self,
        network_name,
        network_view=None,
        node_id=None,
        pool_id=None,
        use_ipv4=True,
        bot=None,
        identity_name=None,
        description="",
        **metadata,
    ):
        identity_name = identity_name or j.core.identity.me.instance_name
        network_view = network_view or NetworkView(network_name, identity_name=identity_name)
        network, wg = network_view.add_access(node_id, use_ipv4, pool_id)
        result = {"ids": [], "wg": wg}
        node_workloads = {}
        # deploy only latest resource generated by zos sal for each node
        owner = None
        node_metadata = defaultdict(dict)  # node_id: metadata dict
        for workload in network.network_resources:
            node_workloads[workload.info.node_id] = workload
            decrypted_metadata = self.decrypt_metadata(workload.info.metadata, identity_name)
            metadata_dict = j.data.serializers.json.loads(decrypted_metadata)
            node_metadata[workload.info.node_id].update(metadata_dict)
            if not owner and metadata_dict.get("owner"):
                owner = metadata_dict["owner"]

        if owner and "owner" not in metadata:
            metadata["owner"] = owner

        dry_run_name = uuid.uuid4().hex
        with NetworkView.dry_run_context(dry_run_name, identity_name):
            network_view.dry_run(
                dry_run_name,
                list(node_workloads.keys()),
                [w.info.pool_id for w in node_workloads.values()],
                bot,
                breaking_node_ids=[node_id],
            )

        parent_id = network_view.network_workloads[-1].id
        for resource in node_workloads.values():
            resource.info.reference = ""
            resource.info.description = (
                description if description else j.data.serializers.json.dumps({"parent_id": parent_id})
            )
            metadata["parent_network"] = parent_id
            old_metadata = node_metadata.get(resource.info.node_id, {})
            old_metadata.pop("parent_network", None)
            metadata.update(old_metadata)
            resource.info.metadata = self.encrypt_metadata(metadata, identity_name)
            result["ids"].append(j.sals.zos.get(identity_name).workloads.deploy(resource))
            parent_id = result["ids"][-1]
        result["rid"] = result["ids"][0]
        return result

    def delete_access(
        self,
        network_name,
        iprange,
        network_view=None,
        node_id=None,
        bot=None,
        identity_name=None,
        description="",
        **metadata,
    ):
        network_view = network_view or NetworkView(network_name)
        network = network_view.delete_access(iprange, node_id)

        node_workloads = {}
        # deploy only latest resource generated by zos sal for each node
        owner = None
        node_metadata = defaultdict(dict)
        for workload in network.network_resources:
            node_workloads[workload.info.node_id] = workload
            decrypted_metadata = self.decrypt_metadata(workload.info.metadata, identity_name)
            metadata_dict = j.data.serializers.json.loads(decrypted_metadata)
            node_metadata[workload.info.node_id].update(metadata_dict)
            if not owner and metadata_dict.get("owner"):
                owner = metadata_dict["owner"]

        if owner and "owner" not in metadata:
            metadata["owner"] = owner

        dry_run_name = uuid.uuid4().hex
        with NetworkView.dry_run_context(dry_run_name, identity_name):
            network_view.dry_run(
                dry_run_name,
                list(node_workloads.keys()),
                [w.info.pool_id for w in node_workloads.values()],
                bot,
                breaking_node_ids=[node_id],
            )
        parent_id = network_view.network_workloads[-1].id
        result = []
        for resource in node_workloads.values():
            resource.info.reference = ""
            resource.info.description = (
                description if description else j.data.serializers.json.dumps({"parent_id": parent_id})
            )
            metadata["parent_network"] = parent_id
            old_metadata = node_metadata.get(resource.info.node_id, {})
            old_metadata.pop("parent_network", None)
            metadata.update(old_metadata)
            resource.info.metadata = self.encrypt_metadata(metadata, identity_name)
            result.append(j.sals.zos.get().workloads.deploy(resource))
            parent_id = result[-1]
        return result

    def wait_workload(
        self, workload_id, bot=None, expiry=10, breaking_node_id=None, identity_name=None, cancel_by_uuid=True
    ):
        j.logger.info(f"waiting workload {workload_id} to finish deployment")
        expiry = expiry or 10
        expiration_provisioning = j.data.time.now().timestamp + expiry * 60

        workload = j.sals.zos.get(identity_name).workloads.get(workload_id)
        # if the workload is network and it is not a breaking node, skip if the node is blocked
        if (
            workload.info.workload_type == WorkloadType.Network_resource
            and workload.info.node_id in j.sals.reservation_chatflow.reservation_chatflow.list_blocked_nodes()
        ):
            if workload.info.node_id != breaking_node_id:
                return True

        if workload.info.workload_type in GATEWAY_WORKLOAD_TYPES:
            node = j.sals.zos.get(identity_name)._explorer.gateway.get(workload.info.node_id)
        else:
            node = j.sals.zos.get(identity_name)._explorer.nodes.get(workload.info.node_id)
        # check if the node is up
        if not j.sals.zos.get(identity_name).nodes_finder.filter_is_up(node):
            cancel = True
            if breaking_node_id and breaking_node_id == node.node_id:
                # if the node is down and it is the same as breaking_node_id
                if workload.info.workload_type == WorkloadType.Network_resource:
                    # if the workload is a newtork we don't cancel it
                    cancel = False
            # the node is down but it is not a breaking node_id
            elif workload.info.workload_type == WorkloadType.Network_resource:
                # if the workload is network we can overlook it
                return True
            if cancel:
                if cancel_by_uuid:
                    j.sals.reservation_chatflow.solutions.cancel_solution([workload_id], identity_name)
                else:
                    try:
                        j.sals.zos.get(identity_name).workloads.decomission(workload_id)
                    except Exception as e:
                        j.logger.error(f"failed to delete expired workload {workload_id} due to error {str(e)}")
            raise DeploymentFailed(
                f"Workload {workload_id} failed to deploy because the node is down {node.node_id}",
                wid=workload_id,
                identity_name=identity_name,
            )

        # wait for workload
        while True:
            workload = j.sals.zos.get(identity_name).workloads.get(workload_id)
            remaning_time = j.data.time.get(expiration_provisioning).humanize(granularity=["minute", "second"])
            if bot:
                deploying_message = f"""\
                # Deploying...

                <br />Workload ID: {workload_id}


                Deployment should take around 2 to 3 minutes, but might take longer and will be cancelled if it is not successful in 10 mins
                """
                bot.md_show_update(dedent(deploying_message), md=True)
            if workload.info.result.workload_id:
                success = workload.info.result.state.value == 1
                if not success:
                    error_message = workload.info.result.message
                    msg = f"Workload {workload.id} failed to deploy due to error {error_message}. For more details: {j.core.identity.me.explorer_url}/reservations/workloads/{workload.id}"
                    j.logger.error(msg)
                    j.tools.alerthandler.alert_raise(
                        app_name="chatflows", category="internal_errors", message=msg, alert_type="exception"
                    )
                elif workload.info.workload_type != WorkloadType.Network_resource:
                    j.sals.reservation_chatflow.reservation_chatflow.unblock_node(workload.info.node_id)
                return success
            if expiration_provisioning < j.data.time.get().timestamp:
                j.sals.reservation_chatflow.reservation_chatflow.block_node(workload.info.node_id)
                if workload.info.workload_type != WorkloadType.Network_resource:
                    if cancel_by_uuid:
                        j.sals.reservation_chatflow.solutions.cancel_solution([workload_id], identity_name)
                    else:
                        try:
                            j.sals.zos.get(identity_name).workloads.decomission(workload_id)
                        except Exception as e:
                            j.logger.error(f"failed to delete expired workload {workload_id} due to error {str(e)}")
                elif breaking_node_id and workload.info.node_id != breaking_node_id:
                    return True
                raise DeploymentFailed(f"Workload {workload_id} failed to deploy in time")
            gevent.sleep(1)

    def add_network_node(
        self,
        name,
        node,
        pool_id,
        network_view=None,
        bot=None,
        identity_name=None,
        description="",
        subnet="",
        **metadata,
    ):
        identity_name = identity_name or j.core.identity.me.instance_name
        if not network_view:
            network_view = NetworkView(name, identity_name=identity_name)
        network = network_view.add_node(node, pool_id, subnet)
        if not network:
            return
        parent_id = network_view.network_workloads[-1].id
        ids = []
        node_workloads = {}
        # deploy only latest resource generated by zos sal for each node
        owner = None
        node_metadata = defaultdict(dict)
        for workload in network.network_resources:
            node_workloads[workload.info.node_id] = workload
            decrypted_metadata = self.decrypt_metadata(workload.info.metadata, identity_name)
            metadata_dict = j.data.serializers.json.loads(decrypted_metadata)
            node_metadata[workload.info.node_id].update(metadata_dict)
            if not owner and metadata_dict.get("owner"):
                owner = metadata_dict["owner"]

        if owner and "owner" not in metadata:
            metadata["owner"] = owner

        dry_run_name = uuid.uuid4().hex
        with NetworkView.dry_run_context(dry_run_name, identity_name):
            network_view.dry_run(
                dry_run_name,
                list(node_workloads.keys()),
                [w.info.pool_id for w in node_workloads.values()],
                bot,
                breaking_node_ids=[node.node_id],
            )
        for workload in node_workloads.values():
            workload.info.reference = ""
            workload.info.description = (
                description if description else j.data.serializers.json.dumps({"parent_id": parent_id})
            )
            metadata["parent_network"] = parent_id
            old_metadata = node_metadata.get(workload.info.node_id, {})
            old_metadata.pop("parent_network", None)
            metadata.update(old_metadata)
            workload.info.metadata = self.encrypt_metadata(metadata, identity_name)
            ids.append(j.sals.zos.get(identity_name).workloads.deploy(workload))
            parent_id = ids[-1]
        return {"ids": ids, "rid": ids[0]}

    def add_multiple_network_nodes(
        self, name, node_ids, pool_ids, network_view=None, bot=None, identity_name=None, description="", **metadata
    ):
        if not network_view:
            network_view = NetworkView(name, identity_name=identity_name)
        network = network_view.add_multiple_nodes(node_ids, pool_ids)
        if not network:
            return

        parent_id = network_view.network_workloads[-1].id
        ids = []
        node_workloads = {}
        # deploy only latest resource generated by zos sal for each node
        for workload in network.network_resources:
            node_workloads[workload.info.node_id] = workload
        dry_run_name = uuid.uuid4().hex
        with NetworkView.dry_run_context(dry_run_name, identity_name):
            network_view.dry_run(
                dry_run_name,
                list(node_workloads.keys()),
                [w.info.pool_id for w in node_workloads.values()],
                bot,
                breaking_node_ids=node_ids,
            )
        for workload in node_workloads.values():
            workload.info.reference = ""
            workload.info.description = (
                description if description else j.data.serializers.json.dumps({"parent_id": parent_id})
            )
            metadata["parent_network"] = parent_id
            workload.info.metadata = self.encrypt_metadata(metadata, identity_name)
            ids.append(j.sals.zos.get(identity_name).workloads.deploy(workload))
            parent_id = ids[-1]
        return {"ids": ids, "rid": ids[0]}

    def select_network(self, bot, network_views=None):
        network_views = network_views or self.list_networks()
        if not network_views:
            raise StopChatFlow(f"You don't have any deployed network.")
        network_name = bot.single_choice(
            "Please select a network to connect your solution to", list(network_views.keys()), required=True
        )
        return network_views[network_name]

    def deploy_volume(
        self, pool_id, node_id, size, volume_type=DiskType.SSD, identity_name=None, description="", **metadata
    ):
        volume = j.sals.zos.get(identity_name).volume.create(node_id, pool_id, size, volume_type)
        if metadata:
            volume.info.metadata = self.encrypt_metadata(metadata, identity_name)
            volume.info.description = description
        return j.sals.zos.get(identity_name).workloads.deploy(volume)

    def deploy_container(
        self,
        pool_id,
        node_id,
        network_name,
        ip_address,
        flist,
        env=None,
        cpu=1,
        memory=1024,
        disk_size=256,
        disk_type=DiskType.SSD,
        entrypoint="",
        interactive=False,
        secret_env=None,
        volumes=None,
        log_config=None,
        public_ipv6=False,
        identity_name=None,
        description="",
        **metadata,
    ):
        """
        volumes: dict {"mountpoint (/)": volume_id}
        log_Config: dict. keys ("channel_type", "channel_host", "channel_port", "channel_name")
        """
        identity_name = identity_name or j.core.identity.me.instance_name
        env = env or {}
        encrypted_secret_env = {}
        if secret_env:
            for key, val in secret_env.items():
                val = val or ""
                encrypted_secret_env[key] = j.sals.zos.get(identity_name).container.encrypt_secret(node_id, val)
        for key, val in env.items():
            env[key] = val or ""
        container = j.sals.zos.get(identity_name).container.create(
            node_id,
            network_name,
            ip_address,
            flist,
            pool_id,
            env,
            cpu,
            memory,
            disk_size,
            entrypoint,
            interactive,
            encrypted_secret_env,
            public_ipv6=public_ipv6,
        )
        if volumes:
            for mount_point, vol_id in volumes.items():
                j.sals.zos.get(identity_name).volume.attach_existing(container, f"{vol_id}-1", mount_point)
        if metadata:
            container.info.metadata = self.encrypt_metadata(metadata, identity_name=identity_name)
            container.info.description = description
        if log_config:
            j.sals.zos.get(identity_name).container.add_logs(container, **log_config)
        return j.sals.zos.get(identity_name).workloads.deploy(container)

    def ask_container_resources(
        self,
        bot,
        cpu=True,
        memory=True,
        disk_size=True,
        disk_type=False,
        default_cpu=1,
        default_memory=1024,
        default_disk_size=256,
        default_disk_type="SSD",
    ):
        form = bot.new_form()
        if cpu:
            cpu_answer = form.int_ask("Please specify how many CPUs", default=default_cpu, required=True, min=1)
        if memory:
            memory_answer = form.int_ask(
                "Please specify how much memory (in MB)", default=default_memory, required=True, min=1024
            )
        if disk_size:
            disk_size_answer = form.int_ask(
                "Please specify the size of root filesystem (in MB)", default=default_disk_size, required=True
            )
        if disk_type:
            disk_type_answer = form.single_choice(
                "Please choose the root filesystem disktype", ["SSD", "HDD"], default=default_disk_type, required=True
            )
        form.ask()
        resources = {}
        if cpu:
            resources["cpu"] = cpu_answer.value
        if memory:
            resources["memory"] = memory_answer.value
        if disk_size:
            resources["disk_size"] = disk_size_answer.value
        if disk_type:
            resources["disk_type"] = DiskType[disk_type_answer.value]
        return resources

    def ask_container_logs(self, bot, solution_name=None):
        logs_config = {}
        form = bot.new_form()
        channel_type = form.string_ask("Please add the channel type", default="redis", required=True)
        channel_host = form.string_ask("Please add the IP address where the logs will be output to", required=True)
        channel_port = form.int_ask("Please add the port available where the logs will be output to", required=True)
        channel_name = form.string_ask(
            "Please add the channel name to be used. The channels will be in the form" " NAME-stdout and NAME-stderr",
            default=solution_name,
            required=True,
        )
        form.ask()
        logs_config["channel_type"] = channel_type.value
        logs_config["channel_host"] = channel_host.value
        logs_config["channel_port"] = channel_port.value
        logs_config["channel_name"] = channel_name.value
        return logs_config

    def schedule_container(self, pool_id, cru=None, sru=None, mru=None, hru=None, ip_version=None):
        query = {"cru": cru, "sru": sru, "mru": mru, "hru": hru, "ip_version": ip_version}
        return j.sals.reservation_chatflow.reservation_chatflow.get_nodes(1, pool_ids=[pool_id], **query)[0]

    def ask_container_placement(
        self,
        bot,
        pool_id,
        cru=None,
        sru=None,
        mru=None,
        hru=None,
        ip_version=None,
        free_to_use=False,
        workload_name=None,
    ):
        if not workload_name:
            workload_name = "your workload"
        automatic_choice = bot.single_choice(
            f"Do you want to automatically select a node to deploy {workload_name} on?",
            ["YES", "NO"],
            default="YES",
            required=True,
        )
        if automatic_choice == "YES":
            return None
        if j.config.get("OVER_PROVISIONING"):
            cru = 0
            mru = 0
        nodes = j.sals.zos.get().nodes_finder.nodes_by_capacity(pool_id=pool_id, cru=cru, sru=sru, mru=mru, hru=hru)
        nodes = list(nodes)
        nodes = j.sals.reservation_chatflow.reservation_chatflow.filter_nodes(nodes, free_to_use, ip_version)
        blocked_nodes = j.sals.reservation_chatflow.reservation_chatflow.list_blocked_nodes()
        node_messages = {node.node_id: node for node in nodes if node.node_id not in blocked_nodes}
        if not node_messages:
            raise StopChatFlow("Failed to find resources for this reservation")
        node_id = bot.drop_down_choice(
            f"Please choose the node you want to deploy {workload_name} on", list(node_messages.keys()), required=True
        )
        return node_messages[node_id]

    def calculate_capacity_units(self, cru=0, mru=0, sru=0, hru=0, ipv4u=0):
        """
        return:
        CloudUnits(object): contains all the needed resources cu, su and ipv4
        """

        return ResourceUnitAmount(cru=cru, mru=mru, sru=sru, hru=hru, ipv4u=ipv4u).cloud_units()

    def get_network_view(self, network_name, workloads=None, identity_name=None):
        nv = NetworkView(network_name, workloads, identity_name=identity_name)
        if not nv.network_workloads:
            return
        return nv

    def delegate_domain(self, pool_id, gateway_id, domain_name, identity_name=None, description="", **metadata):
        domain_delegate = j.sals.zos.get(identity_name).gateway.delegate_domain(gateway_id, domain_name, pool_id)
        if metadata:
            domain_delegate.info.metadata = self.encrypt_metadata(metadata, identity_name)
        domain_delegate.info.description = description
        return j.sals.zos.get(identity_name).workloads.deploy(domain_delegate)

    def deploy_public_ip(self, pool_id, node_id, ip_address, identity_name=None, description="", **metadata):
        zos = j.sals.zos.get(identity_name)
        public_ip = zos.public_ip.create(node_id, pool_id, ip_address)
        if metadata:
            public_ip.info.metadata = self.encrypt_metadata(metadata, identity_name)
        public_ip.info.description = description
        return zos.workloads.deploy(public_ip)

    def deploy_vmachine(
        self, node_id, network_name, name, ip_address, ssh_keys, pool_id, size=1, enable_public_ip=False, **metadata
    ):
        identity_name = metadata.get("owner", j.core.identity.me.instance_name)
        public_ip_wid = 0
        public_ip = ""
        if enable_public_ip:
            # Reserve public_Ip on node_id[0]
            if enable_public_ip:
                public_ip_wid, public_ip = self.create_public_ip(
                    pool_id, node_id, solution_uuid=metadata.get("solution_uuid")
                )
                if not public_ip_wid or not public_ip:
                    raise DeploymentFailed(f"Can not get public ip for your solutions")
                public_ip = public_ip.split("/")[0] if public_ip else ""
        vmachine = j.sals.zos.get(identity_name).vm.create(
            node_id, network_name, name, ip_address, ssh_keys, pool_id, size, public_ip_wid
        )
        return j.sals.zos.get(identity_name).workloads.deploy(vmachine), public_ip

    def deploy_kubernetes_master(
        self,
        pool_id,
        node_id,
        network_name,
        cluster_secret,
        ssh_keys,
        ip_address,
        size=1,
        identity_name=None,
        description="",
        public_ip_wid=0,
        datastore_endpoint="",
        disable_default_ingress=False,
        **metadata,
    ):
        master = j.sals.zos.get(identity_name).kubernetes.add_master(
            node_id,
            network_name,
            cluster_secret,
            ip_address,
            size,
            ssh_keys,
            pool_id,
            public_ip_wid,
            disable_default_ingress,
            datastore_endpoint,
        )
        desc = {"role": "master"}
        if metadata:
            master.info.metadata = self.encrypt_metadata(metadata, identity_name)
        master.info.description = description if description else j.data.serializers.json.dumps(desc)
        return j.sals.zos.get(identity_name).workloads.deploy(master)

    def deploy_kubernetes_worker(
        self,
        pool_id,
        node_id,
        network_name,
        cluster_secret,
        ssh_keys,
        ip_address,
        master_ip,
        size=1,
        identity_name=None,
        description="",
        public_ip_wid=0,
        **metadata,
    ):
        worker = j.sals.zos.get(identity_name).kubernetes.add_worker(
            node_id, network_name, cluster_secret, ip_address, size, master_ip, ssh_keys, pool_id, public_ip_wid
        )
        desc = {"role": "worker"}
        if metadata:
            worker.info.metadata = self.encrypt_metadata(metadata, identity_name)
        worker.info.description = description if description else j.data.serializers.json.dumps(desc)
        return j.sals.zos.get(identity_name).workloads.deploy(worker)

    def fetch_available_ips(self, farm):
        addresses = [address for address in farm.ipaddresses if not address.reservation_id]
        random.shuffle(addresses)
        return addresses

    def create_public_ip(self, pool_id, node_id, solution_uuid=None):
        """
        try to reserve a public ip on network farm and returns the wid
        """
        solution_uuid = solution_uuid or uuid.uuid4().hex
        zos = j.sals.zos.get()
        node = zos._explorer.nodes.get(node_id)
        farm = zos._explorer.farms.get(node.farm_id)
        identity = j.core.identity.me.instance_name
        for farmer_address in self.fetch_available_ips(farm):
            address = farmer_address.address
            wid = deployer.deploy_public_ip(
                pool_id, node_id, address, identity_name=identity, solution_uuid=solution_uuid
            )
            try:
                success = deployer.wait_workload(wid, bot=None, expiry=5, cancel_by_uuid=False, identity_name=identity)
                if not success:
                    raise DeploymentFailed(f"public ip workload failed. wid: {wid}")
                return wid, address
            except DeploymentFailed as e:
                raise StopChatFlow(f"failed to reserve public ip {address} on node {node_id} due to error {str(e)}")
                continue
        raise StopChatFlow(
            f"all tries to reserve a public ip failed on farm: {farm.name} pool: {pool_id} node: {node_id}"
        )

    def deploy_kubernetes_cluster(
        self,
        pool_id,
        node_ids,
        network_name,
        cluster_secret,
        ssh_keys,
        size=1,
        ip_addresses=None,
        slave_pool_ids=None,
        description="",
        public_ip=False,
        **metadata,
    ):
        """
        deploy k8s cluster with the same number of nodes as specified in node_ids

        Args:
            pool_id: this one is always used for master.
            node_ids: list() of node ids to deploy on. first node_id is used for master reservation
            ip_addresses: if specified it will be mapped 1-1 with node_ids for workloads. if not specified it will choose any free_ip from the node
            slave_pool_ids: if specified, k8s workers will deployed on each of these pools respectively. if empty it will use the master pool_id

        Return:
            list: [{"node_id": "ip_address"}, ...] first dict is master's result
        """
        slave_pool_ids = slave_pool_ids or ([pool_id] * (len(node_ids) - 1))
        pool_ids = [pool_id] + slave_pool_ids
        result = []  # [{"node_id": id,  "ip_address": ip, "reservation_id": 16}] first dict is master's result
        if ip_addresses and len(ip_addresses) != len(node_ids):
            raise StopChatFlow("length of ips != node_ids")

        if not ip_addresses:
            # get free_ips for the nodes
            ip_addresses = []
            for i in range(len(node_ids)):
                node_id = node_ids[i]
                pool_id = pool_ids[i]
                node = self._explorer.nodes.get(node_id)
                res = self.add_network_node(network_name, node, pool_id)
                if res:
                    for wid in res["ids"]:
                        success = self.wait_workload(wid, breaking_node_id=node.node_id)
                        if not success:
                            raise StopChatFlow(f"Failed to add node {node.node_id} to network {wid}")
                network_view = NetworkView(network_name)
                address = network_view.get_free_ip(node)
                if not address:
                    raise StopChatFlow(f"No free IPs for network {network_name} on the specifed node" f" {node_id}")
                ip_addresses.append(address)

        # deploy_master
        master_ip = ip_addresses[0]
        # Reserve public_Ip on node_id[0]
        public_id_wid = 0
        master_public_ip = ""
        if public_ip:
            public_id_wid, master_public_ip = self.create_public_ip(
                pool_id, node_ids[0], solution_uuid=metadata.get("solution_uuid")
            )
            master_public_ip = master_public_ip.split("/")[0] if master_public_ip else ""

        master_resv_id = self.deploy_kubernetes_master(
            pool_ids[0],
            node_ids[0],
            network_name,
            cluster_secret,
            ssh_keys,
            master_ip,
            size,
            decription=description,
            public_ip_wid=public_id_wid,
            **metadata,
        )

        result.append(
            {
                "node_id": node_ids[0],
                "ip_address": master_ip,
                "reservation_id": master_resv_id,
                "public_ip": master_public_ip,
            }
        )
        for i in range(1, len(node_ids)):
            node_id = node_ids[i]
            pool_id = pool_ids[i]
            ip_address = ip_addresses[i]
            resv_id = self.deploy_kubernetes_worker(
                pool_id,
                node_id,
                network_name,
                cluster_secret,
                ssh_keys,
                ip_address,
                master_ip,
                size,
                decription=description,
                **metadata,
            )
            result.append({"node_id": node_id, "ip_address": ip_address, "reservation_id": resv_id})
        return result

    def ask_multi_pool_placement(
        self, bot, number_of_nodes, resource_query_list=None, pool_ids=None, workload_names=None, ip_version=None
    ):
        """
        Ask and schedule workloads accross multiple pools

        Args:
            bot: chatflow object
            number_of_nodes: number of required nodes for deployment
            resource_query_list: list of query dicts {"cru": 1, "sru": 2, "mru": 1, "hru": 1}. if specified it must be same length as number_of_nodes
            pool_ids: if specfied it will limit the pools shown in the chatflow to only these pools
            workload_names: if specified they will shown when asking the user for node selection for each workload. if specified it must be same length as number_of_nodes

        Returns:
            ([], []): first list contains the selected node objects. second list contains selected pool ids
        """
        resource_query_list = resource_query_list or [dict()] * number_of_nodes
        workload_names = workload_names or [None] * number_of_nodes
        if len(resource_query_list) != number_of_nodes:
            raise StopChatFlow("resource query_list must be same length as number of nodes")
        if len(workload_names) != number_of_nodes:
            raise StopChatFlow("workload_names must be same length as number of nodes")

        pools = self.list_pools()
        if pool_ids:
            filtered_pools = {}
            for pool_id in pools:
                if pool_id in pool_ids:
                    filtered_pools[pool_id] = pools[pool_id]
            pools = filtered_pools
        selected_nodes = []
        selected_pool_ids = []
        for i in range(number_of_nodes):
            cloud_units = self.calculate_capacity_units(**resource_query_list[i])
            cu, su = cloud_units.cu, cloud_units.su
            pool_choices = {}
            for p in pools:
                if pools[p][0] < cu or pools[p][1] < su:
                    continue
                nodes = j.sals.zos.get().nodes_finder.nodes_by_capacity(pool_id=p, **resource_query_list[i])
                if not nodes:
                    continue
                pool_choices[p] = pools[p]
            bot.md_show_update(f"## Setup pool and container node for node {i+1}", md=True)
            gevent.sleep(2)
            pool_id = self.select_pool(bot, available_pools=pool_choices, workload_name=workload_names[i], cu=cu, su=su)
            node = self.ask_container_placement(
                bot, pool_id, workload_name=workload_names[i], ip_version=ip_version, **resource_query_list[i]
            )
            if not node:
                node = self.schedule_container(pool_id, ip_version=ip_version, **resource_query_list[i])
            selected_nodes.append(node)
            selected_pool_ids.append(pool_id)
        return selected_nodes, selected_pool_ids

    def list_pool_gateways(self, pool_id, identity_name=None):
        """
        return dict of gateways where keys are descriptive string of each gateway
        """
        zos = j.sals.zos.get(identity_name)
        pool = zos.pools.get(pool_id)
        farm_id = self.get_pool_farm_id(pool_id, identity_name=identity_name)
        if farm_id < 0:
            raise StopChatFlow(f"no available gateways in pool {pool_id} farm: {farm_id}")
        gateways = zos._explorer.gateway.list(farm_id=farm_id)
        if not gateways:
            raise StopChatFlow(f"no available gateways in pool {pool_id} farm: {farm_id}")
        result = {}
        for g in gateways:
            if not g.dns_nameserver:
                continue
            if g.node_id not in pool.node_ids:
                continue
            result[f"{g.dns_nameserver[0]} {g.location.continent} {g.location.country}" f" {g.node_id}"] = g
        return result

    def list_all_gateways(self, pool_ids=None, identity_name=None):
        """
        Args:
            pool_ids: if specified it will only list gateways inside these pools

        Returns:
            dict: {"gateway_message": {"gateway": g, "pool": pool},}
        """
        identity_name = identity_name or j.core.identity.me.instance_name
        all_gateways = filter(j.sals.zos.get(identity_name).nodes_finder.filter_is_up, self._explorer.gateway.list())
        if not all_gateways:
            raise StopChatFlow(f"no available gateways")
        all_pools = [p for p in j.sals.zos.get(identity_name).pools.list() if p.node_ids]
        available_node_ids = {}  # node_id: pool
        if pool_ids is not None:
            for pool in all_pools:
                if pool.pool_id in pool_ids:
                    available_node_ids.update({node_id: pool for node_id in pool.node_ids})
        else:
            for pool in all_pools:
                available_node_ids.update({node_id: pool for node_id in pool.node_ids})
        result = {}
        for gateway in all_gateways:
            if gateway.node_id in available_node_ids:
                if not gateway.dns_nameserver:
                    continue
                pool = available_node_ids[gateway.node_id]
                hidden = False
                name = ""
                if f"pool_{pool.pool_id}" in pool_factory.list_all():
                    local_config = pool_factory.get(f"pool_{pool.pool_id}")
                    hidden = local_config.hidden
                    name = local_config.name
                if hidden:
                    continue
                if name:
                    message = (
                        f"Pool: {pool.pool_id} Name: {name} {gateway.dns_nameserver[0]}"
                        f" {gateway.location.continent} {gateway.location.country}"
                        f" {gateway.node_id}"
                    )
                else:
                    message = (
                        f"Pool: {pool.pool_id} {gateway.dns_nameserver[0]}"
                        f" {gateway.location.continent} {gateway.location.country}"
                        f" {gateway.node_id}"
                    )
                result[message] = {"gateway": gateway, "pool": pool}
        if not result:
            raise StopChatFlow(f"no gateways available in your pools")
        return result

    def select_gateway(self, bot, pool_ids=None, identity_name=None):
        """
        Args:
            pool_ids: if specified it will only list gateways inside these pools

        Returns:
            gateway, pool_objects
        """
        gateways = self.list_all_gateways(pool_ids, identity_name)

        selected = bot.single_choice("Please select a gateway", list(gateways.keys()), required=True)
        return gateways[selected]["gateway"], gateways[selected]["pool"]

    def create_ipv6_gateway(self, gateway_id, pool_id, public_key, identity_name=None, description="", **metadata):
        if isinstance(public_key, bytes):
            public_key = public_key.decode()
        workload = j.sals.zos.get(identity_name).gateway.gateway_4to6(gateway_id, public_key, pool_id)
        if metadata:
            workload.info.metadata = self.encrypt_metadata(metadata, identity_name)
            workload.info.description = description
        return j.sals.zos.get(identity_name).workloads.deploy(workload)

    def deploy_zdb(
        self,
        pool_id,
        node_id,
        size,
        mode,
        password,
        disk_type="SSD",
        public=False,
        identity_name=None,
        description="",
        **metadata,
    ):
        metadata["password"] = password
        workload = j.sals.zos.get(identity_name).zdb.create(node_id, size, mode, password, pool_id, disk_type, public)
        if metadata:
            workload.info.metadata = self.encrypt_metadata(metadata, identity_name)
            workload.info.description = description
        return j.sals.zos.get(identity_name).workloads.deploy(workload)

    def create_subdomain(
        self, pool_id, gateway_id, subdomain, addresses=None, identity_name=None, description="", **metadata
    ):
        """
        creates an A record pointing to the specified addresses
        if no addresses are specified, the record will point the gateway IP address (used for exposing solutions)
        """
        identity_name = identity_name or j.core.identity.me.instance_name
        if not addresses:
            gateway = self._explorer.gateway.get(gateway_id)
            addresses = [j.sals.nettools.get_host_by_name(ns) for ns in gateway.dns_nameserver]
        workload = j.sals.zos.get(identity_name).gateway.sub_domain(gateway_id, subdomain, addresses, pool_id)
        if metadata:
            workload.info.metadata = self.encrypt_metadata(metadata, identity_name)
            workload.info.description = description
        return j.sals.zos.get(identity_name).workloads.deploy(workload)

    def create_proxy(
        self, pool_id, gateway_id, domain_name, trc_secret, identity_name=None, description="", **metadata
    ):
        """
        creates a reverse tunnel on the gateway node
        """
        identity_name = identity_name or j.core.identity.me.instance_name
        workload = j.sals.zos.get(identity_name).gateway.tcp_proxy_reverse(gateway_id, domain_name, trc_secret, pool_id)
        if metadata:
            workload.info.metadata = self.encrypt_metadata(metadata, identity_name)
            workload.info.description = description
        return j.sals.zos.get(identity_name).workloads.deploy(workload)

    def expose_and_create_certificate(
        self,
        pool_id,
        gateway_id,
        network_name,
        trc_secret,
        domain,
        email,
        solution_ip,
        solution_port,
        enforce_https=False,
        node_id=None,
        proxy_pool_id=None,
        log_config=None,
        bot=None,
        public_key="",
        identity_name=None,
        description="",
        **metadata,
    ):
        """
        exposes the solution and enable ssl for it's domain
        Args:
            pool_id: the pool used to create your solution
            gateway_id: Gateway id
            network_name: Name of the network selected while creating the solution
            trc_secret: Secret for tcp router
            domain: the domain we will issue certificate for
            email: used to issue certificate
            solution_ip: where your server is hosted (the actual server)
            solution_port: the port your application is listening on
            enforce_https: whether you want to only use https or not
            node_id: your node id
            solution_uuid: solution id
            public_key: your public key in case you want to have ssh access on the nginx container

        """
        zos = j.sals.zos.get(identity_name)
        test_cert = j.config.get("TEST_CERT")
        proxy_pool_id = proxy_pool_id or pool_id
        gateway = zos._explorer.gateway.get(gateway_id)

        proxy_id = self.create_proxy(
            pool_id=proxy_pool_id,
            gateway_id=gateway_id,
            domain_name=domain,
            trc_secret=trc_secret,
            identity_name=identity_name,
            description=description,
            **metadata,
        )
        success = self.wait_workload(proxy_id, identity_name=identity_name)
        if not success:
            raise DeploymentFailed(
                f"failed to create reverse proxy on gateway {gateway_id} workload {proxy_id}",
                wid=proxy_id,
                solution_uuid=metadata.get("solution_uuid"),
                identity_name=identity_name,
            )

        tf_gateway = f"{gateway.dns_nameserver[0]}:{gateway.tcp_router_port}"
        secret_env = {
            "TRC_SECRET": trc_secret,
            "TFGATEWAY": tf_gateway,
            "EMAIL": email,
            "SOLUTION_IP": solution_ip,
            "SOLUTION_PORT": str(solution_port),
            "ENFORCE_HTTPS": "true" if enforce_https else "false",
            "PUBKEY": public_key,
            "TEST_CERT": "true" if test_cert else "false",
        }
        if not node_id:
            node = self.schedule_container(pool_id=pool_id, cru=1, mru=1, hru=1)
            node_id = node.node_id
        else:
            node = zos._explorer.nodes.get(node_id)

        res = self.add_network_node(network_name, node, pool_id, identity_name=identity_name, bot=bot)
        if res:
            for wid in res["ids"]:
                success = self.wait_workload(
                    wid, bot, expiry=3, identity_name=identity_name, breaking_node_id=node.node_id
                )
                if not success:
                    raise DeploymentFailed(
                        f"failed to add node {node.node_id} to network workload {wid}",
                        wid=wid,
                        solution_uuid=metadata.get("solution_uuid"),
                        identity_name=identity_name,
                    )
        network_view = self.get_network_view(network_name, identity_name=identity_name)
        ip_address = network_view.get_free_ip(node)
        resv_id = self.deploy_container(
            pool_id=pool_id,
            node_id=node_id,
            network_name=network_name,
            ip_address=ip_address,
            flist="https://hub.grid.tf/omar0.3bot/omarelawady-nginx-certbot-zinit.flist",
            disk_type=DiskType.HDD,
            disk_size=512,
            secret_env=secret_env,
            env={"DOMAIN": domain},
            public_ipv6=False,
            log_config=log_config,
            identity_name=identity_name,
            description=description,
            **metadata,
        )
        return resv_id, proxy_id

    def expose_address(
        self,
        pool_id,
        gateway_id,
        network_name,
        local_ip,
        port,
        tls_port,
        trc_secret,
        node_id=None,
        reserve_proxy=False,
        proxy_pool_id=None,
        domain_name=None,
        bot=None,
        log_config=None,
        identity_name=None,
        description="",
        **metadata,
    ):
        identity_name = identity_name or j.core.identity.me.instance_name
        zos = j.sals.zos.get(identity_name)
        proxy_pool_id = proxy_pool_id or pool_id
        gateway = zos._explorer.gateway.get(gateway_id)

        reverse_id = None
        if reserve_proxy:
            if not domain_name:
                raise StopChatFlow("you must pass domain_name when you ise reserv_proxy")
            resv_id = self.create_proxy(
                pool_id=proxy_pool_id,
                gateway_id=gateway_id,
                domain_name=domain_name,
                trc_secret=trc_secret,
                identity_name=identity_name,
                description=description,
                **metadata,
            )
            reverse_id = resv_id
            success = self.wait_workload(resv_id, identity_name=identity_name)
            if not success:
                raise DeploymentFailed(
                    f"failed to create reverse proxy on gateway {gateway_id} to network workload {resv_id}",
                    wid=resv_id,
                    solution_uuid=metadata.get("solution_uuid"),
                    identity_name=identity_name,
                )

        remote = f"{gateway.dns_nameserver[0]}:{gateway.tcp_router_port}"
        secret_env = {"TRC_SECRET": trc_secret}
        if not node_id:
            node = self.schedule_container(pool_id=pool_id, cru=1, mru=1, hru=1)
            node_id = node.node_id
        else:
            node = zos._explorer.nodes.get(node_id)

        res = self.add_network_node(network_name, node, pool_id, identity_name=identity_name, bot=bot)
        if res:
            for wid in res["ids"]:
                success = self.wait_workload(wid, bot, breaking_node_id=node.node_id, identity_name=identity_name)
                if not success:
                    if reserve_proxy:
                        j.sals.reservation_chatflow.solutions.cancel([resv_id], identity_name=identity_name)
                    raise DeploymentFailed(
                        f"Failed to add node {node.node_id} to network {wid}",
                        wid=wid,
                        solution_uuid=metadata.get("solution_uuid"),
                        identity_name=identity_name,
                    )
        network_view = NetworkView(network_name, identity_name=identity_name)
        network_view = network_view.copy()
        network_view.used_ips.append(local_ip)
        ip_address = network_view.get_free_ip(node)
        env = {
            "SOLUTION_IP": local_ip,
            "HTTP_PORT": str(port),
            "HTTPS_PORT": str(tls_port),
            "REMOTE_IP": gateway.dns_nameserver[0],
            "REMOTE_PORT": str(gateway.tcp_router_port),
        }
        resv_id = self.deploy_container(
            pool_id=pool_id,
            node_id=node_id,
            network_name=network_name,
            ip_address=ip_address,
            flist="https://hub.grid.tf/omar0.3bot/omarelawady-trc-zinit.flist",
            disk_type=DiskType.HDD,
            secret_env=secret_env,
            env=env,
            public_ipv6=False,
            log_config=log_config,
            identity_name=identity_name,
            description=description,
            **metadata,
        )
        return resv_id, reverse_id

    def deploy_minio_zdb(
        self,
        pool_id,
        password,
        node_ids=None,
        zdb_no=None,
        disk_type=DiskType.HDD,
        disk_size=10,
        pool_ids=None,
        identity_name=None,
        description="",
        **metadata,
    ):
        """
        deploy zdb workloads on the specified node_ids if specified or deploy workloads as specifdied by the zdb_no
        Args:
            pool_id: used to deploy all workloads in this pool (overriden when pool_ids is specified)
            node_ids: if specified, it will be used for deployment of workloads.
            pool_ids: if specified, zdb workloads will be
            zdb_no: if specified and no node_ids, it will automatically schedule zdb workloads matching pool config

        Returns:
            []: list of workload ids deployed
        """
        node_ids = node_ids or []
        if not (zdb_no or node_ids):
            raise StopChatFlow("you must pass at least one of zdb_no or node_ids")

        if node_ids:
            pool_ids = pool_ids or [pool_id] * len(node_ids)
        else:
            pool_ids = pool_ids or [pool_id] * zdb_no

        if not node_ids and zdb_no:
            query = {}
            if disk_type == DiskType.SSD:
                query["sru"] = disk_size
            else:
                query["hru"] = disk_size
            for pool_id in pool_ids:
                node = j.sals.reservation_chatflow.reservation_chatflow.get_nodes(
                    pool_ids=[pool_id], number_of_nodes=1, **query
                )[0]
                node_ids.append(node.node_id)

        result = []
        for i in range(len(node_ids)):
            node_id = node_ids[i]
            pool_id = pool_ids[i]
            resv_id = self.deploy_zdb(
                pool_id=pool_id,
                node_id=node_id,
                size=disk_size,
                mode=ZDBMode.Seq,
                password=password,
                disk_type=disk_type,
                identity_name=identity_name,
                description=description,
                **metadata,
            )
            result.append(resv_id)
        return result

    def deploy_minio_containers(
        self,
        pool_id,
        network_name,
        minio_nodes,
        minio_ip_addresses,
        zdb_configs,
        ak,
        sk,
        ssh_key,
        cpu,
        memory,
        data,
        parity,
        disk_type=DiskType.SSD,
        disk_size=10,
        log_config=None,
        mode="Single",
        bot=None,
        public_ipv6=False,
        secondary_pool_id=None,
        identity_name=None,
        description="",
        **metadata,
    ):
        secondary_pool_id = secondary_pool_id or pool_id
        secret_env = {}
        if mode == "Master/Slave":
            secret_env["TLOG"] = zdb_configs.pop(-1)
        shards = ",".join(zdb_configs)
        secret_env["SHARDS"] = shards
        secret_env["SECRET_KEY"] = sk
        secret_env["ACCESS_KEY"] = ak
        env = {"DATA": str(data), "PARITY": str(parity), "SSH_KEY": ssh_key, "MINIO_PROMETHEUS_AUTH_TYPE": "public"}
        result = []
        master_volume_id = self.deploy_volume(
            pool_id,
            minio_nodes[0],
            disk_size,
            disk_type,
            identity_name=identity_name,
            description=description,
            **metadata,
        )
        success = self.wait_workload(master_volume_id, bot, identity_name=identity_name)
        if not success:
            raise DeploymentFailed(
                f"Failed to create volume {master_volume_id} for minio container on" f" node {minio_nodes[0]}",
                wid=master_volume_id,
                solution_uuid=metadata.get("solution_uuid"),
                identity_name=identity_name,
            )
        master_cont_id = self.deploy_container(
            pool_id=pool_id,
            node_id=minio_nodes[0],
            network_name=network_name,
            ip_address=minio_ip_addresses[0],
            env=env,
            cpu=cpu,
            memory=memory,
            secret_env=secret_env,
            log_config=log_config,
            volumes={"/data": master_volume_id},
            public_ipv6=public_ipv6,
            flist="https://hub.grid.tf/tf-official-apps/minio:latest.flist",
            identity_name=identity_name,
            description=description,
            **metadata,
        )
        result.append(master_cont_id)
        if mode == "Master/Slave":
            secret_env["MASTER"] = secret_env.pop("TLOG")
            slave_volume_id = self.deploy_volume(
                pool_id,
                minio_nodes[1],
                disk_size,
                disk_type,
                identity_name=identity_name,
                description=description,
                **metadata,
            )
            success = self.wait_workload(slave_volume_id, bot, identity_name=identity_name)
            if not success:
                raise DeploymentFailed(
                    f"Failed to create volume {slave_volume_id} for minio container on" f" node {minio_nodes[1]}",
                    solution_uuid=metadata.get("solution_uuid"),
                    wid=slave_volume_id,
                    identity_name=identity_name,
                )
            slave_cont_id = self.deploy_container(
                pool_id=secondary_pool_id,
                node_id=minio_nodes[1],
                network_name=network_name,
                ip_address=minio_ip_addresses[1],
                env=env,
                cpu=cpu,
                memory=memory,
                secret_env=secret_env,
                log_config=log_config,
                volumes={"/data": slave_volume_id},
                public_ipv6=public_ipv6,
                flist="https://hub.grid.tf/tf-official-apps/minio:latest.flist",
                identity_name=identity_name,
                description=description,
                **metadata,
            )
            result.append(slave_cont_id)
        return result

    def deploy_etcd_containers(
        self,
        pool_ids,
        node_ids,
        network_name,
        ip_addresses,
        etcd_cluster,
        etcd_flist,
        cpu=1,
        memory=1024,
        disk_size=1024,
        disk_type=DiskType.SSD,
        entrypoint="etcd",
        public_ipv6=False,
        identity_name=None,
        description="",
        secret_env=None,
        log_config=None,
        ssh_key="",
        **metadata,
    ):
        """
        Deploy single and cluster etcd nodes
        Args:
            pool_ids : Pools used to deploy etcd solution
            node_ids : Nodes used to deploy etcd solution
            network_name : Network name used to deploy etcd solution
            ip_addresses (List): List of IP address for every etcd node
            etcd_cluster (str): Contains ETCD_INITIAL_CLUSTER value
            etcd_flist (str): ETCD flist image used
            cpu (int): CPU resource value. Defaults to 1.
            memory (int): Memory resource size in MB. Defaults to 1024.
            disk_size (int): Disk resource size in MB. Defaults to 1024.
            disk_type (DiskType): Disk resource type. Defaults to DiskType.SSD.
            entrypoint (str): Command that run at the start of the container. Defaults to "etcd".
            public_ipv6 (bool): Check for IPv6. Defaults to False.

        Returns:
            List: List of reservation ids
        """
        etcd_cluster = etcd_cluster.rstrip(",")
        solution_uuid = metadata.get("solution_uuid", uuid.uuid4().hex)
        env_cluster = {
            "ETCD_INITIAL_CLUSTER_TOKEN": f"etcd_cluster_{solution_uuid}",
            "ETCD_INITIAL_CLUSTER_STATE": "new",
        }
        result = []
        for n, ip_address in enumerate(ip_addresses):
            env = {}
            if len(ip_addresses) > 1:
                env.update(env_cluster)
            env.update(
                {
                    "ALLOW_NONE_AUTHENTICATION": "yes",
                    "ETCD_NAME": f"etcd_{n+1}",
                    "ETCD_INITIAL_ADVERTISE_PEER_URLS": f"http://{ip_address}:2380",
                    "ETCD_LISTEN_PEER_URLS": "http://0.0.0.0:2380",
                    "ETCD_ADVERTISE_CLIENT_URLS": f"http://{ip_address}:2379",
                    "ETCD_LISTEN_CLIENT_URLS": "http://0.0.0.0:2379",
                    "ETCD_INITIAL_CLUSTER": etcd_cluster,
                    "SSH_KEY": ssh_key,
                }
            )
            result.append(
                self.deploy_container(
                    pool_ids[n],
                    node_ids[n],
                    network_name,
                    ip_address,
                    etcd_flist,
                    env,
                    cpu,
                    memory,
                    disk_size,
                    disk_type,
                    entrypoint=entrypoint,
                    secret_env=secret_env,
                    public_ipv6=public_ipv6,
                    description=description,
                    identity_name=identity_name,
                    log_config=log_config,
                    **metadata,
                )
            )
        return result

    def get_zdb_url(self, zdb_id, password, identity_name=None, workload=None):
        workload = workload or j.sals.zos.get(identity_name).workloads.get(zdb_id)
        result_json = j.data.serializers.json.loads(workload.info.result.data_json)
        if "IPs" in result_json:
            ip = result_json["IPs"][0]
        else:
            ip = result_json["IP"]
        namespace = result_json["Namespace"]
        port = result_json["Port"]
        url = f"{namespace}:{password}@[{ip}]:{port}"
        return url

    def ask_multi_pool_distribution(
        self, bot, number_of_nodes, resource_query=None, pool_ids=None, workload_name=None, ip_version=None
    ):
        """
        Choose multiple pools to distribute workload automatically

        Args:
            bot: chatflow object
            resource_query: query dict {"cru": 1, "sru": 2, "mru": 1, "hru": 1,"ipv4u": 1}.
            pool_ids: if specfied it will limit the pools shown in the chatflow to only these pools
            workload_name: name shown in the message
            ip_version: determine ip version for the selected pools
        Returns:
            ([], []): first list contains the selected node objects. second list contains selected pool ids
        """
        resource_query = resource_query or {}
        cloud_units = self.calculate_capacity_units(**resource_query)
        pools = self.list_pools(cloud_units.cu, cloud_units.su, cloud_units.ipv4u)
        if pool_ids:
            filtered_pools = {}
            for pool_id in pools:
                if pool_id in pool_ids:
                    filtered_pools[pool_id] = pools[pool_id]
            pools = filtered_pools

        workload_name = workload_name or "workloads"
        messages = {}
        pool_factory = StoredFactory(PoolConfig)
        for p in pools:
            hidden = False
            name = ""
            if f"pool_{p}" in pool_factory.list_all():
                pool_config = pool_factory.get(f"pool_{p}")
                hidden = pool_config.hidden
                name = pool_config.name
            if hidden:
                continue
            if name:
                messages[f"Name: {name} Pool: {p} CU: {pools[p][0]} SU: {pools[p][1]}"] = p
            else:
                messages[f"Pool: {p} CU: {pools[p][0]} SU: {pools[p][1]}"] = p

        if not messages:
            raise StopChatFlow(f"no pools available for resources: {resource_query}")

        while True:
            pool_choices = bot.multi_list_choice(
                "Please select the pools you wish to distribute you" f" {workload_name} on",
                options=list(messages.keys()),
                required=True,
            )
            if not pool_choices:
                bot.md_show("You must select at least one pool. please click next to try again.")
            else:
                break

        pool_ids = {}
        node_to_pool = {}
        for p in pool_choices:
            pool = pool_ids.get(messages[p], j.sals.zos.get().pools.get(messages[p]))
            pool_ids[messages[p]] = pool.pool_id
            for node_id in pool.node_ids:
                node_to_pool[node_id] = pool

        nodes = j.sals.reservation_chatflow.reservation_chatflow.get_nodes(
            number_of_nodes, pool_ids=list(pool_ids.values()), ip_version=ip_version, **resource_query
        )
        selected_nodes = []
        selected_pool_ids = []
        for node in nodes:
            selected_nodes.append(node)
            pool = node_to_pool[node.node_id]
            selected_pool_ids.append(pool.pool_id)
        return selected_nodes, selected_pool_ids

    def chatflow_pools_check(self):
        if not self.list_pools():
            raise StopChatFlow("You don't have any capacity pools. Please create one first.")

    def chatflow_network_check(self, bot):
        networks = self.list_networks()
        if not networks:
            raise StopChatFlow("You don't have any deployed networks. Please create one first.")
        bot.all_network_viewes = networks

    def wait_demo_payment(self, bot, pool_id, exp=5, trigger_cus=0, trigger_sus=1, identity_name=None):
        expiration = j.data.time.now().timestamp + exp * 60
        msg = "<h2> Waiting on resource provisioning...</h2>"
        while j.data.time.get().timestamp < expiration:
            bot.md_show_update(msg, html=True)
            pool = j.sals.zos.get(identity_name).pools.get(pool_id)
            if pool.cus >= trigger_cus or pool.sus >= trigger_sus:
                bot.md_show_update("Preparing application resources")
                return True
            gevent.sleep(2)

        return False

    def wait_pool_payment(self, bot, pool_id, exp=5, qr_code=None, trigger_cus=0, trigger_sus=1, identity_name=None):
        expiration = j.data.time.now().timestamp + exp * 60
        msg = "<h2> Waiting for payment...</h2>"
        if qr_code:
            qr_encoded = j.tools.qrcode.base64_get(qr_code, scale=2)
            msg += f"Please scan the QR Code below (Using ThreeFold Connect Application) for the payment details"
            qr_code_msg = f"""
            <div class="text-center">
                <img style="border:1px dashed #85929E" src="data:image/png;base64,{qr_encoded}"/>
            </div>
            """
            pool = j.sals.zos.get(identity_name).pools.get(pool_id)
            msg = msg + self.msg_payment_info + qr_code_msg
        while j.data.time.get().timestamp < expiration:
            bot.md_show_update(msg, html=True)
            pool = j.sals.zos.get(identity_name).pools.get(pool_id)
            if pool.cus >= trigger_cus and pool.sus >= trigger_sus:
                bot.md_show_update("Preparing application resources")
                return True
            gevent.sleep(2)

        return False

    def wait_pool_reservation(self, reservation_id, exp=5, qr_code=None, bot=None, identity_name=None):
        expiration = j.data.time.now().timestamp + exp * 60
        msg = "<h2> Waiting for payment...</h2>"
        if qr_code:
            qr_encoded = j.tools.qrcode.base64_get(qr_code, scale=2)
            msg += f"Please scan the QR Code below (Using ThreeFold Connect Application) for the payment"
            qr_code_msg = f"""
            <div class="text-center">
                <img style="border:1px dashed #85929E" src="data:image/png;base64,{qr_encoded}"/>
            </div>
            """
            msg = msg + self.msg_payment_info + qr_code_msg
        zos = j.sals.zos.get(identity_name)
        if bot:
            bot.md_show_update(msg, html=True)
        while j.data.time.get().timestamp < expiration:
            payment_info = zos.pools.get_payment_info(reservation_id)
            if payment_info.paid and payment_info.released:
                return True
            if payment_info.canceled:
                raise DeploymentFailed(f"pool reservation {reservation_id} was cancelled because: {payment_info.cause}")
            gevent.sleep(2)
        return False

    def get_payment_info(self, pool):
        escrow_info = pool.escrow_information
        resv_id = pool.reservation_id
        escrow_address = escrow_info.address
        escrow_asset = escrow_info.asset
        total_amount = escrow_info.amount
        total_amount_dec = Decimal(total_amount) / Decimal(1e7)
        thecurrency = escrow_asset.split(":")[0]
        return {
            "escrow_info": escrow_info,
            "resv_id": resv_id,
            "escrow_address": escrow_address,
            "escrow_asset": escrow_asset,
            "total_amount_dec": total_amount_dec,
            "thecurrency": thecurrency,
            "total_amount": total_amount,
        }

    def get_qr_code_payment_info(self, pool):
        info = self.get_payment_info(pool)
        total_amount = "{0:f}".format(info["total_amount_dec"])
        qr_code = f"{info['thecurrency']}:{info['escrow_address']}?amount={total_amount}&message=p-{info['resv_id']}&sender=me"
        msg_text = f"""

        <h4> Destination Wallet Address: </h4>  {info['escrow_address']} \n
        <h4> Currency: </h4>  {info['thecurrency']} \n
        <h4> Memo Text (Reservation ID): </h4>  p-{info['resv_id']} \n
        <h4> Total Amount: </h4> {total_amount} {info['thecurrency']} \n

        <h5>Inserting the memo-text is an important way to identify a transaction recipient beyond a wallet address. Failure to do so will result in a failed payment. Please also keep in mind that an additional Transaction fee of 0.01 {info['thecurrency']} will automatically occur per transaction.</h5>
        """

        return msg_text, qr_code

    def test_managed_domain(self, gateway_id, managed_domain, pool_id, gateway=None, identity_name=None):
        zos = j.sals.zos.get(identity_name)
        identity_name = identity_name or j.core.identity.me.instance_name
        gateway = gateway or zos._explorer.gateway.get(gateway_id)
        subdomain = f"{uuid.uuid4().hex}.{managed_domain}"
        addresses = [j.sals.nettools.get_host_by_name(gateway.dns_nameserver[0])]
        subdomain_id = self.create_subdomain(pool_id, gateway_id, subdomain, addresses, identity_name=identity_name)
        success = self.wait_workload(subdomain_id, identity_name=identity_name)
        if not success:
            return False
        try:
            j.sals.nettools.get_host_by_name(subdomain)
        except Exception as e:
            j.logger.error(f"managed domain test failed for {managed_domain} due to error {str(e)}")
            zos.workloads.decomission(subdomain_id)
            return False
        zos.workloads.decomission(subdomain_id)
        return True

    def block_managed_domain(self, managed_domain):
        count = j.core.db.hincrby(DOMAINS_COUNT_KEY, managed_domain)
        expiration = count * DOMAINS_DISALLOW_EXPIRATION
        domain_key = f"{DOMAINS_DISALLOW_PREFIX}:{managed_domain}"
        j.core.db.set(domain_key, j.data.time.utcnow().timestamp + expiration, ex=expiration)

    def unblock_managed_domain(self, managed_domain, reset=True):
        domain_key = f"{DOMAINS_DISALLOW_PREFIX}:{managed_domain}"
        j.core.db.delete(domain_key)
        if reset:
            j.core.db.hdel(DOMAINS_COUNT_KEY, managed_domain)

    def list_blocked_managed_domains(self):
        blocked_domains_keys = j.core.db.keys(f"{DOMAINS_DISALLOW_PREFIX}:*")
        failure_count_dict = j.core.db.hgetall(DOMAINS_COUNT_KEY)
        blocked_domains_values = j.core.db.mget(blocked_domains_keys)
        result = {}
        for idx, key in enumerate(blocked_domains_keys):
            key = key[len(DOMAINS_DISALLOW_PREFIX) + 1 :]
            node_id = key.decode()
            expiration = int(blocked_domains_values[idx])
            failure_count = int(failure_count_dict[key])
            result[node_id] = {"expiration": expiration, "failure_count": failure_count}
        return result

    def clear_blocked_managed_domains(self):
        blocked_domains_keys = j.core.db.keys(f"{DOMAINS_DISALLOW_PREFIX}:*")

        if blocked_domains_keys:
            j.core.db.delete(*blocked_domains_keys)
        j.core.db.delete(DOMAINS_COUNT_KEY)

        return True

    def wait_workload_deletion(self, wid, timeout=5, identity_name=None):
        j.logger.info(f"waiting workload {wid} to be deleted")
        zos = j.sals.zos.get(identity_name)
        expiry = j.data.time.now().timestamp + timeout * 60
        while j.data.time.now().timestamp < expiry:
            workload = zos.workloads.get(wid)
            if workload.info.next_action == NextAction.DELETED:
                return True
            gevent.sleep(2)
        return False


deployer = ChatflowDeployer()
