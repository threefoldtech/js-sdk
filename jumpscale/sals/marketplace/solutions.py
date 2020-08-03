from jumpscale.loader import j
from jumpscale.clients.explorer.models import NextAction, Type
from jumpscale.sals.reservation_chatflow.solutions import ChatflowSolutions


class MarketplaceSolutions(ChatflowSolutions):
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

    def list_ubuntu_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][Type.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = []
        for container_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][Type.Container].values():
            for workload in container_workloads:
                if not workload.info.metadata:
                    continue
                try:
                    metadata = j.data.serializers.json.loads(workload.info.metadata)
                except:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata.get("owner") != username:
                    continue
                if metadata["form_info"].get("chatflow") == "ubuntu":
                    result.append(
                        {
                            "wids": [workload.id],
                            "Name": metadata.get("name", metadata["form_info"].get("Solution name"))[
                                len(username) + 1 :
                            ],
                            "IPv4 Address": workload.network_connection[0].ipaddress,
                            "IPv6 Address": self.get_ipv6_address(workload),
                            "Network": workload.network_connection[0].network_id,
                            "Node": workload.info.node_id,
                            "Pool": workload.info.pool_id,
                        }
                    )
                    result[-1].update(self.get_workload_capacity(workload))
        return result


solutions = MarketplaceSolutions()
