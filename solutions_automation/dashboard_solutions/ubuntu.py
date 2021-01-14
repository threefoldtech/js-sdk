from jumpscale.packages.tfgrid_solutions.chats.ubuntu import UbuntuDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class UbuntuAutomated(GedisChatBotPatch, UbuntuDeploy):
    NAME_MESSAGE = "Please enter a name for your workload (Can be used to prepare domain for you and needed to track your solution on the grid)"
    VERSION_MESSAGE = "Please choose ubuntu version"
    CPU_MESSAGE = "Please specify how many CPUs"
    MEM_MESSAGE = "Please specify how much memory (in MB)"
    DISK_SIZE_MESSAGE = "Please specify the size of root filesystem (in MB)"
    DISK_TYPE_MESSAGE = "Please choose the root filesystem disktype"
    NETWORK_MESSAGE = "Please select a network"
    LOG_MESSAGE = "Do you want to push the container logs (stdout and stderr) onto an external redis channel"
    SSH_MESSAGE = "Please upload your public SSH key to be able to access the depolyed container via ssh"
    IPV4_MESSAGE = "Please choose IP Address for your solution"
    IPV6_MESSAGE = r"^Do you want to assign a global IPv6 address to (.*)\?$"
    NODE_ID_MESSAGE = r"^Do you want to automatically select a node for deployment for (.*)\?$"
    POOL_MESSAGE = r"^Please select a pool( for (.*))?$"
    NODE_SELECTION_MESSAGE = r"^Please choose the node you want to deploy (.*) on$"

    QS = {
        # strs
        NAME_MESSAGE: "get_name",
        SSH_MESSAGE: "ssh",
        # ints
        CPU_MESSAGE: "cpu",
        MEM_MESSAGE: "memory",
        DISK_SIZE_MESSAGE: "disk_size",
        # single choice
        VERSION_MESSAGE: "version",
        DISK_TYPE_MESSAGE: "disk_type",
        NETWORK_MESSAGE: "network",
        LOG_MESSAGE: "log",
        IPV4_MESSAGE: "ipv4",
        IPV6_MESSAGE: "ipv6",
        POOL_MESSAGE: "pool",
        NODE_ID_MESSAGE: "node_automatic",
        NODE_SELECTION_MESSAGE: "node",
    }

    def single_choice(self, msg, *args, **kwargs):
        selected = self.fetch_param(msg, *args, **kwargs)
        print(args)
        if args:
            for m in args[0]:
                if str(selected) in m:
                    return m
        return selected
