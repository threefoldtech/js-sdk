from jumpscale.clients.explorer.models import NextAction, WorkloadType
from jumpscale.loader import j
from jumpscale.sals.reservation_chatflow.solutions import ChatflowSolutions
from jumpscale.core.base import StoredFactory
from .models import UserPool


class MarketplaceSolutions(ChatflowSolutions):
    def list_network_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        networks = j.sals.marketplace.deployer.list_networks(username, next_action=next_action)
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
        return self._list_single_container_solution("ubuntu", next_action, sync, owner=username)

    def list_peertube_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("peertube", next_action, sync, owner=username)

    def list_discourse_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("discourse", next_action, sync, owner=username)

    def list_taiga_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("taiga", next_action, sync, "nginx", owner=username)

    def list_flist_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self._list_single_container_solution("flist", next_action, sync, owner=username)

    def list_gitea_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("gitea", next_action, sync, "nginx", owner=username)

    def list_mattermost_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("mattermost", next_action, sync, "nginx", owner=username)

    def list_meetings_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("meetings", next_action, sync, "nginx", owner=username)

    def list_publisher_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("publisher", next_action, sync, None, owner=username)

    def list_wiki_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("wiki", next_action, sync, None, owner=username)

    def list_blog_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("blog", next_action, sync, None, owner=username)

    def list_website_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("website", next_action, sync, None, owner=username)

    def list_threebot_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("threebot", next_action, sync, owner=username)

    def list_gollum_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self._list_single_container_solution("gollum", next_action, sync, owner=username)

    def list_cryptpad_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("cryptpad", next_action, sync, "nginx", owner=username)

    def list_minio_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = []
        container_workloads = self._list_container_workloads(
            "minio",
            next_action,
            metadata_filters=[lambda metadata: False if metadata.get("owner") != username else True],
        )
        for name in container_workloads:
            primary_dict = container_workloads[name][0]
            solution_dict = {
                "wids": [primary_dict["wid"]] + primary_dict["vol_ids"],
                "Name": name[len(username) + 1 :],
                "Network": primary_dict["network"],
                "Primary IPv4": primary_dict["ipv4"],
                "Primary IPv6": primary_dict["ipv6"],
                "Primary Pool": primary_dict["pool"],
            }
            for key, val in primary_dict["capacity"].items():
                solution_dict[f"Primary {key}"] = val
            if len(container_workloads[name]) == 2:
                secondary_dict = container_workloads[name][1]
                solution_dict["wids"].append(secondary_dict["wid"])
                solution_dict["wids"] += secondary_dict["vol_ids"]
                solution_dict.update(
                    {
                        "Secondary IPv4": secondary_dict["ipv4"],
                        "Secondary IPv6": secondary_dict["ipv6"],
                        "Secondary Pool": secondary_dict["pool"],
                    }
                )
                for key, val in secondary_dict["capacity"].items():
                    solution_dict[f"Secondary {key}"] = val
            result.append(solution_dict)
        return result

    def list_monitoring_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = []
        container_workloads = self._list_container_workloads(
            "monitoring",
            next_action,
            metadata_filters=[lambda metadata: False if metadata.get("owner") != username else True],
        )
        for name in container_workloads:
            if len(container_workloads[name]) != 3:
                continue
            solution_dict = {"wids": [], "Name": name[len(username) + 1 :]}
            for c_dict in container_workloads[name]:
                solution_dict["wids"].append(c_dict["wid"])
                solution_dict["wids"] += c_dict["vol_ids"]
                if "grafana" in c_dict["flist"]:
                    cont_type = "Grafana"
                elif "prometheus" in c_dict["flist"]:
                    cont_type = "Prometheus"
                elif "redis_zinit" in c_dict["flist"]:
                    cont_type = "Redis"
                else:
                    continue
                solution_dict[f"{cont_type} IPv4"] = c_dict["ipv4"]
                solution_dict[f"{cont_type} IPv6"] = c_dict["ipv6"]
                solution_dict[f"{cont_type} Node"] = c_dict["node"]
                solution_dict[f"{cont_type} Pool"] = c_dict["pool"]
                for key, val in c_dict["capacity"].items():
                    solution_dict[f"{cont_type} {key}"] = val
            result.append(solution_dict)
        return result

    def list_kubernetes_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Kubernetes]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = {}
        for kube_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Kubernetes
        ].values():
            for workload in kube_workloads:
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
                name = metadata["form_info"].get("Solution name", metadata.get("name"))
                if name:
                    if name in result:
                        if len(workload.master_ips) != 0:
                            result[name]["wids"].append(workload.id)
                            result[name]["Slave IPs"].append(workload.ipaddress)
                            result[name]["Slave Pools"].append(workload.info.pool_id)
                        continue
                    result[name] = {
                        "wids": [workload.id],
                        "Name": name[len(username) + 1 :],
                        "Network": workload.network_id,
                        "Master IP": workload.ipaddress if len(workload.master_ips) == 0 else workload.master_ips[0],
                        "Slave IPs": [],
                        "Slave Pools": [],
                        "Master Pool": workload.info.pool_id,
                    }
                    result[name].update(self.get_workload_capacity(workload))
                    if len(workload.master_ips) != 0:
                        result[name]["Slave IPs"].append(workload.ipaddress)
        return list(result.values())

    def list_4to6gw_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Gateway4to6]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = []
        for gateways in j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Gateway4to6].values():
            for g in gateways:
                if not g.info.metadata:
                    continue
                try:
                    metadata = j.data.serializers.json.loads(g.info.metadata)
                except:
                    continue
                if metadata.get("owner") != username:
                    continue
                result.append(
                    {
                        "wids": [g.id],
                        "Name": g.public_key,
                        "Public Key": g.public_key,
                        "Gateway": g.info.node_id,
                        "Pool": g.info.pool_id,
                    }
                )
        return result

    def list_delegated_domain_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Domain_delegate]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = []
        for domains in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Domain_delegate
        ].values():
            for dom in domains:
                try:
                    metadata = j.data.serializers.json.loads(dom.info.metadata)
                except:
                    continue
                if metadata.get("owner") != username:
                    continue
                result.append(
                    {"wids": [dom.id], "Name": dom.domain, "Gateway": dom.info.node_id, "Pool": dom.info.pool_id,}
                )
        return result

    def list_exposed_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Reverse_proxy]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = {}
        pools = set()
        name_to_proxy = {}
        for proxies in j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Reverse_proxy].values():
            for proxy in proxies:
                if proxy.info.metadata:
                    metadata = j.data.serializers.json.loads(proxy.info.metadata)
                    if not metadata:
                        continue
                    if metadata.get("owner") != username:
                        continue
                    chatflow = metadata.get("form_info", {}).get("chatflow")
                    if chatflow and chatflow != "exposed":
                        continue
                    result[f"{proxy.info.pool_id}-{proxy.domain}"] = {
                        "wids": [proxy.id],
                        "Name": proxy.domain,
                        "Gateway": proxy.info.node_id,
                        "Pool": proxy.info.pool_id,
                        "Domain": proxy.domain,
                    }
                    name = metadata.get("Solution name", metadata.get("form_info", {}).get("Solution name"),)
                    name_to_proxy[name] = f"{proxy.info.pool_id}-{proxy.domain}"
                pools.add(proxy.info.pool_id)

        # link subdomains to proxy_reservations
        for subdomains in j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Subdomain].values():
            for workload in subdomains:
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if metadata.get("owner") != username:
                    continue
                chatflow = metadata.get("form_info", {}).get("chatflow")
                if chatflow and chatflow != "exposed":
                    continue
                solution_name = metadata.get(
                    "Solution name", metadata.get("name", metadata.get("form_info", {}).get("Solution name")),
                )
                if not solution_name:
                    continue
                domain = workload.domain
                if name_to_proxy.get(solution_name):
                    result[name_to_proxy[solution_name]]["wids"].append(workload.id)

        # link tcp router containers to proxy reservations
        for pool_id in pools:
            for container_workload in j.sals.reservation_chatflow.deployer.workloads[next_action][
                WorkloadType.Container
            ][pool_id]:
                if (
                    container_workload.flist != "https://hub.grid.tf/tf-official-apps/tcprouter:latest.flist"
                    or not container_workload.info.metadata
                ):
                    continue
                metadata = j.data.serializers.json.loads(container_workload.info.metadata)
                if not metadata:
                    continue
                if metadata.get("owner") != username:
                    continue
                chatflow = metadata.get("form_info", {}).get("chatflow")
                if chatflow and chatflow != "exposed":
                    continue
                solution_name = metadata.get(
                    "Solution name", metadata.get("name", metadata.get("form_info", {}).get("Solution name")),
                )
                if not solution_name:
                    continue
                if name_to_proxy.get(solution_name):
                    domain = name_to_proxy.get(solution_name)
                    result[domain]["wids"].append(container_workload.id)
        return list(result.values())

    def count_solutions(self, username, next_action=NextAction.DEPLOY):
        count_dict = {
            "network": 0,
            "ubuntu": 0,
            "kubernetes": 0,
            "minio": 0,
            "monitoring": 0,
            "flist": 0,
            "gitea": 0,
            "4to6gw": 0,
            "delegated_domain": 0,
            "exposed": 0,
            "publisher": 0,
            "peertube": 0,
            "discourse": 0,
            "mattermost": 0,
            "threebot": 0,
            "cryptpad": 0,
            "pools": 0,
            "wiki": 0,
            "blog": 0,
            "website": 0,
            "taiga": 0,
            "meetings": 0,
        }
        j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        for key in count_dict.keys():
            method = getattr(self, f"list_{key}_solutions")
            count_dict[key] = len(method(username, next_action=next_action, sync=False))
        return count_dict

    def list_pools_solutions(self, username, next_action=NextAction.DEPLOY, sync=False):
        pools = j.sals.marketplace.deployer.list_user_pools(username)
        result = [pool.to_dict() for pool in pools]
        return result

    def list_solutions(self, username, solution_type):
        j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=NextAction.DEPLOY)
        method = getattr(self, f"list_{solution_type}_solutions")
        return method(username, next_action=NextAction.DEPLOY, sync=False)

    def cancel_solution(self, username, solution_wids, delete_pool=False):
        valid = True
        pool_id = None
        for wid in solution_wids:
            workload = j.sals.zos.get().workloads.get(wid)
            if workload.info.workload_type == WorkloadType.Container:
                pool_id = workload.info.pool_id
            metadata_json = j.sals.reservation_chatflow.deployer.decrypt_metadata(workload.info.metadata)
            metadata = j.data.serializers.json.loads(metadata_json)
            if metadata.get("owner") != username:
                valid = False
                break
        if valid:
            if pool_id and delete_pool:
                # deassociate the pool from user
                pool_factory = StoredFactory(UserPool)
                instance_name = f"pool_{username.replace('.3bot', '')}_{pool_id}"
                pool_factory.delete(instance_name)
            super().cancel_solution(solution_wids)


solutions = MarketplaceSolutions()
