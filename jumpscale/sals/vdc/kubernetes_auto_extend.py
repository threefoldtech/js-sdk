from collections import defaultdict
from jumpscale.loader import j
from jumpscale.sals.kubernetes.manager import Manager
from .size import INITIAL_RESERVATION_DURATION, VDC_SIZE
import re


class StatsHistory:
    def __init__(self, vdc_instance, rotation_len=5):
        self.client = j.clients.redis.get(vdc_instance.vdc_name)
        self.key = f"{vdc_instance.vdc_name}_K8S_STATS"
        self.rotation_len = rotation_len

    def update(self, node_stats):
        self.client.lpush(self.key, j.data.serializers.json.dumps(node_stats))
        self.client.ltrim(self.key, 0, self.rotation_len - 1)

    def get(self):
        items = self.client.lrange(self.key, 0, self.rotation_len - 1)
        return [j.data.serializers.json.loads(item.decode()) for item in items]


class NodeReservation:
    def __init__(self, name, reserved_cpu, reserved_memory, total_cpu, total_memory):
        self.name = name
        self.reserved_cpu = reserved_cpu
        self.reserved_memory = reserved_memory
        self.total_cpu = total_cpu
        self.total_memory = total_memory

    @property
    def free_memory(self):
        return self.total_memory - self.reserved_memory

    @property
    def free_cpu(self):
        return self.total_cpu - self.reserved_cpu

    def has_enough_resources(self, cpu, memory):
        if self.free_memory < memory:
            return False
        if self.free_cpu < cpu:
            return False
        return True

    def update(self, cpu, memory):
        self.reserved_cpu += cpu
        self.reserved_memory += memory


class KubernetesMonitor:
    def __init__(self, vdc_instance, burst_size=5):
        self.vdc_instance = vdc_instance
        self.burst_size = burst_size
        self.manager = Manager()
        self._node_stats = {}
        self.stats_history = StatsHistory(self.vdc_instance, burst_size)

    @property
    def nodes(self):
        if not self.vdc_instance.kubernetes:
            self.vdc_instance.load_info()
        return self.vdc_instance.kubernetes

    @property
    def node_stats(self):
        if not self._node_stats:
            self.update_stats()
        return self._node_stats

    def update_stats(self):
        self.vdc_instance.load_info()
        out = self.manager.execute_native_cmd("kubectl top nodes  --no-headers=true")
        for line in out.splitlines():
            splits = line.split()
            if len(splits) != 5:
                continue
            node_name = splits[0]
            try:
                cpu_mill = float(splits[1][:-1])
                cpu_percentage = float(splits[2][:-1]) / 100
                memory_usage = float(splits[3][:-2])
                memory_percentage = float(splits[4][:-1]) / 100
            except Exception as e:
                j.logger.warning(
                    f"k8s monitor: failed to get node: {node_name} usage due to error: {e}, vdc uuid: {self.vdc_instance.solution_uuid}"
                )
                cpu_mill = cpu_percentage = memory_usage = memory_percentage = 0

            cpu_percentage = cpu_percentage or 1 / 100
            memory_percentage = memory_percentage or 1 / 100
            self._node_stats[node_name] = {
                "cpu": {"used": cpu_mill, "total": cpu_mill / cpu_percentage},
                "memory": {"used": memory_usage, "total": memory_usage / memory_percentage},
            }
        out = self.manager.execute_native_cmd("kubectl get nodes -o wide -o json")
        result_dict = j.data.serializers.json.loads(out)
        ip_to_wid = {node.ip_address: node.wid for node in self.nodes}
        for node in result_dict["items"]:
            node_name = node["metadata"]["labels"].get("kubernetes.io/hostname")
            node_ip = node["metadata"]["annotations"].get("flannel.alpha.coreos.com/public-ip")
            if (not node_name and node_name not in self._node_stats) or not node_ip:
                continue
            self._node_stats[node_name]["wid"] = ip_to_wid.get(node_ip)
        j.logger.info(f"Kubernetes stats: {self.node_stats}")
        self.stats_history.update(self._node_stats)

    def is_extend_triggered(self, cpu_threshold=0.7, memory_threshold=0.7):
        if self._is_usage_triggered(cpu_threshold, memory_threshold):
            return True
        else:
            reserved_cpu = reserved_memory = 0.0
            total_cpu = total_memory = 0.0
            for node in self.fetch_resource_reservations():
                total_cpu += node.total_cpu
                total_memory += node.total_memory
                reserved_cpu += node.reserved_cpu
                reserved_memory += node.reserved_memory
            total_cpu = total_cpu or 1.0
            total_memory = total_memory or 0.1
            if any([(reserved_cpu / total_cpu) >= cpu_threshold, (reserved_memory / total_memory) >= memory_threshold]):
                return True
        return False

    def _is_usage_triggered(self, cpu_threshold, memory_threshold):
        burst_usage = []
        stats_history = self.stats_history.get()
        if len(stats_history) < self.burst_size:
            return False
        for h_dict in stats_history:
            total_cpu = used_cpu = total_memory = used_memory = 0
            for stats in h_dict.values():
                total_cpu += stats["cpu"]["total"]
                used_cpu += stats["cpu"]["used"]
                total_memory += stats["memory"]["total"]
                used_memory += stats["memory"]["used"]
            overall_cpu_percentage = used_cpu / total_cpu if total_cpu else 0
            overall_memory_percentage = used_memory / total_memory if total_memory else 0
            burst_usage.append({"cpu": overall_cpu_percentage, "memory": overall_memory_percentage})
        j.logger.info(f"burst stats: {burst_usage}")
        for usage_dict in burst_usage:
            if all([usage_dict["cpu"] < cpu_threshold, usage_dict["memory"] < memory_threshold]):
                return False
        return True

    def has_enough_resources(self, cpu=0, memory=0):
        self.update_stats()
        for stats in self.node_stats.values():
            if all(
                [
                    stats["memory"]["total"] - stats["memory"]["used"] > memory,
                    stats["cpu"]["total"] - stats["cpu"]["used"] > cpu,
                ]
            ):
                return True
        return False

    def extend(self, flavor=None, deployer=None, farm_name=None, no_nodes=None, force=False, bot=None):
        """
        used to extend the vdc k8s cluster according to the vdc spec
        Args:
            flavor: used to override the default k8s size in the vdc spec
            deployer: pass a custom deployer if none it will use the vdc's get_deployer()
            farm_name: farm to deploy on
            no_nodes: no_nodes to extend. defaults to the nodes remaining in the vdc spec. must use force flag to override
            force: if True it will force the extension with the specified no_nodes regardless of the vdc spec

        Returns:
            wids
        """
        current_spec = self.vdc_instance.get_current_spec()
        if not force:
            if current_spec["no_nodes"] < 1:
                return []
            no_nodes = 1

        flavor = flavor or VDC_SIZE.VDC_FLAVORS[self.vdc_instance.flavor]["k8s"]["size"]
        no_nodes = no_nodes or current_spec["no_nodes"]
        if no_nodes < 1:
            return []
        deployer = deployer or self.vdc_instance.get_deployer(bot=bot)
        farm_name, capacity_check = self.vdc_instance.find_worker_farm(flavor, farm_name)
        if not capacity_check:
            j.logger.warning(f"There is no capacity to add worker node")
        duration = self.vdc_instance.get_pools_expiration() - j.data.time.utcnow().timestamp
        two_weeks = 2 * 7 * 24 * 60 * 60
        if duration > two_weeks:
            duration = two_weeks
        wids = deployer.add_k8s_nodes(flavor, farm_name, no_nodes=no_nodes, external=False)
        deployer.extend_k8s_workloads(duration, *wids)
        return wids

    def fetch_resource_reservations(self, exclude_nodes=None):
        exclude_nodes = exclude_nodes or []
        out = self.manager.execute_native_cmd("kubectl get pod -A -o json")
        result = j.data.serializers.json.loads(out)
        node_reservations = defaultdict(lambda: {"cpu": 0.0, "memory": 0.0, "total_cpu": 0.0, "total_memory": 0.0})
        for pod in result["items"]:
            cpu = memory = 0
            if not "nodeName" in pod["spec"]:
                continue
            node = pod["spec"]["nodeName"]
            for cont in pod["spec"]["containers"]:
                cont_requests = cont["resources"].get("requests", {})
                cpu_str = cont_requests.get("cpu", "0m")
                if not cpu_str.endswith("m"):
                    cpu += float(cpu_str) * 1000
                else:
                    cpu += float(cpu_str.split("m")[0])
                p = re.search(r"^([0-9]*)(.*)$", cont_requests.get("memory", "0Gi"))
                memory = float(p.group(1))
                memory_unit = p.group(2)
                if memory_unit == "Gi":
                    memory *= 1024
            node_reservations[node]["cpu"] += cpu
            node_reservations[node]["memory"] += memory

        result = []
        for node_name, resv in node_reservations.items():
            if node_name not in self.node_stats or node_name in exclude_nodes:
                continue
            node_reservations[node_name]["total_cpu"] = self.node_stats[node_name]["cpu"]["total"]
            node_reservations[node_name]["total_memory"] = self.node_stats[node_name]["memory"]["total"]
            result.append(
                NodeReservation(
                    name=node_name,
                    reserved_cpu=resv["cpu"],
                    reserved_memory=resv["memory"],
                    total_cpu=resv["total_cpu"],
                    total_memory=resv["total_memory"],
                )
            )
        return result

    def check_deployment_resources(self, queries: list):
        """
        check if the cluster has enough resources for the queries specified

        Args:
            queries (list): list of dicts containing cpu, memory of the deployment
        """
        node_reservations = self.fetch_resource_reservations()
        for query in queries:
            query_result = False
            node_reservations = sorted(node_reservations, key=lambda resv: resv.free_memory)
            for node in node_reservations:
                if node.has_enough_resources(cpu=query.get("cpu", 0), memory=query.get("memory", 0)):
                    query_result = True
                    node.update(cpu=query.get("cpu", 0), memory=query.get("memory", 0))
                    break
            if not query_result:
                return False
        return True
