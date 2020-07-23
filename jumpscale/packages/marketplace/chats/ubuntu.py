import time

from jumpscale.loader import j
from jumpscale.clients.explorer.models import DiskType
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.marketplace import deployer, MarketPlaceChatflow


class UbuntuDeploy(MarketPlaceChatflow):
    SOLUTION_TYPE = SolutionType.Ubuntu

    HUB_URL = "https://hub.grid.tf/tf-bootable"
    IMAGES = ["ubuntu-18.04", "ubuntu-19.10", "ubuntu-20.04"]

    steps = [
        "welcome",
        "choose_network",
        "container_resources",
        "container_node_id",
        "container_farm",
        "solution_name",
        "ubuntu_version",
        "container_logs",
        "public_key_get",
        "container_ip",
        "expiration_time",
        "overview",
        "container_pay",
        "ubuntu_acess",
    ]
    title = "Ubuntu"

    @chatflow_step(title="Ubuntu version")
    def ubuntu_version(self):
        self.user_form_data["Version"] = self.single_choice("Please choose ubuntu version", self.IMAGES, required=True)
        self.metadata["Version"] = self.user_form_data["Version"]
        self.entry_point = "/bin/bash /start.sh"
        self.flist_url = f"{self.HUB_URL}/3bot-{self.user_form_data['Version']}.flist"

    @chatflow_step(title="Success", disable_previous=True)
    def ubuntu_acess(self):
        res = f"""\
# Ubuntu has been deployed successfully: your reservation id is: {self.resv_id}
To connect ```ssh root@{self.ip_address}``` .It may take a few minutes.
"""
        self.md_show(res, md=True)


chat = UbuntuDeploy
