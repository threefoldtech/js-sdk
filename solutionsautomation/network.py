from gedispatch import GedisChatBotPatch
from jumpscale.packages.tfgrid_solutions.chats.network import NetworkDeploy

class NetworkDeployAutomated(GedisChatBotPatch, NetworkDeploy):
    CREATE_NETWORK = "Would you like to create a new network, or add access to an existing one?"
    WORKLOAD_NAME = "Please enter a name for your workload (Needed to track your solution on the grid)"
    IP_TYPE = "How would you like to connect to your network? If unsure, choose IPv4"
    NETWORK_IP = "To have access to the 3Bot, the network must be configured"
    NETWORK = "Please select a network"


    QS = {
        CREATE_NETWORK: "type",
        WORKLOAD_NAME: "get_name",
        IP_TYPE: "ip_type",
        NETWORK_IP: "network_ip",
        NETWORK: "choose_random",
    }

    def ask(self, data):
        if(data.get("msg")):
            self.md_show(data.get("msg"))


NetworkDeployAutomated(
    solution_name="network_t",
    type="Create",
    ip_type="IPv4",
    network_ip= "Choose ip range for me",
    debug=True,
)

NetworkDeployAutomated(
    type="Add Access",
    ip_type="IPv4",
    network_ip= "Choose ip range for me",
    debug=True,
)