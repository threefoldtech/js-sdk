from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.vdc.deployer import VDCIdentityError
from jumpscale.sals.vdc.scheduler import CapacityChecker, GlobalCapacityChecker
from jumpscale.sals.vdc.size import VDC_SIZE


class ExtendKubernetesCluster(GedisChatBot):
    title = "Extend Kubernetes Cluster"
    steps = ["flavor", "add_node", "different_farm", "select_farm", "success"]

    @chatflow_step(title="Node Size")
    def flavor(self):
        self.md_show_update("Checking payment service...")
        # check stellar service
        if not j.clients.stellar.check_stellar_service():
            raise StopChatFlow("Payment service is currently down, try again later")
        self.vdc_name = list(j.sals.vdc.list_all())[0]
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

    @property
    def old_node_ids(self):
        old_node_ids = []
        for k8s_node in self.vdc.kubernetes:
            old_node_ids.append(k8s_node.node_id)
        return old_node_ids

    @chatflow_step(title="Farm Selection")
    def different_farm(self):
        self.diff_farm = False
        diff_farm = self.single_choice(
            "Do you want to deploy this node on different farm", options=["Yes", "No"], default="No", required=True
        )
        if diff_farm == "Yes":
            self.diff_farm = True

    @chatflow_step(title="Farm selection")
    def select_farm(self):
        self.farm_name = None
        if self.diff_farm:
            gcc = GlobalCapacityChecker()
            gcc.exclude_nodes(*self.old_node_ids)
            node_flavor_size = VDC_SIZE.K8SNodeFlavor[self.node_flavor.upper()]
            farms_names = gcc.get_available_farms(**VDC_SIZE.K8S_SIZES[node_flavor_size])
            if not farms_names:
                self.stop(f"There's no enough capacity for kubernetes node of flavor {self.node_flavor}")
            self.farm_name = self.single_choice("Choose a farm to deploy on", options=farms_names, required=True)

    @chatflow_step(title="Adding node")
    def add_node(self):
        try:
            self.vdc.load_info()
            deployer = self.vdc.get_deployer(bot=self)
        except VDCIdentityError:
            self.stop(
                f"Couldn't verify VDC secret. please make sure you are using the correct secret for VDC {self.vdc_name}"
            )
        # check for capacity before deploying
        if not self.farm_name:
            self.farm_name = j.sals.marketplace.deployer.get_pool_farm_name(self.vdc.kubernetes[0].pool_id)
        cc = CapacityChecker(self.farm_name)
        cc.exclude_nodes(*self.old_node_ids)
        node_flavor_size = VDC_SIZE.K8SNodeFlavor[self.node_flavor.upper()]
        if not cc.add_query(**VDC_SIZE.K8S_SIZES[node_flavor_size]):
            self.stop(
                f"There's no enough capacity in farm {self.farm_name} for kubernetes node of flavor {self.node_flavor}"
            )
        j.logger.debug("found enough capacity, continue to payment")

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
