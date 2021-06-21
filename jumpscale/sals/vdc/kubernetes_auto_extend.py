from collections import defaultdict
from jumpscale.loader import j
from jumpscale.sals.kubernetes.manager import Manager
from .size import INITIAL_RESERVATION_DURATION, VDC_SIZE
import re
import os


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
        self._memory_unit_to_Mi = {
            "Ki": lambda x: x / 1024,
            "Mi": lambda x: x,
            "Gi": lambda x: x * 1024,
            "Ti": lambda x: x * 1024 * 1024,
        }

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
        nodes_capacity = sorted(self.get_nodes_capacity(), key=lambda x: x["node_name"])
        nodes_allocated = sorted(self.get_allocated_requests_resources(), key=lambda x: x["node_name"])

        assert len(nodes_capacity) == len(nodes_allocated)  # To avoid code execution in case of race condition
        for i in range(len(nodes_capacity)):
            self._node_stats[nodes_capacity[i]["node_name"]] = {
                "cpu": {"total": nodes_capacity[i]["cpu"], "used": nodes_allocated[i]["cpu"]},
                "memory": {"total": nodes_capacity[i]["memory"], "used": nodes_allocated[i]["memory"]},
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

    def get_nodes_capacity(self):
        """Return the capacity of nodes (CPU and Memory)

        Returns:
            list: of dictionaries, each with keys: node_name, cpu, memory
        """
        out = self.manager.execute_native_cmd("kubectl get nodes -o json")
        result_dict = j.data.serializers.json.loads(out)
        nodes_capacity = []
        for node in result_dict["items"]:
            capacity = {}
            capacity["node_name"] = node["metadata"]["name"]
            # int(re.compile("(\d+)").match('12//').group(1))
            cpu_str = node["status"]["capacity"]["cpu"]  # core
            capacity["cpu"] = int(cpu_str) * 1000  # mcore
            capacity["memory"] = self._parse_memory_in_Mi(
                node["status"]["capacity"]["memory"]
            )  # in Ki (# make sure kuberenets always return mem in Ki)
            nodes_capacity.append(capacity)
        return nodes_capacity

    def get_allocated_requests_resources(self):
        """Return the allocated requests of nodes (CPU and Memory)

        Returns:
            list: of dictionaries, each with keys: node_name, cpu, memory
        """
        out = self.manager.execute_native_cmd("kubectl describe nodes")
        nodes_list = out.split(os.linesep * 2)
        nodes_allocated_requests = []
        for node_info in nodes_list:
            allocated_requests = {}
            allocated_requests["node_name"] = re.search(r"Name:\s*([^\n\r]*)", node_info).group(1)
            allocated_resources = re.search(r"(?<=Allocated resources:)[\s\S]*(?=Event)", node_info).group()
            cpu_str = re.search(r"cpu\s*([^\n\r]\S*)", allocated_resources).group(1)
            if not cpu_str.endswith("m"):
                cpu = int(cpu_str) * 1000
            else:
                cpu = int(cpu_str.rstrip("m"))
            allocated_requests["cpu"] = cpu
            memory_str = re.search(r"memory\s*([^\n\r]\S*)", allocated_resources).group(1)
            allocated_requests["memory"] = self._parse_memory_in_Mi(memory_str)
            nodes_allocated_requests.append(allocated_requests)
        return nodes_allocated_requests

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
        result = []
        self.update_stats()
        for node_name, node_dict in self.node_stats.items():
            if node_name in exclude_nodes:
                continue
            result.append(
                NodeReservation(
                    name=node_name,
                    reserved_cpu=node_dict["cpu"]["used"],
                    reserved_memory=node_dict["memory"]["used"],
                    total_cpu=node_dict["cpu"]["total"],
                    total_memory=node_dict["memory"]["total"],
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

    def _parse_memory_in_Mi(self, memory):
        if memory == "0":
            return 0
        mem_value, mem_unit = int(memory[:-2]), memory[-2:]
        return self._memory_unit_to_Mi[mem_unit](mem_value)
