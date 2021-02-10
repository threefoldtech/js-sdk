from jumpscale.packages.tfgrid_solutions.chats.network import NetworkDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class NetworkDeployAutomated(GedisChatBotPatch, NetworkDeploy):
    NETWORK_TYPE = "Would you like to create a new network, or add access to an existing one?"
    WORKLOAD_NAME = "Please enter a name for your workload (Needed to track your solution on the grid)"
    IP_VERSION = "How would you like to connect to your network? If unsure, choose IPv4"
    IP_SELECT = "How would you like to configure the network IP range"
    IP_RANGE = "Please add private IP Range of the network"
    ACCESS_NODE = "Please select an access node or leave it empty to automatically select it"
    NETWORK_NAME = "Please select a network"
    POOL = "Please select a pool or leave it empty to automaically select it"

    QS = {
        NETWORK_TYPE: "type",
        WORKLOAD_NAME: "get_name",
        IP_VERSION: "ip_version",
        IP_SELECT: "ip_select",
        IP_RANGE: "ip_range",
        ACCESS_NODE: "access_node",
        NETWORK_NAME: "network_name",
        POOL: "pool",
    }

    def ask(self, data):
        if data.get("msg"):
            self.md_show(data.get("msg"))
