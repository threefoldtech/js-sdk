from jumpscale.god import j

from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType

from jumpscale.clients.explorer.models import DiskType

import math


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
        self.IMAGES = ["ubuntu-18.04", "ubuntu-19.10", "ubuntu-20.04"]
        user_info = self.user_info()
        self.user_form_data["chatflow"] = "ubuntu"
        self.md_show("# This wizard will help you deploy an ubuntu container", md=True)
        # j.sals.reservation_chatflow.validate_user(user_info)  # TODO: bring it back when Auth is ready

    @chatflow_step(title="Network")
    def ubuntu_network(self):
        self.network = j.sals.reservation_chatflow.select_network(self, j.core.identity.tid)

    @chatflow_step(title="Solution name")
    def ubuntu_name(self):
        self.user_form_data["Solution name"] = self.string_ask(
            "Please enter a name for your ubuntu container", required=True, field="name"
        )

    @chatflow_step(title="Ubuntu version")
    def ubuntu_version(self):
        self.user_form_data["Version"] = self.single_choice("Please choose ubuntu version", self.IMAGES, required=True)

    @chatflow_step(title="Container resources")
    def container_resources(self):
        form = self.new_form()
        cpu = form.int_ask("Please add how many CPU cores are needed", default=1, required=True)
        memory = form.int_ask("Please add the amount of memory in MB", default=1024, required=True)
        disk = form.single_choice("Select the storage type for your root filesystem", ["SSD", "HDD"], default="SSD")
        self.rootfs_size = form.int_ask("Choose the amount of storage for your root filesystem in MiB", default=256)
        form.ask()
        self.rootfs_type = getattr(DiskType, disk.value)
        self.user_form_data["CPU"] = cpu.value
        self.user_form_data["Memory"] = memory.value
        self.user_form_data["Root filesystem Type"] = disk.value
        self.user_form_data["Root filesystem Size"] = self.rootfs_size.value

    @chatflow_step(title="Access keys")
    def public_key_get(self):
        self.user_form_data["Public key"] = self.upload_file(
            """Please add your public ssh key, this will allow you to access the deployed container using ssh.
                    Just upload the file with the key""",
            required=True,
        ).split("\n")[0]

    @chatflow_step(title="Container node id")
    def container_node_id(self):
        self.var_dict = {"pub_key": self.user_form_data["Public key"]}
        self.query["mru"] = math.ceil(self.user_form_data["Memory"] / 1024)
        self.query["cru"] = self.user_form_data["CPU"]
        storage_units = math.ceil(self.rootfs_size.value / 1024)
        if self.rootfs_type.value == "SSD":
            self.query["sru"] = storage_units
        else:
            self.query["hru"] = storage_units
        # create new reservation
        self.reservation = j.sals.zos.reservation_create()
        self.nodeid = self.string_ask(
            "Please enter the nodeid you would like to deploy on if left empty a node will be chosen for you"
        )
        while self.nodeid:
            try:
                self.node_selected = j.sals.reservation_chatflow.validate_node(
                    self.nodeid, self.query, self.network.currency
                )
                break
            except (j.exceptions.Value, j.exceptions.NotFound) as e:
                message = "<br> Please enter a different nodeid to deploy on or leave it empty"
                self.nodeid = self.string_ask(str(e) + message, html=True, retry=True)
        self.query["currency"] = self.network.currency

    @chatflow_step(title="Ubuntu container farm")
    def ubuntu_farm(self):
        if not self.nodeid:
            farms = j.sals.reservation_chatflow.get_farm_names(1, self, **self.query)
            self.node_selected = j.sals.reservation_chatflow.get_nodes(1, farm_names=farms, **self.query)[0]

    @chatflow_step(title="Container IP")
    def container_ip(self):
        self.network_copy = self.network.copy(j.core.identity.tid)
        self.network_copy.add_node(self.node_selected)
        self.ip_address = self.network_copy.ask_ip_from_node(
            self.node_selected, "Please choose IP Address for your solution"
        )
        self.user_form_data["IP Address"] = self.ip_address

    @chatflow_step(title="Expiration time")
    def expiration_time(self):
        self.expiration = self.datetime_picker(
            "Please enter solution expiration time.",
            required=True,
            min_time=[3600, "Date/time should be at least 1 hour from now"],
            default=j.data.time.get().timestamp + 3900,
        )
        self.user_form_data["Solution expiration"] = j.data.time.get(self.expiration).humanize()

    @chatflow_step(title="Confirmation")
    def overview(self):
        self.md_show_confirm(self.user_form_data)

    @chatflow_step(title="Payment", disable_previous=True)
    def container_pay(self):
        self.network = self.network_copy
        self.network.update(j.core.identity.tid, currency=self.query["currency"], bot=self)
        container_flist = f"{self.HUB_URL}/3bot-{self.user_form_data['Version']}.flist"
        storage_url = "zdb://hub.grid.tf:9900"
        entry_point = "/bin/bash /start.sh"

        # create container
        j.sals.zos.container.create(
            reservation=self.reservation,
            node_id=self.node_selected.node_id,
            network_name=self.network.name,
            ip_address=self.ip_address,
            flist=container_flist,
            storage_url=storage_url,
            disk_type=self.rootfs_type,
            disk_size=self.rootfs_size.value,
            env=self.var_dict,
            interactive=False,
            entrypoint=entry_point,
            cpu=self.user_form_data["CPU"],
            memory=self.user_form_data["Memory"],
        )
        metadata = dict()
        metadata["chatflow"] = self.user_form_data["chatflow"]
        metadata["Solution name"] = self.user_form_data["Solution name"]
        metadata["Version"] = self.user_form_data["Version"]
        metadata["Solution expiration"] = self.user_form_data["Solution expiration"]

        res = j.sals.reservation_chatflow.get_solution_metadata(
            self.user_form_data["Solution name"], SolutionType.Ubuntu, metadata
        )
        reservation = j.sals.reservation_chatflow.add_reservation_metadata(self.reservation, res)
        self.resv_id = j.sals.reservation_chatflow.register_and_pay_reservation(
            reservation, self.expiration, customer_tid=j.core.identity.tid, currency=self.query["currency"], bot=self
        )

        j.sals.reservation_chatflow.save_reservation(
            self.resv_id, self.user_form_data["Solution name"], SolutionType.Ubuntu, self.user_form_data
        )

    @chatflow_step(title="Success", disable_previous=True)
    def ubuntu_acess(self):
        res = f"""\
# Ubuntu has been deployed successfully: your reservation id is: {self.resv_id}
To connect ```ssh root@{self.ip_address}``` .It may take a few minutes.
"""
        self.md_show(res, md=True)


chat = UbuntuDeploy
