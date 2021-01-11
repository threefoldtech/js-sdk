from jumpscale.loader import j
from jumpscale.sals.kubernetes.manager import Manager
from .size import INITIAL_RESERVATION_DURATION, VDC_SIZE


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
                j.logger.warning(f"k8s monitor: failed to get node: {node_name} usage due to error: {e}")
                continue
            self._node_stats[node_name] = {
                "cpu": {"used": cpu_mill, "total": cpu_mill / cpu_percentage,},
                "memory": {"used": memory_usage, "total": memory_usage / memory_percentage},
            }
        out = self.manager.execute_native_cmd("kubectl get nodes -o wide -o json")
        result_dict = j.data.serializers.json.loads(out)
        ip_to_wid = {node.ip_address: node.wid for node in self.nodes}
        for node in result_dict["items"]:
            node_name = node["metadata"]["labels"]["k3s.io/hostname"]
            node_ip = node["metadata"]["annotations"]["flannel.alpha.coreos.com/public-ip"]
            if not node_name in self._node_stats:
                continue
            self._node_stats[node_name]["wid"] = ip_to_wid.get(node_ip)
        j.logger.info(f"kubernetes stats: {self.node_stats}")
        self.stats_history.update(self._node_stats)

    def is_extend_triggered(self, cpu_threshold=0.7, memory_threshold=0.7):
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

    def extend(self, flavor=None, deployer=None, farm_name=None, no_nodes=None, force=False):
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
        deployer = deployer or self.vdc_instance.get_deployer()
        deployer._set_wallet(self.vdc_instance.prepaid_wallet.instance_name)
        wids = deployer.add_k8s_nodes(flavor, farm_name, no_nodes=no_nodes)
        deployer._set_wallet(self.vdc_instance.provision_wallet.instance_name)
        deployer.extend_k8s_workloads(14 - (INITIAL_RESERVATION_DURATION / 24))
        return wids
