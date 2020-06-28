import time

from jumpscale.god import j
from jumpscale.clients.explorer.models import DiskType
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.deployer import deployer, MarketPlaceChatflow


class UbuntuDeploy(MarketPlaceChatflow):
    SOLUTION_TYPE = "Ubuntu"

    HUB_URL = "https://hub.grid.tf/tf-bootable"
    IMAGES = ["ubuntu-18.04", "ubuntu-19.10", "ubuntu-20.04"]

    steps = [
        "solution_name",
        "choose_network",
        "ubuntu_version",
        "container_resources",
        "container_logs",
        "public_key_get",
        "container_node_id",
        "container_farm",
        "container_ip",
        "expiration_time",
        "overview",
        "container_pay",
        "ubuntu_acess",
    ]

    @chatflow_step(title="Ubuntu version")
    def ubuntu_version(self):
        self.user_form_data["Version"] = self.single_choice("Please choose ubuntu version", self.IMAGES, required=True)

    @chatflow_step(title="Payment", disable_previous=True)
    def container_pay(self):
        self.network = self.network_copy
        self.network.update(self.get_tid(), currency=self.query["currency"], bot=self)
        container_flist = f"{self.HUB_URL}/3bot-{self.user_form_data['Version']}.flist"
        storage_url = "zdb://hub.grid.tf:9900"
        entry_point = "/bin/bash /start.sh"

        # create container
        cont = j.sals.zos.container.create(
            reservation=self.reservation,
            node_id=self.node_selected.node_id,
            network_name=self.network.name,
            ip_address=self.ip_address,
            flist=container_flist,
            storage_url=storage_url,
            disk_type=DiskType.SSD.value,
            disk_size=self.rootfs_size.value,
            env=self.var_dict,
            interactive=False,
            entrypoint=entry_point,
            cpu=self.user_form_data["CPU"],
            memory=self.user_form_data["Memory"],
        )
        if self.container_logs_option == "YES":
            j.sals.zos.container.add_logs(
                cont,
                channel_type=self.user_form_data["Logs Channel type"],
                channel_host=self.user_form_data["Logs Channel host"],
                channel_port=self.user_form_data["Logs Channel port"],
                channel_name=self.user_form_data["Logs Channel name"],
            )
        metadata = dict()
        metadata["Version"] = self.user_form_data["Version"]
        metadata["Solution expiration"] = self.user_form_data["Solution expiration"]

        res = deployer.get_solution_metadata(
            self.user_form_data["Solution name"], SolutionType.Ubuntu, self.tid, metadata
        )
        reservation = deployer.add_reservation_metadata(self.reservation, res)
        self.resv_id = j.sals.reservation_chatflow.register_and_pay_reservation(
            reservation, self.expiration, customer_tid=j.core.identity.me.tid, currency=self.query["currency"], bot=self
        )

    @chatflow_step(title="Success", disable_previous=True)
    def ubuntu_acess(self):
        res = f"""\
# Ubuntu has been deployed successfully: your reservation id is: {self.resv_id}
To connect ```ssh root@{self.ip_address}``` .It may take a few minutes.
"""
        self.md_show(res, md=True)


chat = UbuntuDeploy
