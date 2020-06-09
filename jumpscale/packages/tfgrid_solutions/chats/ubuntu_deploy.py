from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
from jumpscale.sals.reservation_chatflow.models import SolutionType
import time


class UbuntuDeploy(GedisChatBot):
    steps = [
        "ubuntu_start",
        "ubuntu_network",
        "ubuntu_name",
        "ubuntu_version",
        "container_resources",
        "public_key_get",
        "container_node_id",
        "ubuntu_farm",
        "container_ip",
        "expiration_time",
        "overview",
        "container_pay",
        "ubuntu_acess",
    ]

    @chatflow_step()
    def ubuntu_start(self):
        self.user_form_data = dict()
        self.query = dict()
        self.HUB_URL = "https://hub.grid.tf/tf-bootable"
        self.IMAGES = ["ubuntu-18.04","ubuntu-19.10","ubuntu-20.04"]
        user_info = self.user_info()
        self.user_form_data["chatflow"] = "ubuntu"
        self.md_show("# This wizard will help you deploy an ubuntu container", md=True)
        # j.sals.reservation_chatflow.validate_user(user_info)  # TODO: bring it back when Auth is ready

    @chatflow_step(title="Network")
    def ubuntu_network(self):
        self.network = j.sals.reservation_chatflow.select_network(self, j.core.identity.tid)

    @chatflow_step(title="Solution name")
    def ubuntu_name(self):
        self.user_form_data["Solution name"] = self.string_ask("Please enter a name for your ubuntu container", required=True, field="name")

    @chatflow_step(title="Ubuntu version")
    def ubuntu_version(self):
        self.user_form_data["Version"] = self.single_choice("Please choose ubuntu version", self.IMAGES, required=True)

    @chatflow_step(title="Container resources")
    def container_resources(self):
        form = self.new_form()
        cpu = form.int_ask("Please add how many CPU cores are needed", default=1, required=True)
        memory = form.int_ask("Please add the amount of memory in MB", default=1024, required=True)
        self.rootfs_type = form.single_choice("Select the storage type for your root filesystem", ["SSD", "HDD"], default="SSD")
        self.rootfs_size = form.int_ask("Choose the amount of storage for your root filesystem in MiB", default=256)
        form.ask()
        self.user_form_data["CPU"] = cpu.value
        self.user_form_data["Memory"] = memory.value
        self.user_form_data["Root filesystem Type"] = str(self.rootfs_type.value)
        self.user_form_data["Root filesystem Size"] = self.rootfs_size.value

    @chatflow_step(title="Access keys")
    def public_key_get(self):
        self.user_form_data["Public key"] = self.upload_file(
            """Please add your public ssh key, this will allow you to access the deployed container using ssh.
                    Just upload the file with the key""",
            required=True,
        ).split("\n")[0]


chat = UbuntuDeploy