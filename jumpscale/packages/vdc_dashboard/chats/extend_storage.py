from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.vdc.scheduler import CapacityChecker, GlobalCapacityChecker
from jumpscale.sals.vdc.size import VDC_SIZE, ZDB_STARTING_SIZE


class ExtendKubernetesCluster(GedisChatBot):
    title = "Extend Storage Nodes"
    steps = ["different_farm", "select_farm", "add_node", "success"]

    @chatflow_step(title="Farm Selection")
    def different_farm(self):
        self.md_show_update("Checking payment service...")
        # check stellar service
        if not j.clients.stellar.check_stellar_service():
            raise StopChatFlow("Payment service is currently down, try again later")
        self.diff_farm = False
        diff_farm = self.single_choice(
            "Do you want to deploy this node on a different farm", options=["Yes", "No"], default="No", required=True
        )
        if diff_farm == "Yes":
            self.diff_farm = True

    @chatflow_step(title="Farm selection")
    def select_farm(self):
        self.farm_name = None
        if self.diff_farm:
            self.md_show_update("Checking the available farms")
            gcc = GlobalCapacityChecker()
            farms_names = list(gcc.get_available_farms(hru=ZDB_STARTING_SIZE, ip_version="IPv6"))
            if not farms_names:
                self.stop("There's no enough capacity for adding storage node")
            self.farm_name = self.single_choice("Choose a farm to deploy on", options=farms_names, required=True)

    @chatflow_step(title="Adding node")
    def add_node(self):
        self.vdc_name = list(j.sals.vdc.list_all())[0]
        self.vdc = j.sals.vdc.get(name=self.vdc_name)
        if not self.vdc:
            self.stop(f"VDC {self.vdc_name} doesn't exist")
        self.vdc.load_info()
        zdb_monitor = self.vdc.get_zdb_monitor()

        # check for capacity before deploying
        if not self.farm_name:
            farm_names = zdb_monitor.get_zdb_farm_names()
            self.farm_name = farm_names[0]
        cc = CapacityChecker(self.farm_name)
        if not cc.add_query(hru=ZDB_STARTING_SIZE, ip_version="IPv6"):
            self.stop(f"There's no enough capacity in farm {self.farm_name} for adding storage node")
        j.logger.debug("found enough capacity, continue to payment")

        success, payment_id = self.vdc.show_external_zdb_payment(self, self.farm_name)
        if not success:
            self.stop(f"payment timedout")

        self.md_show_update("Payment successful")
        try:
            self.md_show_update("Deploying 1 Storage Node")
            zdb_monitor.extend(
                required_capacity=ZDB_STARTING_SIZE, farm_names=[self.farm_name], wallet_name="prepaid_wallet"
            )
        except Exception as e:
            j.sals.billing.issue_refund(payment_id)
            self.stop(f"failed to add storage nodes to your VDC. due to error {str(e)}")

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        self.md_show(f"""Your VDC {self.vdc.vdc_name} has been extended successfuly""")


chat = ExtendKubernetesCluster
