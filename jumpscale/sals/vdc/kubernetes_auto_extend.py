from jumpscale.loader import j
from jumpscale.sals.kubernetes.manager import Manager


class KubernetesMonitor:
    def __init__(self, vdc_instance):
        self.vdc_instance = vdc_instance
        self.manager = Manager()
        self._node_stats = {}

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
        out = self.manager.execute_native_cmd("kubectl top nodes  --no-headers=true")
        for line in out.splitlines():
            splits = line.split()
            if len(splits) != 5:
                continue
            node_name = splits[0]
            cpu_mill = float(splits[1][:-1])
            cpu_percentage = float(splits[2][:-1]) / 100
            memory_usage = float(splits[3][:-2])
            memory_percentage = float(splits[4][:-1]) / 100
            self._node_stats[node_name] = {
                "cpu": {"used": cpu_mill, "total": cpu_mill / cpu_percentage,},
                "memory": {"used": memory_usage, "total": memory_usage / memory_percentage},
            }
        j.logger.info(f"kubernetes stats: {self.node_stats}")

    def is_extend_triggered(self, cpu_threshold=0.7, memory_threshold=0.7):
        total_cpu = used_cpu = total_memory = used_memory = 0
        for stats in self.node_stats.values():
            total_cpu += stats["cpu"]["total"]
            used_cpu += stats["cpu"]["used"]
            total_memory += stats["memory"]["total"]
            used_memory += stats["memory"]["used"]
        overall_cpu_percentage = used_cpu / total_cpu if total_cpu else 0
        overall_memory_percentage = used_memory / total_memory if total_memory else 0
        if any([overall_cpu_percentage >= cpu_threshold, overall_memory_percentage >= memory_threshold,]):
            return True
        return False
