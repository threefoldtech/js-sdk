from jumpscale.loader import j
from jumpscale.clients.explorer.models import NextAction, Type


class ChatflowSolutions:
    def list_network_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        networks = j.sals.reservation_chatflow.deployer.list_networks(next_action=next_action, sync=sync)
        if not sync and not networks:
            networks = j.sals.reservation_chatflow.deployer.list_networks(next_action=next_action, sync=False)
        result = []
        for n in networks.values():
            result.append(
                {
                    "Name": n.name,
                    "IP Range": n.network_workloads[-1].network_iprange,
                    "Pool": n.network_workloads[-1].info.pool_id,
                    "nodes": {res.info.node_id: res.iprange for res in n.network_workloads},
                    "wids": [res.id for res in n.network_workloads],
                }
            )
        return result


solutions = ChatflowSolutions()
