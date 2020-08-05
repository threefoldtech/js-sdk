from jumpscale.clients.explorer.models import NextAction, Type
from jumpscale.core.base import StoredFactory
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import StopChatFlow
from jumpscale.sals.reservation_chatflow.deployer import ChatflowDeployer, NetworkView
from decimal import Decimal
from .models import UserPool


class MarketPlaceDeployer(ChatflowDeployer):
    def list_user_pool_ids(self, username):
        user_pools = self.list_user_pools(username)
        user_pool_ids = [p.pool_id for p in user_pools]
        return user_pool_ids

    def list_user_pools(self, username):
        pool_factory = StoredFactory(UserPool)
        _, _, user_pools = pool_factory.find_many(owner=username)
        all_pools = j.sals.zos.pools.list()
        user_pool_ids = [p.pool_id for p in user_pools]
        result = [p for p in all_pools if p.pool_id in user_pool_ids]
        return result

    def list_networks(self, username, next_action=NextAction.DEPLOY, sync=True):
        user_pool_ids = self.list_user_pool_ids(username)
        if sync:
            self.load_user_workloads(next_action=next_action)
        networks = {}  # name: last child network resource
        for pool_id in self.workloads[next_action][Type.Network_resource]:
            if pool_id in user_pool_ids:
                for workload in self.workloads[next_action][Type.Network_resource][pool_id]:
                    networks[workload.name] = workload
        all_workloads = []
        for pools_workloads in self.workloads[next_action].values():
            for pool_id, workload_list in pools_workloads.items():
                if pool_id in user_pool_ids:
                    all_workloads += workload_list
        network_views = {}
        if all_workloads:
            for network_name in networks:
                network_views[network_name] = NetworkView(network_name, all_workloads)
        return network_views

    def create_pool(self, username, bot):
        pool_info = super().create_pool(bot)
        pool_factory = StoredFactory(UserPool)
        user_pool = pool_factory.new(f"{username.replace('.3bot', '')}_{pool_info.reservation_id}")
        user_pool.owner = username
        user_pool.pool_id = pool_info.reservation_id
        user_pool.save()
        return pool_info

    def show_payment(self, pool, bot):
        escrow_info = pool.escrow_information
        resv_id = pool.reservation_id
        escrow_address = escrow_info.address
        escrow_asset = escrow_info.asset
        total_amount = escrow_info.amount
        total_amount_dec = Decimal(total_amount) / Decimal(1e7)
        total_amount = "{0:f}".format(total_amount_dec)
        qr_code = f"{escrow_asset.split(':')[0]}:{escrow_address}?amount={total_amount}&message=p-{resv_id}&sender=me"
        msg_text = f"""
        <h3> Please make your payment </h3>
        Scan the QR code with your application (do not change the message) or enter the information below manually and proceed with the payment. Make sure to add the reservationid as memo_text.

        <h4> Wallet address: </h4>  {escrow_address} \n
        <h4> Currency: </h4>  {escrow_asset} \n
        <h4> Reservation id: </h4>  p-{resv_id} \n
        <h4> Total Amount: </h4> {total_amount} \n
        """
        bot.qrcode_show(data=qr_code, msg=msg_text, scale=4, update=True, html=True)

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
        user_pools = available_pools or self.list_pools(username)
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
                farm_id = self.get_pool_farm_id(p)
                nodes = j.sals.reservation_chatflow.reservation_chatflow.check_farm_resources(
                    farm_id, **resource_query_list[i]
                )
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
        Choose multiple pools and to distribute workload automatically

        Args:
            bot: chatflow object
            resource_query: query dict {"cru": 1, "sru": 2, "mru": 1, "hru": 1}.
            pool_ids: if specfied it will limit the pools shown in the chatflow to only these pools
            workload_name: name shown in the message
        Returns:
            ([], []): first list contains the selected node objects. second list contains selected pool ids
        """
        resource_query = resource_query or {}
        pools = self.list_pools(username)
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
                f"Please seclect the pools you wish to distribute you {workload_name} on",
                options=list(messages.keys()),
                required=True,
            )
            if not pool_choices:
                bot.md_show("You must select at least one pool. please click next to try again.")
            else:
                break
        farm_to_pool = {}
        farm_names = []
        pool_ids = {}
        for p in pool_choices:
            pool = pool_ids.get(messages[p], j.sals.zos.pools.get(messages[p]))
            pool_ids[messages[p]] = pool
            farm_id = self._explorer.nodes.get(pool.node_ids[0]).farm_id
            farm_name = self._explorer.farms.get(farm_id).name
            farm_to_pool[farm_id] = pool
            farm_names.append(farm_name)
        nodes = j.sals.reservation_chatflow.reservation_chatflow.get_nodes(
            number_of_nodes, farm_names=farm_names, **resource_query
        )
        selected_nodes = []
        selected_pool_ids = []
        for node in nodes:
            selected_nodes.append(node)
            pool = farm_to_pool[node.farm_id]
            selected_pool_ids.append(pool.pool_id)
        return selected_nodes, selected_pool_ids


deployer = MarketPlaceDeployer()
