import random

from jumpscale.loader import j

from jumpscale.clients.explorer.models import DiskType
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.vdc.deployer import VDCIdentityError
from jumpscale.sals.vdc.scheduler import CapacityChecker, GlobalCapacityChecker
from jumpscale.sals.vdc.size import VDC_SIZE, ZDB_STARTING_SIZE


class ExtendStorageNodes(GedisChatBot):
    title = "Extend Storage Containers"
    steps = ["disk_type", "different_farm", "select_farm", "add_node", "success"]

    @chatflow_step(title="Disk Type")
    def disk_type(self):
        disk_type = self.single_choice(
            "Choose the type of disk for the storage container", ["SSD", "HDD"], required=True, default="HDD"
        )
        self.zdb_disk_type = DiskType[disk_type]

    @chatflow_step(title="Farm Selection")
    def different_farm(self):
        self.md_show_update("Checking payment service...")
        # check stellar service
        if not j.clients.stellar.check_stellar_service():
            raise StopChatFlow("Payment service is currently down, try again later")
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
            gcc = GlobalCapacityChecker()
            farms_names = list(gcc.get_available_farms(hru=ZDB_STARTING_SIZE, ip_version="IPv6"))
            if not farms_names:
                self.stop("There's no enough capacity for adding storage node")
            self.farm_name = self.drop_down_choice("Choose a farm to deploy on", options=farms_names, required=True)

    @chatflow_step(title="Adding node")
    def add_node(self):
        if not j.sals.vdc.list_all():
            self.stop("Couldn't find any vdcs on this machine, Please make sure to have it configured properly")
        self.vdc_name = list(j.sals.vdc.list_all())[0]
        self.vdc = j.sals.vdc.get(name=self.vdc_name)
        if not self.vdc:
            self.stop(f"VDC {self.vdc_name} doesn't exist")
        try:
            self.vdc.load_info()
            deployer = self.vdc.get_deployer(bot=self)
        except VDCIdentityError:
            self.stop(
                f"Couldn't verify VDC secret. please make sure you are using the correct secret for VDC {self.vdc_name}"
            )

        # check for capacity before deploying
        if not self.farm_name:
            zdb_config = j.config.get("S3_AUTO_TOP_SOLUTIONS")
            farm_names = zdb_config.get("farm_names")
            self.farm_name = random.choice(farm_names)
        cc = CapacityChecker(self.farm_name)
        storage_query = {"hru": ZDB_STARTING_SIZE}
        if self.disk_type == DiskType.SSD:
            storage_query = {"sru": ZDB_STARTING_SIZE}

        if not cc.add_query(ip_version="IPv6", **storage_query):
            self.stop(f"There's no enough capacity in farm {self.farm_name} for adding storage node")
        j.logger.debug("found enough capacity, continue to payment")

        success, _, payment_id = self.vdc.show_external_zdb_payment(self, self.farm_name, disk_type=self.zdb_disk_type)
        if not success:
            self.stop(f"payment timedout (in case you already paid, please contact support)")

        self.md_show_update("Payment successful")
        duration = self.vdc.get_pools_expiration() - j.data.time.utcnow().timestamp
        two_weeks = 2 * 7 * 24 * 60 * 60
        duration = duration if duration < two_weeks else two_weeks
        wids = []
        try:
            zdb_monitor = self.vdc.get_zdb_monitor()
            self.md_show_update("Deploying 1 Storage Node")
            wids = zdb_monitor.extend(
                required_capacity=ZDB_STARTING_SIZE,
                farm_names=[self.farm_name],
                wallet_name="prepaid_wallet",
                duration=60 * 60,
                disk_type=self.zdb_disk_type,
            )
            deployer.extend_zdb_workload(duration, *wids)
        except Exception as e:
            [deployer.delete_s3_zdb(wid) for wid in wids]
            self.stop(f"failed to add storage nodes to your VDC. due to error {str(e)}")

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        self.md_show(f"""Your VDC {self.vdc.vdc_name} has been extended successfully""")


chat = ExtendStorageNodes
