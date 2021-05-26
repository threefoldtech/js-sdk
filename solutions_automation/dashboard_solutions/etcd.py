from jumpscale.packages.tfgrid_solutions.chats.etcd import EtcdDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class EtcdAutomated(GedisChatBotPatch, EtcdDeploy):
    NAME_MESSAGE = "Please enter a name for your workload (Can be used to prepare domain for you and needed to track your solution on the grid)"
    ETCD_NODES = "Enter number of etcd nodes"
    CPU_MESSAGE = "Please specify how many CPUs"
    MEM_MESSAGE = "Please specify how much memory (in MB)"
    DISK_SIZE_MESSAGE = "Please specify the size of root filesystem (in MB)"
    POOL_MESSAGE = "Please select a pool"
    NETWORK_MESSAGE = "Please select a network to connect your solution to"
    IPv6 = "Do you want to assign a global IPv6 address to your workload?"
    NODE_ID_MESSAGE = "Do you want to automatically select a node to deploy your workload on?"
    ADDRESS_ETCD_NODE = r"Please choose IP Address for ETCD Node (.*)$"

    QS = {
        # strs
        NAME_MESSAGE: "get_name",
        ADDRESS_ETCD_NODE: "address_etcd_node",
        # ints
        ETCD_NODES: "etcd_nodes",
        CPU_MESSAGE: "cpu",
        MEM_MESSAGE: "memory",
        DISK_SIZE_MESSAGE: "disk_size",
        # single choice
        POOL_MESSAGE: "pool",
        NETWORK_MESSAGE: "network",
        IPv6: "ipv6",
        NODE_ID_MESSAGE: "node_automatic",
    }

    def single_choice(self, msg, *args, **kwargs):
        selected = self.fetch_param(msg, *args, **kwargs)
        if args:
            for m in args[0]:
                if str(selected) in m:
                    return m
        return selected
