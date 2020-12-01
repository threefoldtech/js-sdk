from jumpscale.loader import j
from jumpscale.sals.vdc.size import K8SNodeFlavor
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step


class AddK3sNode(GedisChatBot):
    title = "K3s Node"
    steps = ["flavor", "public_ip", "add_node", "success"]

    @chatflow_step(title="Node Flavor")
    def flavor(self):
        node_flavors = [flavor.name for flavor in K8SNodeFlavor]
        self.node_flavor = self.single_choice(
            "Choose the Node Flavor", options=node_flavors, default=node_flavors[0], required=True
        )

    @chatflow_step(title="Public IP")
    def public_ip(self):
        self.public_ip = self.single_choice(
            "Do you want to allow public ip for your node?", options=["No", "Yes"], default="No", required=True
        )

    @chatflow_step(title="Adding node")
    def add_node(self):
        pass

    @chatflow_step(title="Success")
    def success(self):
        pass


chat = AddK3sNode
