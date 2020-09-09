from gedispatch import GedisChatBotPatch
from jumpscale.packages.tfgrid_solutions.chats.ubuntu import UbuntuDeploy
from time import time


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
    IP_MESSAGE = "Please choose IP Address for your solution"
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
        NETWORK_MESSAGE: "choose_random",
        LOG_MESSAGE: "log",
        IP_MESSAGE: "choose_random",
        IPV6_MESSAGE: "ipv6",
        POOL_MESSAGE: "choose_random",
        NODE_ID_MESSAGE: "node_automatic",
        NODE_SELECTION_MESSAGE: "choose_random",
    }


test = UbuntuAutomated(
    solution_name="ubnutu",
    currency="TFT",
    version="ubuntu-18.04",
    cpu=1,
    memory=1024,
    disk_size=256,
    disk_type="SSD",
    log="NO",
    ssh="~/.ssh/id_rsa.pub",
    ipv6="NO",
    node_automatic="NO",
    debug=True,
)
