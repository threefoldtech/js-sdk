from jumpscale.loader import j
from jumpscale.sals.vdc.size import VDC_SIZE, INITIAL_RESERVATION_DURATION
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.vdc.deployer import VDCIdentityError


class ExtendKubernetesCluster(GedisChatBot):
    title = "Extend Kubernetes Cluster"
    steps = ["flavor", "use_public_ip", "add_node", "success"]

    @chatflow_step(title="Node Flavor")
    def flavor(self):
        self.md_show_update("Checking payment service...")
        # check stellar service
        if not j.clients.stellar.check_stellar_service():
            raise StopChatFlow("Payment service is currently down, try again later")
        self.vdc_name = self.kwargs["vdc_name"]
        self.user_info_data = self.user_info()
        self.username = self.user_info_data["username"]
        self.vdc = j.sals.vdc.find(vdc_name=self.vdc_name, owner_tname=self.username)
        if not self.vdc:
            self.stop(f"VDC {self.vdc_name} doesn't exist")
        node_flavors = [flavor.name for flavor in VDC_SIZE.K8SNodeFlavor]
        self.node_flavor = self.single_choice(
            "Choose the Node Flavor", options=node_flavors, default=node_flavors[0], required=True
        )

    @chatflow_step(title="Public IP")
    def use_public_ip(self):
        self.public_ip = self.single_choice(
            "Do you want to allow public ip for your node?", options=["No", "Yes"], default="No", required=True
        )
        if self.public_ip == "Yes":
            self.public_ip = True
        else:
            self.public_ip = False

    @chatflow_step(title="Adding node")
    def add_node(self):
        vdc_secret = self.secret_ask(f"Specify your VDC secret for {self.vdc_name}", min_length=8, required=True,)
        try:
            deployer = self.vdc.get_deployer(password=vdc_secret, bot=self)
        except VDCIdentityError:
            self.stop(
                f"Couldn't verify VDC secret. please make sure you are using the correct secret for vdc {self.vdc_name}"
            )

        transaction_hash, amount = self.vdc.show_external_node_payment(self, self.node_flavor, expiry=1)
        if not transaction_hash:
            self.stop(f"payment timedout")

        self.md_show_update("Payment successful")
        initialization_wallet_name = j.core.config.get("VDC_INITIALIZATION_WALLET")
        old_wallet = deployer._set_wallet(initialization_wallet_name)
        wids = deployer.add_k8s_nodes(self.node_flavor, public_ip=self.public_ip)
        if not wids:
            self.vdc.refund_payment(transaction_hash, amount=amount)
            self.stop("failed to add nodes to your cluster. please contact support")
        self.md_show_update("processing tansaction...")
        initial_transaction_hashes = deployer.transaction_hashes
        self.vdc.transfer_to_provisioning_wallet(amount / 2)
        if initialization_wallet_name:
            self.vdc.pay_initialization_fee(initial_transaction_hashes, initialization_wallet_name)
        deployer._set_wallet(old_wallet)
        self.md_show_update(f"updating pool expiration...")
        deployer.extend_k8s_workloads(14 - (INITIAL_RESERVATION_DURATION / 24), *wids)

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        self.md_show(f"""# You VDC {self.vdc_name} has been extended successfuly""")


chat = ExtendKubernetesCluster
