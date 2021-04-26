from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.vdc.deployer import VDCIdentityError
from jumpscale.sals.vdc.scheduler import CapacityChecker, GlobalCapacityChecker
from jumpscale.sals.vdc.size import VDC_SIZE


class ExtendKubernetesCluster(GedisChatBot):
    title = "Extend Kubernetes Cluster"
    steps = ["flavor", "different_farm", "select_farm", "add_node", "success"]

    @chatflow_step(title="Node Size")
    def flavor(self):
        self.md_show_update("Checking payment service...")
        # check stellar service
        if not j.clients.stellar.check_stellar_service():
            raise StopChatFlow("Payment service is currently down, try again later")
        if not j.sals.vdc.list_all():
            self.stop("Couldn't find any vdcs on this machine, Please make sure to have it configured properly")
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
        form = self.new_form()
        self.node_flavor = form.single_choice(
            "Choose the Node size", options=node_flavor_messages, default=node_flavor_messages[0], required=True
        )
        self.node_public = form.single_choice(
            "Do you want the added node with public IP?", options=["Yes", "No"], default="No", required=True
        )
        form.ask()
        self.node_flavor = self.node_flavor.value.split(":")[0].lower()
        self.public_ip = False
        if self.node_public.value == "Yes":
            self.public_ip = True

    @chatflow_step(title="Farm Selection")
    def different_farm(self):
        self.diff_farm = False
        diff_farm = self.single_choice(
            "Do you want to deploy this node on a different farm?", options=["Yes", "No"], default="No", required=True
        )
        if diff_farm == "Yes":
            self.diff_farm = True

    @chatflow_step(title="Farm selection")
    def select_farm(self):
        self.farm_name = None
        if self.diff_farm:
            self.md_show_update("Checking the available farms")
            old_node_ids = []
            for k8s_node in self.vdc.kubernetes:
                old_node_ids.append(k8s_node.node_id)
            gcc = GlobalCapacityChecker()
            gcc.exclude_nodes(*old_node_ids)
            node_flavor_size = VDC_SIZE.K8SNodeFlavor[self.node_flavor.upper()]
            farms_names = list(gcc.get_available_farms(**VDC_SIZE.K8S_SIZES[node_flavor_size]))
            if not farms_names:
                self.stop(f"There's no enough capacity for kubernetes node of flavor {self.node_flavor}")
            self.farm_name = self.drop_down_choice("Choose a farm to deploy on", options=farms_names, required=True)

    @chatflow_step(title="Adding node")
    def add_node(self):
        farm_name, capacity_check = self.vdc.find_worker_farm(self.node_flavor, self.farm_name, self.public_ip)
        if not capacity_check:
            self.stop(
                f"There's no enough capacity in farm {farm_name} for kubernetes node of flavor {self.node_flavor}"
            )
        j.logger.debug("found enough capacity, continue to payment")

        success, _, payment_id = self.vdc.show_external_node_payment(
            self, farm_name=farm_name, size=self.node_flavor, public_ip=self.public_ip
        )
        if not success:
            self.stop(f"payment timedout (in case you already paid, please contact support)")

        try:
            self.vdc.load_info()
            deployer = self.vdc.get_deployer(bot=self, network_farm=farm_name)
        except VDCIdentityError:
            self.stop(
                f"Couldn't verify VDC secret. please make sure you are using the correct secret for VDC {self.vdc_name}"
            )
        self.md_show_update("Payment successful")
        duration = self.vdc.get_pools_expiration() - j.data.time.utcnow().timestamp
        two_weeks = 2 * 7 * 24 * 60 * 60
        if duration > two_weeks:
            duration = two_weeks
        old_wallet = deployer._set_wallet(self.vdc.prepaid_wallet.instance_name)
        wids = []
        try:
            wids = deployer.add_k8s_nodes(self.node_flavor, farm_name=farm_name, public_ip=self.public_ip)
            self.md_show_update("Updating expiration...")
            deployer.extend_k8s_workloads(duration, *wids)
        except Exception as e:
            [deployer.delete_k8s_node(wid) for wid in wids]
            self.stop(f"failed to add nodes to your cluster. due to error {str(e)}")

        self.md_show_update("Processing transaction...")
        deployer._set_wallet(old_wallet)

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        self.md_show(f"""Your VDC {self.vdc.vdc_name} has been extended successfuly""")


chat = ExtendKubernetesCluster
