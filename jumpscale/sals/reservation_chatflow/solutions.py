from jumpscale.loader import j
from jumpscale.clients.explorer.models import NextAction, WorkloadType

K8S_SIZES = {1: {"CPU": 1, "Memory": 2048, "Disk Size": "50GiB"}, 2: {"CPU": 2, "Memory": 4096, "Disk Size": "100GiB"}}


class ChatflowSolutions:
    def get_node_farm(self, node_id):
        explorer = j.core.identity.me.explorer
        farm_id = explorer.nodes.get(node_id).farm_id
        return str(explorer.farms.get(farm_id))

    def list_network_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        networks = j.sals.reservation_chatflow.deployer.list_networks(next_action=next_action, sync=sync)
        if not sync and not networks:
            networks = j.sals.reservation_chatflow.deployer.list_networks(next_action=next_action, sync=False)
        result = []
        nodes = {}
        farms = {}
        if networks:
            nodes = {node.node_id: node.farm_id for node in j.sals.zos._explorer.nodes.list()}
            farms = {farm.id: farm.name for farm in j.sals.zos._explorer.farms.list()}
        for n in networks.values():
            if not n.network_workloads:
                continue
            result.append(
                {
                    "Name": n.name,
                    "IP Range": n.network_workloads[-1].network_iprange,
                    "nodes": {
                        res.info.node_id: f"{res.iprange} {farms.get(nodes.get(res.info.node_id))}"
                        for res in n.network_workloads
                    },
                    "wids": [res.id for res in n.network_workloads],
                }
            )
        return result

    def list_ubuntu_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        return self._list_single_container_solution("ubuntu", next_action, sync)

    def list_peertube_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("peertube", next_action, sync, "nginx")

    def list_discourse_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("discourse", next_action, sync, "nginx")

    def list_taiga_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("taiga", next_action, sync, "nginx")

    def list_flist_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        return self._list_single_container_solution("flist", next_action, sync)

    def list_gitea_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("gitea", next_action, sync, "nginx")

    def list_mattermost_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("mattermost", next_action, sync, "nginx")

    def list_publisher_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("publisher", next_action, sync, None)

    def list_wiki_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("wiki", next_action, sync, None)

    def list_blog_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("blog", next_action, sync, None)

    def list_website_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("website", next_action, sync, None)

    def list_threebot_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("threebot", next_action, sync)

    def list_gollum_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        return self._list_single_container_solution("gollum", next_action, sync)

    def list_cryptpad_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        return self._list_proxied_solution("cryptpad", next_action, sync, "nginx")

    def list_minio_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = []
        container_workloads = self._list_container_workloads("minio", next_action)
        for name in container_workloads:
            primary_dict = container_workloads[name][0]
            solution_dict = {
                "wids": [primary_dict["wid"]] + primary_dict["vol_ids"],
                "Name": name,
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

    def list_kubernetes_solutions(self, next_action=NextAction.DEPLOY, sync=True):
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
                name = metadata["form_info"].get("Solution name", metadata.get("name"))
                if name:
                    if name in result:
                        if workload.master_ips:
                            result[name]["wids"].append(workload.id)
                            result[name]["Slave IPs"].append(workload.ipaddress)
                            result[name]["Slave Pools"].append(workload.info.pool_id)
                        continue
                    result[name] = {
                        "wids": [workload.id],
                        "Name": name,
                        "Network": workload.network_id,
                        "Master IP": workload.ipaddress if not workload.master_ips else workload.master_ips[0],
                        "Slave IPs": [],
                        "Slave Pools": [],
                        "Master Pool": workload.info.pool_id,
                    }
                    result[name].update(self.get_workload_capacity(workload))
                    if workload.master_ips:
                        result[name]["Slave IPs"].append(workload.ipaddress)
        return list(result.values())

    def list_monitoring_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = []
        container_workloads = self._list_container_workloads("monitoring", next_action)
        for name in container_workloads:
            if len(container_workloads[name]) != 3:
                continue
            solution_dict = {"wids": [], "Name": name}
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
                solution_dict[f"{cont_type} Farm"] = self.get_node_farm(c_dict["node"])
                solution_dict[f"{cont_type} Pool"] = c_dict["pool"]
                for key, val in c_dict["capacity"].items():
                    solution_dict[f"{cont_type} {key}"] = val
            result.append(solution_dict)
        return result

    def list_4to6gw_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Gateway4to6]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = []
        for gateways in j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Gateway4to6].values():
            for g in gateways:
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

    def list_delegated_domain_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Domain_delegate]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = []
        for domains in j.sals.reservation_chatflow.deployer.workloads[next_action][
            WorkloadType.Domain_delegate
        ].values():
            for dom in domains:
                result.append(
                    {"wids": [dom.id], "Name": dom.domain, "Gateway": dom.info.node_id, "Pool": dom.info.pool_id}
                )
        return result

    def list_exposed_solutions(self, next_action=NextAction.DEPLOY, sync=True):
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
                    name = metadata.get("Solution name", metadata.get("form_info", {}).get("Solution name"))
                    name_to_proxy[name] = f"{proxy.info.pool_id}-{proxy.domain}"
                pools.add(proxy.info.pool_id)

        # link subdomains to proxy_reservations
        for subdomains in j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Subdomain].values():
            for workload in subdomains:
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                chatflow = metadata.get("form_info", {}).get("chatflow")
                if chatflow and chatflow != "exposed":
                    continue
                solution_name = metadata.get(
                    "Solution name", metadata.get("name", metadata.get("form_info", {}).get("Solution name"))
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
                chatflow = metadata.get("form_info", {}).get("chatflow")
                if chatflow and chatflow != "exposed":
                    continue
                solution_name = metadata.get(
                    "Solution name", metadata.get("name", metadata.get("form_info", {}).get("Solution name"))
                )
                if not solution_name:
                    continue
                if name_to_proxy.get(solution_name):
                    domain = name_to_proxy.get(solution_name)
                    result[domain]["wids"].append(container_workload.id)
        return list(result.values())

    def cancel_solution(self, solution_wids):
        """
        solution_wids should be part of the same solution. if they are not created by the same solution they may not all be deleted
        """
        workload = j.sals.zos.workloads.get(solution_wids[0])
        solution_uuid = self.get_solution_uuid(workload)
        ids_to_delete = []
        if solution_uuid:
            # solutions created by new chatflows
            for workload in j.sals.zos.workloads.list(j.core.identity.me.tid, next_action="DEPLOY"):
                if solution_uuid == self.get_solution_uuid(workload):
                    ids_to_delete.append(workload.id)
        else:
            ids_to_delete = solution_wids

        for wid in ids_to_delete:
            j.sals.zos.workloads.decomission(wid)

    def count_solutions(self, next_action=NextAction.DEPLOY):
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
            "threebot": 0,
            "peertube": 0,
            "discourse": 0,
            "gollum": 0,
            "mattermost": 0,
            "peertube": 0,
            "cryptpad": 0,
            "publisher": 0,
            "wiki": 0,
            "blog": 0,
            "website": 0,
            "taiga": 0,
        }
        j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        for key in count_dict.keys():
            method = getattr(self, f"list_{key}_solutions")
            count_dict[key] = len(method(next_action=next_action, sync=False))
        return count_dict

    def get_solution_uuid(self, workload):
        if workload.info.metadata:
            try:
                metadata = j.data.serializers.json.loads(
                    j.sals.reservation_chatflow.deployer.decrypt_metadata(workload.info.metadata)
                )
            except:
                return
            if metadata:
                solution_uuid = metadata.get("solution_uuid")
                return solution_uuid

    def get_ipv6_address(self, workload):
        result = j.data.serializers.json.loads(workload.info.result.data_json)
        if not result:
            result = {}
        return result.get("ipv6")

    def get_workload_capacity(self, workload):
        result = {}
        if workload.info.workload_type == WorkloadType.Container:
            result["CPU"] = workload.capacity.cpu
            result["Memory"] = workload.capacity.memory
            result["RootFS Type"] = workload.capacity.disk_type.name
            result["RootFS Size"] = workload.capacity.disk_size
        elif workload.info.workload_type == WorkloadType.Kubernetes:
            result.update(K8S_SIZES.get(workload.size, {}))
        elif workload.info.workload_type == WorkloadType.Volume:
            result["Size"] = workload.size * 1024
            result["Type"] = workload.type.name
        return result

    def _validate_workload_metadata(self, chatflow, workload):
        if not workload.info.metadata:
            return
        try:
            metadata = j.data.serializers.json.loads(workload.info.metadata)
        except:
            return

        if not metadata.get("form_info"):
            return
        if metadata["form_info"].get("chatflow") != chatflow:
            return

        return metadata

    def _list_container_workloads(
        self,
        chatflow,
        next_action=NextAction.DEPLOY,
        name_identitfier=lambda metadata: metadata.get("name", metadata["form_info"].get("Solution name")),
        metadata_filters=None,
    ):
        """
        Args:
            chatflow: chatflow value set in metadata
            next_action: workload next action
            name_identifier: function with one parameter metadata and returns the solution name
            metadata_filters: list of methods with one parameter metadata and returns True/False. if return is False the workload will be filtered

        Returns:
            {"name": [container_dict]}  # container_dict keys: flist, ipv4, ipv6, capacity, wid, vol_ids, node, pool
        """
        metadata_filters = metadata_filters or []
        result = {}
        values = j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container].values()
        for container_workloads in values:
            for workload in container_workloads:
                metadata = self._validate_workload_metadata(chatflow, workload)
                if not metadata:
                    continue
                valid = True
                for meta_filter in metadata_filters:
                    if not meta_filter(metadata):
                        valid = False
                        break
                if not valid:
                    continue

                name = name_identitfier(metadata)
                container_dict = {
                    "wid": workload.id,
                    "flist": workload.flist,
                    "ipv4": workload.network_connection[0].ipaddress,
                    "ipv6": self.get_ipv6_address(workload),
                    "network": workload.network_connection[0].network_id,
                    "node": workload.info.node_id,
                    "farm": self.get_node_farm(workload.info.node_id),
                    "pool": workload.info.pool_id,
                    "vol_ids": [],
                    "capacity": self.get_workload_capacity(workload),
                    "owner": metadata.get("owner"),
                }
                if workload.volumes:
                    for vol in workload.volumes:
                        container_dict["vol_ids"].append(int(vol.volume_id.split("-")[0]))
                if name not in result:
                    result[name] = [container_dict]
                else:
                    result[name].append(container_dict)
        return result

    def _list_subdomain_workloads(
        self,
        chatflow,
        next_action=NextAction.DEPLOY,
        name_identitfier=lambda metadata: metadata.get("name", metadata["form_info"].get("Solution name")),
        metadata_filters=None,
    ):
        """
        Args:
            chatflow: chatflow value set in metadata
            next_action: workload next action
            name_identifier: function with one parameter metadata and returns the solution name
            metadata_filters: list of methods with one parameter metadata and returns True/False. if return is False the workload will be filtered

        Returns:
            {"name": [subdomain_dict]}  # subdomain_dict keys: wid, domain, ips
        """
        metadata_filters = metadata_filters or []
        result = {}
        values = j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Subdomain].values()
        for subdomain_workloads in values:
            for workload in subdomain_workloads:
                metadata = self._validate_workload_metadata(chatflow, workload)
                if not metadata:
                    continue

                valid = True
                for meta_filter in metadata_filters:
                    if not meta_filter(metadata):
                        valid = False
                        break
                if not valid:
                    continue

                name = name_identitfier(metadata)
                subdomain_dict = {
                    "wid": workload.id,
                    "domain": workload.domain,
                    "ips": workload.ips,
                    "owner": metadata.get("owner"),
                }
                if name not in result:
                    result[name] = [subdomain_dict]
                else:
                    result[name].append(subdomain_dict)
        return result

    def _list_proxy_workloads(
        self,
        chatflow,
        next_action=NextAction.DEPLOY,
        name_identitfier=lambda metadata: metadata.get("name", metadata["form_info"].get("Solution name")),
        metadata_filters=None,
    ):
        """
        Args:
            chatflow: chatflow value set in metadata
            next_action: workload next action
            name_identifier: function with one parameter metadata and returns the solution name
            metadata_filters: list of methods with one parameter metadata and returns True/False. if return is False the workload will be filtered

        Returns:
            {"name": [proxy_dict]}  # subdomain_dict keys: wid, domain
        """
        result = {}
        metadata_filters = metadata_filters or []
        values = j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Reverse_proxy].values()
        for proxy_workloads in values:
            for workload in proxy_workloads:
                metadata = self._validate_workload_metadata(chatflow, workload)
                if not metadata:
                    continue

                valid = True
                for meta_filter in metadata_filters:
                    if not meta_filter(metadata):
                        valid = False
                        break
                if not valid:
                    continue

                name = name_identitfier(metadata)
                proxy_dict = {"wid": workload.id, "domain": workload.domain, "owner": metadata.get("owner")}
                if name not in result:
                    result[name] = [proxy_dict]
                else:
                    result[name].append(proxy_dict)
        return result

    def _list_proxied_solution(
        self, chatflow, next_action=NextAction.DEPLOY, sync=True, proxy_type="tcprouter", owner=None
    ):
        def meta_filter(metadata):
            if metadata.get("owner") != owner:
                return False
            return True

        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = []
        if not proxy_type:
            containers_len = 1
        else:
            containers_len = 2
        if owner:
            container_workloads = self._list_container_workloads(chatflow, next_action, metadata_filters=[meta_filter])
            subdomain_workloads = self._list_subdomain_workloads(chatflow, next_action, metadata_filters=[meta_filter])
            proxy_workloads = self._list_proxy_workloads(chatflow, next_action, metadata_filters=[meta_filter])
        else:
            container_workloads = self._list_container_workloads(chatflow, next_action)
            subdomain_workloads = self._list_subdomain_workloads(chatflow, next_action)
            proxy_workloads = self._list_proxy_workloads(chatflow, next_action)
        for name in container_workloads:
            subdomain_dicts = subdomain_workloads.get(name)
            proxy_dicts = proxy_workloads.get(name)
            if not subdomain_dicts or not proxy_dicts:
                continue
            subdomain_dict = subdomain_dicts[0]
            proxy_dict = proxy_dicts[0]
            sol_name = name
            if owner:
                if len(name) > len(owner) + 1:
                    sol_name = name[len(owner) + 1 :]
            solution_dict = {
                "wids": [subdomain_dict["wid"], proxy_dict["wid"]],
                "Name": sol_name,
                "Domain": subdomain_dict["domain"],
            }
            if chatflow == "threebot":
                solution_dict.update(
                    {"Owner": owner,}
                )
            if len(container_workloads[name]) != containers_len:
                continue
            for c_dict in container_workloads[name]:
                solution_dict["wids"].append(c_dict["wid"])
                if (proxy_type and proxy_type not in c_dict["flist"]) or not proxy_type:
                    pool = j.sals.zos.pools.get(c_dict["pool"])
                    solution_dict.update(
                        {
                            "IPv4 Address": c_dict["ipv4"],
                            "IPv6 Address": c_dict["ipv6"],
                            "Node": c_dict["node"],
                            "Farm": self.get_node_farm(c_dict["node"]),
                            "Pool": c_dict["pool"],
                            "Network": c_dict["network"],
                            "Expiration": pool.empty_at,
                        }
                    )
                    solution_dict.update(c_dict["capacity"])
            result.append(solution_dict)
        return result

    def _list_single_container_solution(self, chatflow, next_action=NextAction.DEPLOY, sync=True, owner=None):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][WorkloadType.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = []
        if owner:
            meta_filter = lambda metadata: False if metadata.get("owner") != owner else True
            container_workloads = self._list_container_workloads(chatflow, next_action, metadata_filters=[meta_filter])
        else:
            container_workloads = self._list_container_workloads(chatflow, next_action)
        for name in container_workloads:
            c_dict = container_workloads[name][0]
            sol_name = name
            if owner:
                if len(name) > len(owner) + 1:
                    sol_name = name[len(owner) + 1 :]
            result.append(
                {
                    "wids": [c_dict["wid"]],
                    "Name": sol_name,
                    "IPv4 Address": c_dict["ipv4"],
                    "IPv6 Address": c_dict["ipv6"],
                    "Node": c_dict["node"],
                    "Farm": self.get_node_farm(c_dict["node"]),
                    "Pool": c_dict["pool"],
                    "Network": c_dict["network"],
                }
            )
            result[-1].update(c_dict["capacity"])
        return result

    def cancel_solution_by_uuid(self, solution_uuid):
        # Get workloads with specific UUID
        for workload in j.sals.zos.workloads.list(j.core.identity.me.tid, next_action="DEPLOY"):
            if solution_uuid == self.get_solution_uuid(workload):
                j.sals.zos.workloads.decomission(workload.id)


solutions = ChatflowSolutions()
