from jumpscale.packages.tfgrid_solutions.chats.monitoring import MonitoringDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class MonitoringAutomated(GedisChatBotPatch, MonitoringDeploy):
    NAME_MESSAGE = "Please enter a name for your workload (Can be used to prepare domain for you and needed to track your solution on the grid)"
    SSH_MESSAGE = "Please add your public ssh key, this will allow you to access the deployed containers using ssh."
    CPU = "Please specify how many CPUs"
    MEMORY = "Please specify how much memory (in MB)"
    DISK_SIZE = "Please specify the size of root filesystem (in MB)"
    VOLUME_SIZE = "Please specify the volume size in GiB"
    POOL_RADIS = "Please select a pool for Redis"
    REDIS_NODE_SELECT = "Do you want to automatically select a node for deployment for Redis?"
    POOL_PROMETHEUS = "Please select a pool for Prometheus"
    PROMETHEUS_NODE_SELECT = "Do you want to automatically select a node for deployment for Prometheus?"
    POOL_GRAFANA = "Please select a pool for Grafana"
    GRAFANA_NODE_SELECT = "Do you want to automatically select a node for deployment for Grafana?"
    NETWORK_MESSAGE = "Please select a network"
    IP_REDIS = "Please choose IP Address for Redis"
    IP_PROMETHEUS = "Please choose IP Address for Prometheus"
    IP_GRAFANA = "Please choose IP Address for Grafana"
    REDIS_NODE = "Please choose the node you want to deploy Redis on"
    PROMETHEUS_NODE = "Please choose the node you want to deploy Prometheus on"
    GRAFANA_NODE = "Please choose the node you want to deploy Grafana on"

    QS = {
        NAME_MESSAGE: "get_name",
        SSH_MESSAGE: "ssh",
        CPU: "cpu",
        MEMORY: "memory",
        DISK_SIZE: "disk_size",
        VOLUME_SIZE: "volume_size",
        POOL_RADIS: "redis_pool",
        REDIS_NODE_SELECT: "redis_node_select",
        POOL_PROMETHEUS: "prometheus_pool",
        PROMETHEUS_NODE_SELECT: "prometheus_node_select",
        POOL_GRAFANA: "grafana_pool",
        GRAFANA_NODE_SELECT: "grafana_node_select",
        IP_REDIS: "redis_ip",
        IP_PROMETHEUS: "prometheus_ip",
        IP_GRAFANA: "grafana_ip",
        NETWORK_MESSAGE: "network",
        REDIS_NODE: "redis_node",
        PROMETHEUS_NODE: "prometheus_node",
        GRAFANA_NODE: "grafana_node",
    }

    def single_choice(self, msg, *args, **kwargs):
        selected = self.fetch_param(msg, *args, **kwargs)
        if args:
            for m in args[0]:
                if str(selected) in m:
                    return m
        return selected
