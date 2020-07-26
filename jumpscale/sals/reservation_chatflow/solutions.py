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

    def list_ubuntu_solutions(self, next_action=NextAction.DEPLOY, sync=True):
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
                if metadata["form_info"].get("chatflow") == "ubuntu":
                    result.append(
                        {
                            "wids": [workload.id],
                            "Name": metadata.get("name", metadata["form_info"].get("Solution name")),
                            "IP Address": workload.network_connection[0].ipaddress,
                            "Network": workload.network_connection[0].network_id,
                            "Node": workload.info.node_id,
                            "Pool": workload.info.pool_id,
                        }
                    )
        return result

    def list_kubernetes_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][Type.Kubernetes]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = {}
        for kube_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][Type.Kubernetes].values():
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
                    if f"{name}" in result:
                        if len(workload.master_ips) != 0:
                            result[f"{name}"]["wids"].append(workload.id)
                            result[f"{name}"]["Slave IPs"].append(workload.ipaddress)
                        continue
                    result[f"{name}"] = {
                        "wids": [workload.id],
                        "Name": name,
                        "Network": workload.network_id,
                        "Master IP": workload.ipaddress if len(workload.master_ips) == 0 else workload.master_ips[0],
                        "Slave IPs": [],
                        "Pool": workload.info.pool_id,
                    }
                    if len(workload.master_ips) != 0:
                        result[f"{name}"]["Slave IPs"].append(workload.ipaddress)
        return list(result.values())

    def list_minio_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        # TODO: add related ZDB wids to solution dict
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][Type.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = {}
        for container_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][Type.Container].values():
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
                if metadata["form_info"].get("chatflow") == "minio":
                    name = metadata["form_info"].get("Solution name", metadata.get("name"))
                    if name:
                        if f"{name}" in result:
                            result[f"{name}"]["wids"].append(workload.id)
                            result[f"{name}"]["Secondary IP"] = workload.network_connection[0].ipaddress
                            result[f"{name}"]["Secondary Node"] = workload.network_connection[0].ipaddress
                            if workload.volumes:
                                for vol in workload.volumes:
                                    result[f"{name}"]["wids"].append(vol.volume_id.split("-")[0])
                            continue
                        result[f"{name}"] = {
                            "wids": [workload.id],
                            "Name": name,
                            "Network": workload.network_connection[0].network_id,
                            "Primary IP": workload.network_connection[0].ipaddress,
                            "Primary Node": workload.info.node_id,
                            "Pool": workload.info.pool_id,
                        }
                        if workload.volumes:
                            for vol in workload.volumes:
                                result[f"{name}"]["wids"].append(vol.volume_id.split("-")[0])
        return list(result.values())

    def list_monitoring_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][Type.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = {}
        for container_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][Type.Container].values():
            for workload in container_workloads:
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
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
                        continue
                    result[name] = {
                        "wids": [workload.id],
                        "Name": solution_name,
                        "Pool": pool_id,
                        "Network": workload.network_connection[0].network_id,
                        f"{container_type} IP": workload.network_connection[0].ipaddress,
                    }
                    if workload.volumes:
                        for vol in workload.volumes:
                            result[name]["wids"].append(vol.volume_id.split("-")[0])
        return list(result.values())

    def list_flist_solutions(self, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        if not sync and not j.sals.reservation_chatflow.deployer.workloads[next_action][Type.Container]:
            j.sals.reservation_chatflow.deployer.load_user_workloads(next_action=next_action)
        result = []
        for container_workloads in j.sals.reservation_chatflow.deployer.workloads[next_action][Type.Container].values():
            for workload in container_workloads:
                if not workload.info.metadata:
                    continue
                metadata = j.data.serializers.json.loads(workload.info.metadata)
                if not metadata:
                    continue
                if not metadata.get("form_info"):
                    continue
                if metadata["form_info"].get("chatflow") == "flist":
                    solution_dict = {
                        "wids": [workload.id],
                        "Name": metadata.get("name", metadata["form_info"].get("Solution name")),
                        "IP Address": workload.network_connection[0].ipaddress,
                        "Network": workload.network_connection[0].network_id,
                        "Node": workload.info.node_id,
                        "Pool": workload.info.pool_id,
                    }
                    if workload.volumes:
                        for vol in workload.volumes:
                            solution_dict["wids"].append(vol.volume_id.split("-")[0])
                    result.append(solution_dict)
        return result

    def cancel_solution(self, solution_wids):
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


solutions = ChatflowSolutions()
