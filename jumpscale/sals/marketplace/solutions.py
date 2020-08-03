from jumpscale.loader import j
from jumpscale.clients.explorer.models import NextAction, Type


class MarketplaceSolutions:
    def list_network_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        networks = j.sals.marketplace.deployer.list_networks(username, next_action=next_action, sync=sync)
        if not sync and not networks:
            networks = j.sals.marketplace.deployer.list_networks(username, next_action=next_action, sync=False)
        result = []
        for n in networks.values():
            if len(n.network_workloads) == 0:
                continue
            result.append(
                {
                    "Name": n.name[len(username) + 1 :],
                    "IP Range": n.network_workloads[-1].network_iprange,
                    "nodes": {res.info.node_id: res.iprange for res in n.network_workloads},
                    "wids": [res.id for res in n.network_workloads],
                }
            )
        return result


solutions = MarketplaceSolutions()
