import math

from jumpscale.clients.explorer.models import DiskType
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
from jumpscale.sals.reservation_chatflow.models import SolutionType
import uuid
from jumpscale.sals.reservation_chatflow import deployer, solutions


class UbuntuDeploy(GedisChatBot):
    HUB_URL = "https://hub.grid.tf/tf-bootable"
    IMAGES = ["ubuntu-18.04", "ubuntu-19.10", "ubuntu-20.04"]

    steps = [
        "ubuntu_start",
        "ubuntu_name",
        "ubuntu_version",
        "container_resources",
        "select_pool",
        "ubuntu_network",
        "container_logs",
        "public_key_get",
        "container_node_id",
        "container_ip",
        "ipv6_config",
        "overview",
        "reservation",
        "ubuntu_access",
    ]

    title = "Ubuntu"

    @chatflow_step()
    def ubuntu_start(self):
        self.solution_id = uuid.uuid4().hex
        self.user_form_data = dict()
        self.query = dict()
        self.user_form_data["chatflow"] = "ubuntu"
        self.md_show("# This wizard will help you deploy an ubuntu container", md=True)

    @chatflow_step(title="Solution name")
    def ubuntu_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            ubuntu_solutions = solutions.list_ubuntu_solutions(sync=False)
            valid = True
            for sol in ubuntu_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True

    @chatflow_step(title="Ubuntu version")
    def ubuntu_version(self):
        self.version = self.single_choice("Please choose ubuntu version", self.IMAGES, required=True)

    @chatflow_step(title="Container resources")
    def container_resources(self):
        self.resources = deployer.ask_container_resources(self)

    @chatflow_step(title="Pool")
    def select_pool(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        cu, su = deployer.calculate_capacity_units(**query)
        self.pool_id = deployer.select_pool(self, cu=cu, su=su)

    @chatflow_step(title="Network")
    def ubuntu_network(self):
        self.network_view = deployer.select_network(self)

    @chatflow_step(title="Container logs")
    def container_logs(self):
        self.container_logs_option = self.single_choice(
            "Do you want to push the container logs (stdout and stderr) onto an external redis channel",
            ["YES", "NO"],
            default="NO",
        )
        if self.container_logs_option == "YES":
            self.log_config = deployer.ask_container_logs(self, self.solution_name)
        else:
            self.log_config = {}

    @chatflow_step(title="Access keys")
    def public_key_get(self):
        self.public_key = self.upload_file(
            """Please add your public ssh key, this will allow you to access the deployed container using ssh.
                    Just upload the file with the key""",
            required=True,
        ).split("\n")[0]

    @chatflow_step(title="Container node id")
    def container_node_id(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": self.resources["disk_size"],
        }
        self.selected_node = deployer.ask_container_placement(self, self.pool_id, **query)
        if not self.selected_node:
            self.selected_node = deployer.schedule_container(self.pool_id, **query)

    @chatflow_step(title="Container IP")
    def container_ip(self):
        self.network_view_copy = self.network_view.copy()
        result = deployer.add_network_node(
            self.network_view.name, self.selected_node, self.pool_id, self.network_view_copy
        )
        if result:
            self.md_show_update("Deploying Network on Nodes....")
            for wid in result["ids"]:
                success = deployer.wait_workload(wid)
                if not success:
                    raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {wid}")
            self.network_view_copy = self.network_view_copy.copy()
        free_ips = self.network_view_copy.get_node_free_ips(self.selected_node)
        self.ip_address = self.drop_down_choice(
            "Please choose IP Address for your solution", free_ips, default=free_ips[0]
        )

    @chatflow_step(title="Global IPv6 Address")
    def ipv6_config(self):
        self.public_ipv6 = deployer.ask_ipv6(self)

    @chatflow_step(title="Confirmation")
    def overview(self):
        self.metadata = {
            "Solution Name": self.solution_name,
            "Network": self.network_view.name,
            "Node ID": self.selected_node.node_id,
            "Pool": self.pool_id,
            "CPU": self.resources["cpu"],
            "Memory": self.resources["memory"],
            "Disk Size": self.resources["disk_size"],
            "IP Address": self.ip_address,
        }
        self.metadata.update(self.log_config)
        self.md_show_confirm(self.metadata)

    @chatflow_step(title="Reservation")
    def reservation(self):
        container_flist = f"{self.HUB_URL}/3bot-{self.version}.flist"
        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": "ubuntu", "Solution name": self.solution_name},
        }
        self.resv_id = deployer.deploy_container(
            pool_id=self.pool_id,
            node_id=self.selected_node.node_id,
            network_name=self.network_view.name,
            ip_address=self.ip_address,
            flist=container_flist,
            cpu=self.resources["cpu"],
            memory=self.resources["memory"],
            disk_size=self.resources["disk_size"],
            env={"pub_key": self.public_key},
            interactive=False,
            entrypoint="/bin/bash /start.sh",
            log_config=self.log_config,
            public_ipv6=self.public_ipv6,
            **metadata,
            solution_uuid=self.solution_id,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

    @chatflow_step(title="Success", disable_previous=True)
    def ubuntu_access(self):
        res = f"""\
# Ubuntu has been deployed successfully: your reservation id is: {self.resv_id}
\n<br />\n
To connect ```ssh root@{self.ip_address}``` .It may take a few minutes.
                """
        self.md_show(res, md=True)


chat = UbuntuDeploy
