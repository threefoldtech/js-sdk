import math
import random

from jumpscale.clients.explorer.models import NextAction, WorkloadType
from jumpscale.core.base import StoredFactory
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import StopChatFlow
from jumpscale.sals.reservation_chatflow import DeploymentFailed
from jumpscale.sals.reservation_chatflow.deployer import ChatflowDeployer, NetworkView

from .models import UserPool


class MarketPlaceDeployer(ChatflowDeployer):

    WALLET_NAME = "demos_wallet"

    def list_user_pool_ids(self, username):
        user_pools = self.list_user_pools(username)
        user_pool_ids = [p.pool_id for p in user_pools]
        return user_pool_ids

    def list_user_pools(self, username):
        pool_factory = StoredFactory(UserPool)
        _, _, user_pools = pool_factory.find_many(owner=username)
        all_pools = [p for p in j.sals.zos.pools.list() if p.node_ids]
        user_pool_ids = [p.pool_id for p in user_pools]
        result = [p for p in all_pools if p.pool_id in user_pool_ids]
        return result

    def list_networks(self, username, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            self.load_user_workloads(next_action=next_action)
        networks = {}  # name: last child network resource
        for pool_id in self.workloads[next_action][WorkloadType.Network_resource]:
            for workload in self.workloads[next_action][WorkloadType.Network_resource][pool_id]:
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if metadata.get("owner") == username:
                    networks[workload.name] = workload
        all_workloads = []
        workload_values = self.workloads[next_action].values()
        for pools_workloads in workload_values:
            for pool_id, workload_list in pools_workloads.items():
                for workload in workload_list:
                    metadata = j.data.serializers.json.loads(workload.info.metadata)
                    if metadata.get("owner") == username:
                        all_workloads.append(workload)
        network_views = {}
        if all_workloads:
            for network_name in networks:
                network_views[network_name] = NetworkView(network_name, all_workloads)
        return network_views

    def create_pool(self, username, bot):
        pool_info = super().create_pool(bot)
        pool_factory = StoredFactory(UserPool)
        user_pool = pool_factory.new(f"pool_{username.replace('.3bot', '')}_{pool_info.reservation_id}")
        user_pool.owner = username
        user_pool.pool_id = pool_info.reservation_id
        user_pool.save()
        return pool_info

    def show_payment(self, pool, bot):
        resv_id = pool.reservation_id
        resv_id_msg_text = f"""<h3>Make a Payment</h3>
        Scan the QR code with your wallet (do not change the message) or enter the information below manually and proceed with the payment. Make sure to put p-{resv_id} as memo_text value.
        """
        self.msg_payment_info, qr_code = self.get_qr_code_payment_info(pool)
        msg_text = resv_id_msg_text + self.msg_payment_info
        bot.qrcode_show(data=qr_code, msg=msg_text, scale=4, update=True, html=True, pool=pool)
        return qr_code

    def pay_for_pool(self, pool):
        info = self.get_payment_info(pool)
        WALLET_NAME = j.sals.marketplace.deployer.WALLET_NAME
        wallet = j.clients.stellar.get(name=WALLET_NAME)
        wallet.transfer(
            destination_address=info["escrow_address"],
            amount=info["total_amount_dec"],
            asset=info["escrow_asset"],
            memo_text=f"p-{info['resv_id']}",
        )

    def list_pools(self, username=None, cu=None, su=None):
        all_pools = self.list_user_pools(username)
        available_pools = {}
        for pool in all_pools:
            res = self.check_pool_capacity(pool, cu, su)
            available = res[0]
            if available:
                resources = res[1:]
                available_pools[pool.pool_id] = resources
        return available_pools

    def select_pool(
        self,
        username,
        bot,
        cu=None,
        su=None,
        sru=None,
        mru=None,
        hru=None,
        cru=None,
        available_pools=None,
        workload_name=None,
    ):
        user_pools = available_pools or self.list_pools(username, su=su, cu=cu)
        return super().select_pool(
            bot,
            cu=cu,
            su=su,
            sru=sru,
            mru=mru,
            hru=hru,
            cru=cru,
            available_pools=user_pools,
            workload_name=workload_name,
        )

    def select_network(self, username, bot):
        network_views = self.list_networks(username)
        network_names = [n[len(username) + 1 :] for n in network_views.keys()]
        if not network_views:
            raise StopChatFlow(f"You don't have any deployed network.")
        network_name = bot.single_choice("Please select a network", network_names, required=True)
        return network_views[f"{username}_{network_name}"]

    def list_all_gateways(self, username):
        pool_ids = self.list_user_pool_ids(username)
        return super().list_all_gateways(pool_ids=pool_ids)

    def select_gateway(self, username, bot):
        """
        Args:
            pool_ids: if specified it will only list gateways inside these pools

        Returns:
            gateway, pool_objects
        """
        gateways = self.list_all_gateways(username)
        selected = bot.single_choice("Please select a gateway", list(gateways.keys()), required=True)
        return gateways[selected]["gateway"], gateways[selected]["pool"]

    def ask_multi_pool_placement(
        self, username, bot, number_of_nodes, resource_query_list=None, pool_ids=None, workload_names=None
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

        pools = self.list_pools(username)
        if pool_ids:
            filtered_pools = {}
            for pool_id in pools:
                if pool_id in pool_ids:
                    filtered_pools[pool_id] = pools[pool_id]
            pools = filtered_pools
        selected_nodes = []
        selected_pool_ids = []
        for i in range(number_of_nodes):
            cu, su = self.calculate_capacity_units(**resource_query_list[i])
            pool_choices = {}
            for p in pools:
                if pools[p][0] < cu or pools[p][1] < su:
                    continue
                nodes = j.sals.zos.nodes_finder.nodes_by_capacity(pool_id=p, **resource_query_list[i])
                if not nodes:
                    continue
                pool_choices[p] = pools[p]
            pool_id = self.select_pool(
                username, bot, available_pools=pool_choices, workload_name=workload_names[i], cu=cu, su=su
            )
            node = self.ask_container_placement(bot, pool_id, workload_name=workload_names[i], **resource_query_list[i])
            if not node:
                node = self.schedule_container(pool_id, **resource_query_list[i])
            selected_nodes.append(node)
            selected_pool_ids.append(pool_id)
        return selected_nodes, selected_pool_ids

    def ask_multi_pool_distribution(
        self, username, bot, number_of_nodes, resource_query=None, pool_ids=None, workload_name=None
    ):
        """
        Choose multiple pools to distribute workload automatically

        Args:
            bot: chatflow object
            resource_query: query dict {"cru": 1, "sru": 2, "mru": 1, "hru": 1}.
            pool_ids: if specfied it will limit the pools shown in the chatflow to only these pools
            workload_name: name shown in the message
        Returns:
            ([], []): first list contains the selected node objects. second list contains selected pool ids
        """
        resource_query = resource_query or {}
        cu, su = self.calculate_capacity_units(**resource_query)
        pools = self.list_pools(username, cu, su)
        if pool_ids:
            filtered_pools = {}
            for pool_id in pools:
                if pool_id in pool_ids:
                    filtered_pools[pool_id] = pools[pool_id]
            pools = filtered_pools

        workload_name = workload_name or "workloads"
        messages = {f"Pool: {p} CU: {pools[p][0]} SU: {pools[p][1]}": p for p in pools}
        while True:
            pool_choices = bot.multi_list_choice(
                f"Please select the pools you wish to distribute your {workload_name} on",
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
            pool = pool_ids.get(messages[p], j.sals.zos.pools.get(messages[p]))
            pool_ids[messages[p]] = pool.pool_id
            for node_id in pool.node_ids:
                node_to_pool[node_id] = pool

        nodes = j.sals.reservation_chatflow.reservation_chatflow.get_nodes(
            number_of_nodes, pool_ids=list(pool_ids.values()), **resource_query
        )
        selected_nodes = []
        selected_pool_ids = []
        for node in nodes:
            selected_nodes.append(node)
            pool = node_to_pool[node.node_id]
            selected_pool_ids.append(pool.pool_id)
        return selected_nodes, selected_pool_ids

    def extend_solution_pool(self, bot, pool_id, expiration, currency, **resources):
        cu, su = self.calculate_capacity_units(**resources)
        cu = math.ceil(cu * expiration)
        su = math.ceil(su * expiration)

        # guard in case of negative results
        cu = max(cu, 0)
        su = max(su, 0)

        if not isinstance(currency, list):
            currency = [currency]
        if cu > 0 or su > 0:
            pool_info = j.sals.zos.pools.extend(pool_id, cu, su, currency)
            qr_code = self.show_payment(pool_info, bot)
            return pool_info, qr_code
        else:
            return None, None

    def create_solution_pool(self, bot, username, farm_name, expiration, currency, **resources):
        cu, su = self.calculate_capacity_units(**resources)
        pool_info = j.sals.zos.pools.create(int(cu * expiration), int(su * expiration), farm_name, [currency])
        pool_factory = StoredFactory(UserPool)
        user_pool = pool_factory.new(f"pool_{username.replace('.3bot', '')}_{pool_info.reservation_id}")
        user_pool.owner = username
        user_pool.pool_id = pool_info.reservation_id
        user_pool.save()
        return pool_info

    def get_free_pools(self, username, workload_types=None):
        user_pools = self.list_user_pools(username)
        j.sals.reservation_chatflow.deployer.load_user_workloads()
        free_pools = []
        workload_types = workload_types or [WorkloadType.Container]
        for pool in user_pools:
            valid = True
            for wokrkload_type in workload_types:
                if j.sals.reservation_chatflow.deployer.workloads[NextAction.DEPLOY][wokrkload_type][pool.pool_id]:
                    valid = False
                    break
            if not valid:
                continue
            if (pool.cus == 0 and pool.sus == 0) or pool.empty_at < j.data.time.now().timestamp:
                continue
            free_pools.append(pool)
        return free_pools

    def get_best_fit_pool(self, pools, expiration, cru=0, mru=0, sru=0, hru=0, free_to_use=False):
        def is_pool_free(pool, nodes_dict):
            for node_id in pool.node_ids:
                node = nodes_dict.get(node_id)
                if node and not node.free_to_use:
                    return False
            return True

        cu, su = self.calculate_capacity_units(cru, mru, sru, hru)
        required_cu = cu * expiration
        required_su = su * expiration
        exact_fit_pools = []  # contains pools that are exact match of the required resources
        over_fit_pools = []  # contains pools that have higher cus AND sus than the required resources
        under_fit_pools = []  # contains pools that have lower cus OR sus than the required resources
        nodes = {}
        if free_to_use:
            nodes = {node.node_id: node for node in j.sals.zos._explorer.nodes.list()}
        for pool in pools:
            if free_to_use and not is_pool_free(pool, nodes):
                continue
            if pool.cus == required_cu and pool.sus == required_su:
                exact_fit_pools.append(pool)
            else:
                if pool.cus < required_cu or pool.sus < required_su:
                    under_fit_pools.append(pool)
                else:
                    over_fit_pools.append(pool)
        if exact_fit_pools:
            return random.choice(exact_fit_pools), 0, 0

        if over_fit_pools:
            # sort overfit_pools ascending according to the sum of extra cus and sus
            for pool in over_fit_pools:
                pool.unit_diff = pool.cus + pool.sus - required_cu - required_su
            sorted_result = sorted(over_fit_pools, key=lambda x: x.unit_diff)
            result_pool = sorted_result[0]
            return result_pool, result_pool.cus - required_cu, result_pool.sus - required_su
        else:
            # sort underfit pools descending according to the sum of diff cus and sus
            for pool in under_fit_pools:
                pool.unit_diff = pool.cus + pool.sus - required_cu - required_su
            sorted_result = sorted(under_fit_pools, key=lambda x: x.unit_diff, reverse=True)
            result_pool = sorted_result[0]
            return result_pool, result_pool.cus - required_cu, result_pool.sus - required_su

    def init_new_user_network(self, bot, username, pool_id):
        access_node = j.sals.reservation_chatflow.reservation_chatflow.get_nodes(
            1, pool_ids=[pool_id], ip_version="IPv4"
        )[0]

        result = self.deploy_network(
            name=f"{username}_apps",
            access_node=access_node,
            ip_range="10.100.0.0/16",
            ip_version="IPv4",
            pool_id=pool_id,
            owner=username,
        )
        for wid in result["ids"]:
            try:
                success = self.wait_workload(wid, bot=bot)
            except StopChatFlow as e:
                for sol_wid in result["ids"]:
                    j.sals.zos.workloads.decomission(sol_wid)
                raise e
            if not success:
                for sol_wid in result["ids"]:
                    j.sals.zos.workloads.decomission(sol_wid)
                raise DeploymentFailed(
                    f"Failed to deploy apps network in workload {wid}. The resources you paid for will be re-used in your upcoming deployments.",
                    wid=wid,
                )
        wgcfg = result["wg"]
        return wgcfg

    def init_new_user(self, bot, username, farm_name, expiration, currency, **resources):
        pool_info = self.create_solution_pool(bot, username, farm_name, expiration, currency, **resources)
        qr_code = self.show_payment(pool_info, bot)
        result = self.wait_pool_payment(bot, pool_info.reservation_id, qr_code=qr_code)
        if not result:
            raise StopChatFlow(f"Waiting for pool payment timedout. pool_id: {pool_info.reservation_id}")

        wgcfg = self.init_new_user_network(bot, username, pool_info.reservation_id)
        return pool_info, wgcfg

    def ask_expiration(self, bot, default=None, msg="", min=None, pool_empty_at=None):
        default = default or j.data.time.utcnow().timestamp + 3900
        min = min or 3600
        timestamp_now = j.data.time.utcnow().timestamp
        min_message = f"Date/time should be at least {j.data.time.get(timestamp_now+min).humanize()} from now"
        self.expiration = bot.datetime_picker(
            "Please enter the solution's expiration time" if not msg else msg,
            required=True,
            min_time=[min, min_message],
            default=default,
        )
        current_pool_expiration = pool_empty_at or j.data.time.utcnow().timestamp
        return self.expiration - current_pool_expiration


deployer = MarketPlaceDeployer()
