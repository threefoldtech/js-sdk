from jumpscale.clients.explorer.models import NextAction, WorkloadType
from jumpscale.loader import j
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
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = []
        for container_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Container
        ].values():
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

    def list_flist_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = []
        for container_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Container
        ].values():
            for workload in container_workloads:
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if metadata.get("owner") != username:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata["form_info"].get("chatflow") == "flist":
                    solution_dict = {
                        "wids": [workload.id],
                        "Name": metadata.get("name", metadata["form_info"].get("Solution name"))[len(username) + 1 :],
                        "IPv4 Address": workload.network_connection[0].ipaddress,
                        "IPv6 Address": self.get_ipv6_address(workload),
                        "Network": workload.network_connection[0].network_id,
                        "Node": workload.info.node_id,
                        "Pool": workload.info.pool_id,
                    }
                    solution_dict.update(self.get_workload_capacity(workload))
                    if workload.volumes:
                        for vol in workload.volumes:
                            solution_dict["wids"].append(vol.volume_id.split("-")[0])
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
                    if f"{name}" in result:
                        if len(workload.master_ips) != 0:
                            result[f"{name}"]["wids"].append(workload.id)
                            result[f"{name}"]["Slave IPs"].append(workload.ipaddress)
                            result[f"{name}"]["Slave Pools"].append(workload.info.pool_id)
                        continue
                    result[f"{name}"] = {
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
                        result[f"{name}"]["Slave IPs"].append(workload.ipaddress)
        return list(result.values())

    def list_minio_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        # TODO: add related ZDB wids to solution dict
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = {}
        for container_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Container
        ].values():
            for workload in container_workloads:
                if not workload.info.metadata:
                    continue
                try:
                    metadata = j.data.serializers.json.loads(workload.info.metadata)
                except:
                    metadata = j.data.serializers.json.loads(
                        j.sals.reservation_chatflow.deployer.decrypt_metadata(workload.info.metadata)
                    )
                    if not metadata:
                        continue
                if not metadata.get("form_info"):
                    continue
                if metadata.get("owner") != username:
                    continue
                if metadata["form_info"].get("chatflow") == "minio":
                    name = metadata["form_info"].get("Solution name", metadata.get("name"))
                    if name:
                        if f"{name}" in result:
                            result[f"{name}"]["wids"].append(workload.id)
                            result[f"{name}"]["Secondary IPv4"] = workload.network_connection[0].ipaddress
                            result[f"{name}"]["Secondary IPv6"] = self.get_ipv6_address(workload)
                            result[f"{name}"]["Secondary Node"] = workload.network_connection[0].ipaddress
                            result[f"{name}"]["Secondary Pool"] = workload.info.pool_id
                            for key, value in self.get_workload_capacity(workload).items():
                                result[name][f"Secondary {key}"] = value
                            if workload.volumes:
                                for vol in workload.volumes:
                                    result[f"{name}"]["wids"].append(vol.volume_id.split("-")[0])
                            continue
                        result[f"{name}"] = {
                            "wids": [workload.id],
                            "Name": name[len(username) + 1 :],
                            "Network": workload.network_connection[0].network_id,
                            "Primary IPv4": workload.network_connection[0].ipaddress,
                            "Primary IPv6": self.get_ipv6_address(workload),
                            "Primary Node": workload.info.node_id,
                            "Primary Pool": workload.info.pool_id,
                        }
                        for key, value in self.get_workload_capacity(workload).items():
                            result[name][f"Primary {key}"] = value
                        if workload.volumes:
                            for vol in workload.volumes:
                                result[f"{name}"]["wids"].append(vol.volume_id.split("-")[0])
        return list(result.values())

    def list_monitoring_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = {}
        for container_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Container
        ].values():
            for workload in container_workloads:
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
                    continue
                if not metadata.get("username") != username:
                    continue
                if metadata["form_info"].get("chatflow") == "monitoring":
                    pool_id = workload.info.pool_id
                    solution_name = metadata["form_info"].get("Solution name")
                    if not solution_name:
                        continue
                    name = f"{solution_name}"
                    if "grafana" in workload.flist:
                        container_type = "Grafana"
                    elif "redis_zinit" in workload.flist:
                        container_type = "Redis"
                    elif "prometheus" in workload.flist:
                        container_type = "Prometheus"
                    else:
                        continue
                    if name in result:
                        result[name]["wids"].append(workload.id)
                        if workload.volumes:
                            for vol in workload.volumes:
                                result[name]["wids"].append(vol.volume_id.split("-")[0])
                        result[name][f"{container_type} IP"] = workload.network_connection[0].ipaddress
                        result[name][f"{container_type} Pool"] = pool_id
                        for key, value in self.get_workload_capacity(workload).items():
                            result[name][f"{container_type} {key}"] = value
                        continue
                    result[name] = {
                        "wids": [workload.id],
                        "Name": solution_name[len(username) + 1 :],
                        f"{container_type} Pool": pool_id,
                        "Network": workload.network_connection[0].network_id,
                        f"{container_type} IPv4": workload.network_connection[0].ipaddress,
                        f"{container_type} IPv6": self.get_ipv6_address(workload),
                    }
                    for key, value in self.get_workload_capacity(workload).items():
                        result[name][f"{container_type} {key}"] = value
                    if workload.volumes:
                        for vol in workload.volumes:
                            result[name]["wids"].append(vol.volume_id.split("-")[0])
        return list(result.values())

    def list_gitea_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = []
        for container_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Container
        ].values():
            for workload in container_workloads:
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata.get("owner") != username:
                    continue
                if metadata["form_info"].get("chatflow") == "gitea":
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
                    name_to_proxy[f"{name}"] = f"{proxy.info.pool_id}-{proxy.domain}"
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
                if name_to_proxy.get(f"{solution_name}"):
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
                if name_to_proxy.get(f"{solution_name}"):
                    domain = name_to_proxy.get(f"{solution_name}")
                    result[f"{domain}"]["wids"].append(container_workload.id)
        return list(result.values())

    def list_wiki_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self.list_publisher_solutions(username, next_action=next_action, sync=sync, publish_type="wiki")

    def list_blog_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self.list_publisher_solutions(username, next_action=next_action, sync=sync, publish_type="blog")

    def list_website_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        return self.list_publisher_solutions(username, next_action=next_action, sync=sync, publish_type="website")

    def list_publisher_solutions(self, username, next_action=NextAction.DEPLOY, sync=True, publish_type="publisher"):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = {}
        for container_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Container
        ].values():
            for workload in container_workloads:
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata.get("owner") != username:
                    continue
                if metadata["form_info"].get("chatflow") == publish_type:
                    name = metadata.get("name", metadata["form_info"].get("Solution name"))
                    result[name] = {
                        "wids": [workload.id],
                        "Name": name[len(username) + 1 :],
                        "IPv4 Address": workload.network_connection[0].ipaddress,
                        "IPv6 Address": self.get_ipv6_address(workload),
                        "Network": workload.network_connection[0].network_id,
                        "Node": workload.info.node_id,
                        "Pool": workload.info.pool_id,
                    }
                    result[name].update(self.get_workload_capacity(workload))
        for proxy_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Reverse_proxy
        ].values():
            for workload in proxy_workloads:
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata.get("owner") != username:
                    continue
                if metadata["form_info"].get("chatflow") == publish_type:
                    name = metadata.get("name", metadata["form_info"].get("Solution name"))
                    if name in result:
                        result[name]["wids"].append(workload.id)
                        result[name]["Domain"] = workload.domain

        for subdomain_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Subdomain
        ].values():
            for workload in subdomain_workloads:
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata.get("owner") != username:
                    continue
                if metadata["form_info"].get("chatflow") == publish_type:
                    name = metadata.get("name", metadata["form_info"].get("Solution name"))
                    if name in result:
                        result[name]["wids"].append(workload.id)
        return list(result.values())

    def list_peertube_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = {}
        for container_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Container
        ].values():
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
                if metadata["form_info"].get("chatflow") == "peertube":
                    name = metadata.get("name", metadata["form_info"].get("Solution name"))
                    result[name] = {
                        "wids": [workload.id],
                        "Name": name,
                        "IPv4 Address": workload.network_connection[0].ipaddress,
                        "IPv6 Address": self.get_ipv6_address(workload),
                        "Network": workload.network_connection[0].network_id,
                        "Node": workload.info.node_id,
                        "Pool": workload.info.pool_id,
                    }
                    result[name].update(self.get_workload_capacity(workload))
        for proxy_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Reverse_proxy
        ].values():
            for workload in proxy_workloads:
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata.get("owner") != username:
                    continue
                if metadata["form_info"].get("chatflow") == "peertube":
                    name = metadata.get("name", metadata["form_info"].get("Solution name"))
                    if name in result:
                        result[name]["wids"].append(workload.id)
                        result[name]["Domain"] = workload.domain

        for subdomain_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Subdomain
        ].values():
            for workload in subdomain_workloads:
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata.get("owner") != username:
                    continue
                if metadata["form_info"].get("chatflow") == "peertube":
                    name = metadata.get("name", metadata["form_info"].get("Solution name"))
                    if name in result:
                        result[name]["wids"].append(workload.id)
        return list(result.values())

    def list_gollum_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = {}
        for container_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Container
        ].values():
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
                if metadata["form_info"].get("chatflow") == "gollum":
                    name = metadata.get("name", metadata["form_info"].get("Solution name"))
                    result[name] = {
                        "wids": [workload.id],
                        "Name": name,
                        "IPv4 Address": workload.network_connection[0].ipaddress,
                        "IPv6 Address": self.get_ipv6_address(workload),
                        "Network": workload.network_connection[0].network_id,
                        "Node": workload.info.node_id,
                        "Pool": workload.info.pool_id,
                    }
                    result[name].update(self.get_workload_capacity(workload))
        for proxy_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Reverse_proxy
        ].values():
            for workload in proxy_workloads:
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata.get("owner") != username:
                    continue
                if metadata["form_info"].get("chatflow") == "gollum":
                    name = metadata.get("name", metadata["form_info"].get("Solution name"))
                    if name in result:
                        result[name]["wids"].append(workload.id)
                        result[name]["Domain"] = workload.domain

        for subdomain_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Subdomain
        ].values():
            for workload in subdomain_workloads:
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata.get("owner") != username:
                    continue
                if metadata["form_info"].get("chatflow") == "gollum":
                    name = metadata.get("name", metadata["form_info"].get("Solution name"))
                    if name in result:
                        result[name]["wids"].append(workload.id)
        return list(result.values())

    def list_cryptpad_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = {}
        for container_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Container
        ].values():
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
                if metadata["form_info"].get("chatflow") == "cryptpad":
                    name = metadata.get("name", metadata["form_info"].get("Solution name"))
                    result[name] = {
                        "wids": [workload.id],
                        "Name": name,
                        "IPv4 Address": workload.network_connection[0].ipaddress,
                        "IPv6 Address": self.get_ipv6_address(workload),
                        "Network": workload.network_connection[0].network_id,
                        "Node": workload.info.node_id,
                        "Pool": workload.info.pool_id,
                    }
                    result[name].update(self.get_workload_capacity(workload))
        for proxy_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Reverse_proxy
        ].values():
            for workload in proxy_workloads:
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata.get("owner") != username:
                    continue
                if metadata["form_info"].get("chatflow") == "cryptpad":
                    name = metadata.get("name", metadata["form_info"].get("Solution name"))
                    if name in result:
                        result[name]["wids"].append(workload.id)
                        result[name]["Domain"] = workload.domain

        for subdomain_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Subdomain
        ].values():
            for workload in subdomain_workloads:
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata.get("owner") != username:
                    continue
                if metadata["form_info"].get("chatflow") == "cryptpad":
                    name = metadata.get("name", metadata["form_info"].get("Solution name"))
                    if name in result:
                        result[name]["wids"].append(workload.id)
        return list(result.values())

    def list_threebot_solutions(self, username, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = {}

        for container_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Container
        ].values():
            for workload in container_workloads:
                if workload.flist == "https://hub.grid.tf/tf-official-apps/tcprouter:latest.flist":
                    continue
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata.get("owner") != username:
                    continue
                if metadata["form_info"].get("chatflow") == "threebot":
                    name = metadata.get("name", metadata["form_info"].get("Solution name"))
                    result[name] = {
                        "wids": [workload.id],
                        "Name": name,
                        "IPv4 Address": workload.network_connection[0].ipaddress,
                        "IPv6 Address": self.get_ipv6_address(workload),
                        "Network": workload.network_connection[0].network_id,
                        "Node": workload.info.node_id,
                        "Pool": workload.info.pool_id,
                    }
                    result[name].update(self.get_workload_capacity(workload))

        for proxy_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Reverse_proxy
        ].values():
            for workload in proxy_workloads:
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata.get("owner") != username:
                    continue
                if metadata["form_info"].get("chatflow") == "threebot":
                    name = metadata.get("name", metadata["form_info"].get("Solution name"))
                    if name in result:
                        result[name]["wids"].append(workload.id)
                        result[name]["Domain"] = workload.domain

        for subdomain_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Subdomain
        ].values():
            for workload in subdomain_workloads:
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata.get("owner") != username:
                    continue
                if metadata["form_info"].get("chatflow") == "threebot":
                    name = metadata.get("name", metadata["form_info"].get("Solution name"))
                    if name in result:
                        result[name]["wids"].append(workload.id)

        for container_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Container
        ].values():
            for workload in container_workloads:
                if workload.flist != "https://hub.grid.tf/tf-official-apps/tcprouter:latest.flist":
                    continue
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata.get("owner") != username:
                    continue
                if metadata["form_info"].get("chatflow") == "threebot":
                    name = metadata.get("name", metadata["form_info"].get("Solution name"))
                    if name in result:
                        result[name]["wids"].append(workload.id)
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
            "threebot": 0,
            "cryptpad": 0,
            "pools": 0,
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
        return method(username, next_action=NextAction.DEPLOY, sync=True)

    def cancel_solution(self, username, solution_wids):
        valid = True
        for wid in solution_wids:
            workload = j.sals.zos.workloads.get(wid)
            metadata_json = j.sals.reservation_chatflow.deployer.decrypt_metadata(workload.info.metadata)
            metadata = j.data.serializers.json.loads(metadata_json)
            if metadata.get("owner") != username:
                valid = False
                break
        if valid:
            super().cancel_solution(solution_wids)


solutions = MarketplaceSolutions()
