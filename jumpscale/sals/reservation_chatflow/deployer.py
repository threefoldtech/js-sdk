import base64
import copy
import json
from jumpscale.loader import j
from jumpscale.core.base import StoredFactory
from jumpscale.sals.chatflows.chatflows import StopChatFlow
from jumpscale.clients.stellar.stellar import Network as StellarNetwork
from jumpscale.clients.explorer.models import NextAction, Type
from nacl.public import Box
import netaddr
import random
import requests
import time
from collections import defaultdict
from decimal import Decimal
import gevent


class NetworkView:
    def __init__(self, name, workloads=None):
        self.name = name
        if not workloads:
            workloads = j.sals.zos.workloads.list(j.core.identity.me.tid, NextAction.DEPLOY)
        self.workloads = workloads
        self.used_ips = []
        self.network_workloads = []
        self._fill_used_ips(self.workloads)
        self._init_network_workloads(self.workloads)
        self.iprange = self.network_workloads[0].network_iprange

    def _init_network_workloads(self, workloads):
        for workload in workloads:
            if workload.info.next_action != NextAction.DEPLOY:
                continue
            if workload.info.workload_type == Type.Network_resource and workload.name == self.name:
                self.network_workloads.append(workload)

    def _fill_used_ips(self, workloads):
        for workload in workloads:
            if workload.info.next_action != NextAction.DEPLOY:
                continue
            if workload.info.workload_type == Type.Kubernetes:
                self.used_ips.append(workload.ipaddress)
            elif workload.info.workload_type == Type.Container:
                for conn in workload.network_connection:
                    if conn.network_id == self.name:
                        self.used_ips.append(conn.ipaddress)

    def add_node(self, node, pool_id):
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
            network = j.sals.zos.network.create(self.iprange, self.name)
            node_workloads = {}
            for net_workload in self.network_workloads:
                node_workloads[net_workload.info.node_id] = net_workload
            network.network_resources = list(node_workloads.values())  # add only latest network resource for each node
            j.sals.zos.network.add_node(network, node.node_id, str(subnet), self.pool_id)
            return network

    def get_node_range(self, node):
        for workload in self.network_workloads:
            if workload.info.node_id == node.node_id:
                return workload.iprange
        raise StopChatFlow(f"Node {node.node_id} is not part of network")

    def copy(self):
        return NetworkView(self.name)

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


class ChatflowDeployer:
    def __init__(self):
        self.workloads = defaultdict(
            lambda: defaultdict(lambda: defaultdict(list))
        )  # Next Action: workload_type: pool_id: [workloads]
        self._explorer = j.core.identity.me.explorer

    def load_user_workloads(self, next_action=NextAction.DEPLOY):
        all_workloads = j.sals.zos.workloads.list(j.core.identity.me.tid, next_action)
        self.workloads.pop(next_action, None)
        for workload in all_workloads:
            if workload.info.metadata:
                workload.info.metadata = self.decrypt_metadata(workload.info.metadata)
            self.workloads[workload.info.next_action][workload.info.workload_type][workload.info.pool_id].append(
                workload
            )

    def decrypt_metadata(self, encrypted_metadata):
        try:
            pk = j.core.identity.me.nacl.signing_key.verify_key.to_curve25519_public_key()
            sk = j.core.identity.me.nacl.signing_key.to_curve25519_private_key()
            box = Box(sk, pk)
            return box.decrypt(base64.b85decode(encrypted_metadata.encode())).decode()
        except:
            return "{}"

    def list_networks(self, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            self.load_user_workloads(next_action=next_action)
        networks = {}  # name: last child network resource
        for pool_id in self.workloads[next_action][Type.Network_resource]:
            for workload in self.workloads[next_action][Type.Network_resource][pool_id]:
                networks[workload.name] = workload
        all_workloads = []
        for pools_workloads in self.workloads[next_action].values():
            for pool_id, workload_list in pools_workloads.items():
                all_workloads += workload_list
        network_views = {}
        for network_name in networks:
            network_views[network_name] = NetworkView(network_name, all_workloads)
        return network_views

    def create_pool(self, bot):
        form = bot.new_form()
        cu = form.int_ask("Please specify the required CU")
        su = form.int_ask("Please specify the required SU")
        currencies = form.single_choice("Please choose the currency", ["TFT", "FreeTFT", "TFTA"])
        form.ask()
        cu = cu.value
        su = su.value
        currencies = [currencies.value]
        all_farms = self._explorer.farms.list()
        available_farms = {}
        for farm in all_farms:
            res = self.check_farm_capacity(farm.name, currencies, cru=None, sru=None)
            available = res[0]
            resources = res[1:]
            if available:
                available_farms[farm.name] = resources
        farm_messages = {}
        for farm in available_farms:
            resources = available_farms[farm]
            farm_messages[
                f"{farm} cru: {resources[0]} sru: {resources[1]} hru: {resources[2]} mru {resources[3]}"
            ] = farm
        selected_farm = bot.single_choice("Please choose a farm", list(farm_messages.keys()))
        farm = farm_messages[selected_farm]
        try:
            pool_info = j.sals.zos.pools.create(cu, su, farm, currencies)
        except Exception as e:
            raise StopChatFlow(f"failed to reserve pool.\n{str(e)}")
        self.show_payment(pool_info, bot)
        return pool_info

    def check_farm_capacity(self, farm_name, currencies=[], sru=None, cru=None, mru=None, hru=None):
        farm_nodes = j.sals.zos.nodes_finder.nodes_search(farm_name=farm_name)
        available_cru = 0
        available_sru = 0
        available_mru = 0
        available_hru = 0
        for node in farm_nodes:
            if "FreeTFT" in currencies and not node.free_to_use:
                continue
            if not j.sals.zos.nodes_finder.filter_is_up(node):
                continue
            available_cru += node.total_resources.cru - node.used_resources.cru
            available_sru += node.total_resources.sru - node.used_resources.sru
            available_mru += node.total_resources.mru - node.used_resources.mru
            available_hru += node.total_resources.hru - node.used_resources.hru
        if sru and available_sru < sru:
            return False, available_cru, available_sru, available_mru, available_hru
        if cru and available_cru < cru:
            return False, available_cru, available_sru, available_mru, available_hru
        if mru and available_mru < mru:
            return False, available_cru, available_sru, available_mru, available_hru
        if hru and available_hru < hru:
            return False, available_cru, available_sru, available_mru, available_hru
        return True, available_cru, available_sru, available_mru, available_hru

    def show_payment(self, pool, bot):
        escrow_info = pool.escrow_information
        resv_id = pool.reservation_id
        escrow_address = escrow_info.address
        escrow_asset = escrow_info.asset
        total_amount = escrow_info.amount
        total_amount_dec = Decimal(total_amount) / Decimal(1e7)
        total_amount = "{0:f}".format(total_amount_dec)

        wallets = j.sals.reservation_chatflow.reservation_chatflow.list_wallets()
        wallet_names = []
        for w in wallets.keys():
            wallet_names.append(w)
        wallet_names.append("3bot app")
        message = f"""
        Billing details:
        <h4> Wallet address: </h4>  {escrow_address} \n
        <h4> Currency: </h4>  {escrow_asset} \n
        <h4> Choose a wallet name to use for payment or proceed with payment through 3bot app </h4>
        """
        result = bot.single_choice(message, wallet_names, html=True)
        if result == "3bot app":
            qr_code = (
                f"{escrow_asset.split(':')[0]}:{escrow_address}?amount={total_amount}&message=p-{resv_id}&sender=me"
            )
            msg_text = f"""
            <h3> Please make your payment </h3>
            Scan the QR code with your application (do not change the message) or enter the information below manually and proceed with the payment. Make sure to add the reservationid as memo_text.

            <h4> Wallet address: </h4>  {escrow_address} \n
            <h4> Currency: </h4>  {escrow_asset} \n
            <h4> Reservation id: </h4>  p-{resv_id} \n
            <h4> Total Amount: </h4> {total_amount} \n
            """
            bot.qrcode_show(data=qr_code, msg=msg_text, scale=4, update=True, html=True)
        else:
            wallet = wallets[result]
            wallet.transfer(
                destination_address=escrow_address, amount=total_amount, asset=escrow_asset, memo_text=f"p-{resv_id}",
            )

    def extend_pool(self, bot, pool_id):
        form = bot.new_form()
        cu = form.int_ask("Please specify the required CU")
        su = form.int_ask("Please specify the required SU")
        currencies = form.single_choice("Please choose the currency", ["TFT", "FreeTFT", "TFTA"])
        form.ask()
        cu = cu.value
        su = su.value
        currencies = [currencies.value]
        try:
            pool_info = j.sals.zos.pools.extend(pool_id, cu, su, currencies=currencies)
        except Exception as e:
            raise StopChatFlow(f"failed to extend pool.\n{str(e)}")
        self.show_payment(pool_info, bot)
        return pool_info

    def list_pools(self, cu=None, su=None):
        all_pools = j.sals.zos.pools.list()
        available_pools = {}
        for pool in all_pools:
            res = self.check_pool_capacity(pool, cu, su)
            available = res[0]
            if available:
                resources = res[1:]
                available_pools[pool.pool_id] = resources
        return available_pools

    def check_pool_capacity(self, pool, cu=None, su=None):
        available_su = pool.sus - pool.active_su
        available_cu = pool.cus - pool.active_cu
        if pool.empty_at < 0:
            return False, 0, 0
        if cu and available_cu < cu:
            return False, available_cu, available_su
        if su and available_su < su:
            return False, available_cu, available_su
        return True, available_cu, available_su

    def select_pool(self, bot, cu=None, su=None):
        available_pools = self.list_pools(cu, su)
        if not available_pools:
            raise StopChatFlow("no available pools")
        pool_messages = {}
        for pool in available_pools:
            pool_messages[f"Pool: {pool} cu: {available_pools[pool][0]} su: {available_pools[pool][1]}"] = pool
        pool = bot.single_choice("Please select a pool", list(pool_messages.keys()))
        return pool_messages[pool]

    def get_pool_farm_id(self, pool_id):
        pool = j.sals.zos.pools.get(pool_id)
        node_id = pool.node_ids[0]
        node = self._explorer.nodes.get(node_id)
        farm_id = node.farm_id
        return farm_id

    def check_pool_capacity(self, pool, cu=None, su=None):
        """
        pool: pool schema object
        """
        available_su = pool.sus - pool.active_su
        available_cu = pool.cus - pool.active_cu
        if pool.empty_at < 0:
            return False, 0, 0
        if cu and available_cu < cu:
            return False, available_cu, available_su
        if su and available_su < su:
            return False, available_cu, available_su
        return True, available_cu, available_su

    def ask_name(self, bot):
        name = bot.string_ask("Please enter a name for you workload", required=True, field="name")
        return name

    def encrypt_metadata(self, metadata):
        if isinstance(metadata, dict):
            metadata = j.data.serializers.json.dumps(metadata)
        pk = j.core.identity.me.nacl.signing_key.verify_key.to_curve25519_public_key()
        sk = j.core.identity.me.nacl.signing_key.to_curve25519_private_key()
        box = Box(sk, pk)
        encrypted_metadata = base64.b85encode(box.encrypt(metadata.encode())).decode()
        return encrypted_metadata

    def deploy_network(self, name, access_node, ip_range, ip_version, pool_id, **metadata):
        network = j.sals.zos.network.create(ip_range, name)
        node_subnets = netaddr.IPNetwork(ip_range).subnet(24)
        network_config = dict()
        use_ipv4 = ip_version == "IPv4"

        j.sals.zos.network.add_node(network, access_node.node_id, str(next(node_subnets)), pool_id)
        wg_quick = j.sals.zos.network.add_access(network, access_node.node_id, str(next(node_subnets)), ipv4=use_ipv4)

        network_config["wg"] = wg_quick
        j.sals.fs.mkdir(f"{j.core.dirs.CFGDIR}/wireguard/")
        j.sals.fs.write_file(f"{j.core.dirs.CFGDIR}/{name}.conf", f"{wg_quick}")

        ids = []
        parent_id = None
        for workload in network.network_resources:
            workload.info.description = j.data.serializers.json.dumps({"parent_id": parent_id})
            metadata["parent_network"] = parent_id
            workload.metadata = self.encrypt_metadata(metadata)
            ids.append(j.sals.zos.workloads.deploy(workload))
            parent_id = ids[-1]
        network_config["ids"] = ids
        network_config["rid"] = ids[0]
        return network_config

    def wait_workload(self, workload_id, bot=None):
        expiration_provisioning = j.data.time.now().timestamp + 15 * 60
        while True:
            workload = j.sals.zos.workloads.get(workload_id)
            remaning_time = j.data.time.get(expiration_provisioning).humanize(granularity=["minute", "second"])
            if bot:
                deploying_message = f"""
# Deploying...\n
Deployment will be cancelled if it is not successful in {remaning_time}
                """
                bot.md_show_update(deploying_message, md=True)
            if workload.info.result.workload_id:
                return workload.info.result.state.value == 1
            if expiration_provisioning < j.data.time.get().timestamp:
                j.sal.chatflow_solutions.cancel_solution([workload_id])
                raise StopChatFlow(f"Workload {workload_id} failed to deploy in time")
            gevent.sleep(1)


deployer = ChatflowDeployer()
