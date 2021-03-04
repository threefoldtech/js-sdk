from jumpscale.loader import j
from jumpscale.sals.vdc.size import VDC_SIZE, INITIAL_RESERVATION_DURATION
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.vdc.deployer import VDCIdentityError


class ExtendKubernetesCluster(GedisChatBot):
    title = "Extend Kubernetes Cluster"
    steps = ["flavor", "add_node", "success"]

    @chatflow_step(title="Node Size")
    def flavor(self):
        self.md_show_update("Checking payment service...")
        # check stellar service
        if not j.clients.stellar.check_stellar_service():
            raise StopChatFlow("Payment service is currently down, try again later")
        self.vdc_name = list(j.sals.vdc.list_all())[0]
        self.user_info_data = self.user_info()
        self.username = self.user_info_data["username"]
        self.vdc = j.sals.vdc.get(name=self.vdc_name)
        if not self.vdc:
            self.stop(f"VDC {self.vdc_name} doesn't exist")

        node_flavors = [VDC_SIZE.K8SNodeFlavor.MEDIUM, VDC_SIZE.K8SNodeFlavor.BIG]
        node_flavor_messages = []
        for flavor in node_flavors:
            plan = VDC_SIZE.K8S_SIZES[flavor]
            node_flavor_messages.append(
                f"{flavor.name}: {plan['cru']} vCPU, {plan['mru']} GB Memory, {plan['sru']} GB SSD storage"
            )

        self.node_flavor = self.single_choice(
            "Choose the Node size", options=node_flavor_messages, default=node_flavor_messages[0], required=True
        )
        self.node_flavor = self.node_flavor.split(":")[0].lower()
        self.public_ip = False

    @chatflow_step(title="Adding node")
    def add_node(self):
        try:
            deployer = self.vdc.get_deployer(bot=self)
        except VDCIdentityError:
            self.stop(
                f"Couldn't verify VDC secret. please make sure you are using the correct secret for VDC {self.vdc_name}"
            )

        success, _, payment_id = self.vdc.show_external_node_payment(self, self.node_flavor, public_ip=self.public_ip)
        if not success:
            self.stop(f"payment timedout")

        self.md_show_update("Payment successful")
        old_wallet = deployer._set_wallet(self.vdc.prepaid_wallet.instance_name)
        try:
            wids = deployer.add_k8s_nodes(self.node_flavor, public_ip=self.public_ip)
        except Exception as e:
            j.sals.billing.issue_refund(payment_id)
            self.stop(f"failed to add nodes to your cluster. due to error {str(e)}")

        self.md_show_update("Processing transaction...")
        deployer._set_wallet(old_wallet)

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        self.md_show(f"""Your VDC {self.vdc.vdc_name} has been extended successfuly""")


chat = ExtendKubernetesCluster
