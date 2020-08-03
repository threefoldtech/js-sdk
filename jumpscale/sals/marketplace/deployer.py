from jumpscale.sals.reservation_chatflow.deployer import ChatflowDeployer, NetworkView
from jumpscale.clients.explorer.models import NextAction, Type
from jumpscale.loader import j
from jumpscale.core.base import StoredFactory
from .models import UserPool
from jumpscale.sals.chatflows.chatflows import StopChatFlow


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

    def list_pools(self, username, cu=None, su=None):
        all_pools = self.list_user_pools(username)
        available_pools = {}
        for pool in all_pools:
            res = self.check_pool_capacity(pool, cu, su)
            available = res[0]
            if available:
                resources = res[1:]
                available_pools[pool.pool_id] = resources
        return available_pools

    def select_pool(self, username, bot, cu=None, su=None, sru=None, mru=None, hru=None, cru=None, workload_name=None):
        user_pools = self.list_pools(username)
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
        network_name = bot.single_choice("Please select a network", network_names)
        return network_views[f"{username}_{network_name}"]

    def ask_multi_pool_placement(self, username, bot, number_of_nodes, resource_query_list=None, workload_names=None):
        pool_ids = self.list_user_pool_ids(username)
        return super().ask_multi_pool_placement(
            bot=bot,
            number_of_nodes=number_of_nodes,
            resource_query_list=resource_query_list,
            pool_ids=pool_ids,
            workload_names=workload_names,
        )

    def list_all_gateways(self, username):
        pool_ids = self.list_user_pool_ids(username)
        return super().list_all_gateways(pool_ids=pool_ids)

    def select_gateway(self, username, bot):
        pool_ids = self.list_user_pool_ids(username)
        return super().select_gateway(bot, pool_ids=pool_ids)


deployer = MarketPlaceDeployer()
