import math
import uuid
import requests
from textwrap import dedent

from jumpscale.clients.explorer.models import DiskType
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.reservation_chatflow import DeploymentFailed, deployer, solutions, deployment_context


class FlistDeploy(GedisChatBot):
    steps = [
        "flist_name",
        "container_resources",
        "container_volume",
        "container_volume_details",
        "select_pool",
        "flist_network",
        "flist_url",
        "container_interactive",
        "ipv6_config",
        "container_node_id",
        "container_logs",
        "container_ip",
        "container_env",
        "reservation",
        "success",
    ]
    title = "Generic Container"

    def _flist_start(self):
        deployer.chatflow_pools_check()
        deployer.chatflow_network_check(self)
        self.solution_id = uuid.uuid4().hex
        self.env = dict()
        self.solution_metadata = {}

    @chatflow_step(title="Solution Name")
    def flist_name(self):
        self._flist_start()
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            flist_solutions = solutions.list_flist_solutions(sync=False)
            valid = True
            for sol in flist_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another name.")
                    break
                valid = True

    @chatflow_step(title="Container resources")
    def container_resources(self):
        self.resources = deployer.ask_container_resources(self)

    @chatflow_step(title="Attach Volume")
    def container_volume(self):
        volume_attach = self.drop_down_choice(
            "Would you like to attach an extra volume to the container", ["YES", "NO"], required=True, default="NO"
        )
        self.container_volume_attach = volume_attach == "YES" or False

    @chatflow_step(title="Volume details")
    def container_volume_details(self):
        if self.container_volume_attach:
            form = self.new_form()
            vol_disk_size = form.int_ask("Please specify the volume size in GiB", required=True, default=10, min=1)
            vol_mount_point = form.string_ask("Please enter the mount point", required=True, default="/data")
            form.ask()
            self.vol_size = vol_disk_size.value
            self.vol_mount_point = vol_mount_point.value

    @chatflow_step(title="Pool")
    def select_pool(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        if self.container_volume_attach:
            query["sru"] += math.ceil(self.vol_size / 1024)
        cloud_units = j.sals.marketplace.deployer._calculate_cloud_units(**query)
        self.pool_id = deployer.select_pool(self, cu=cloud_units.cu, su=cloud_units.su, **query)

    @chatflow_step(title="Network")
    def flist_network(self):
        self.network_view = deployer.select_network(self, self.all_network_viewes)

    @chatflow_step(title="Flist url")
    def flist_url(self):
        valid = False
        while not valid:
            self.flist_link = self.string_ask(
                "Please add the link to your flist to be deployed. For example: https://hub.grid.tf/usr/example.flist",
                required=True,
            )

            self.flist_link = self.flist_link.strip()

            if "hub.grid.tf" not in self.flist_link or ".md" in self.flist_link[-3:]:
                self.md_show(
                    "This flist is not correct. Please make sure you enter a valid link to an existing flist For example: https://hub.grid.tf/usr/example.flist. click next yo try again"
                )
                continue

            response = requests.head(self.flist_link)
            response_md5 = requests.head(f"{self.flist_link}.md5")
            if response.status_code != 200 or response_md5.status_code != 200:
                self.md_show(
                    "This flist doesn't exist. Please make sure you enter a valid link to an existing flist. click next to try again"
                )
                continue
            valid = True

    @chatflow_step(title="Container Interactive & EntryPoint")
    def container_interactive(self):
        self.interactive = self.single_choice(
            "Would you like access to your container through the web browser (coreX)?",
            ["YES", "NO"],
            required=True,
            default="YES",
        )
        if self.interactive == "NO":
            self.entrypoint = self.string_ask("Please add your entrypoint for your flist") or ""
        else:
            self.port = "7681"
            self.entrypoint = ""

    @chatflow_step(title="Environment variables")
    def container_env(self):
        self.env.update(self.multi_values_ask("Set Environment Variables"))

    @chatflow_step(title="Global IPv6 Address")
    def ipv6_config(self):
        self.public_ipv6 = deployer.ask_ipv6(self)
        if self.public_ipv6:
            self.ip_version = "IPv6"
        else:
            self.ip_version = None

    @chatflow_step(title="Choose a node to deploy on")
    def container_node_id(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        self.selected_node = deployer.ask_container_placement(self, self.pool_id, ip_version=self.ip_version, **query)
        if not self.selected_node:
            self.selected_node = deployer.schedule_container(self.pool_id, ip_version=self.ip_version, **query)

    @chatflow_step(title="Container logs")
    def container_logs(self):
        self.container_logs_option = self.single_choice(
            "Do you want to push the container logs (stdout and stderr) onto an external redis channel",
            ["YES", "NO"],
            default="NO",
            required=True,
        )
        if self.container_logs_option == "YES":
            self.log_config = deployer.ask_container_logs(self, self.solution_name)
        else:
            self.log_config = {}

    @chatflow_step(title="Container IP")
    @deployment_context()
    def container_ip(self):
        self.network_view_copy = self.network_view.copy()
        result = deployer.add_network_node(
            self.network_view.name,
            self.selected_node,
            self.pool_id,
            self.network_view_copy,
            bot=self,
            owner=self.solution_metadata.get("owner"),
        )
        if result:
            for wid in result["ids"]:
                success = deployer.wait_workload(wid, self, breaking_node_id=self.selected_node.node_id)
                if not success:
                    raise DeploymentFailed(f"Failed to add node {self.selected_node.node_id} to network {wid}", wid=wid)
            self.network_view_copy = self.network_view_copy.copy()
        free_ips = self.network_view_copy.get_node_free_ips(self.selected_node)
        self.ip_address = self.drop_down_choice(
            "Please choose IP Address for your solution", free_ips, default=free_ips[0], required=True
        )

    @chatflow_step(title="Reservation")
    @deployment_context()
    def reservation(self):
        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": "flist", "Solution name": self.solution_name, "env": self.env},
        }
        self.solution_metadata.update(metadata)
        volume_config = {}
        if self.container_volume_attach:
            vol_id = deployer.deploy_volume(
                self.pool_id,
                self.selected_node.node_id,
                self.vol_size,
                solution_uuid=self.solution_id,
                **self.solution_metadata,
            )
            success = deployer.wait_workload(vol_id, self)
            if not success:
                raise DeploymentFailed(
                    f"Failed to deploy volume on node {self.selected_node.node_id} {vol_id}", wid=vol_id
                )
            volume_config[self.vol_mount_point] = vol_id

        self.resv_id = deployer.deploy_container(
            pool_id=self.pool_id,
            node_id=self.selected_node.node_id,
            network_name=self.network_view.name,
            ip_address=self.ip_address,
            flist=self.flist_link,
            cpu=self.resources["cpu"],
            memory=self.resources["memory"],
            disk_size=self.resources["disk_size"],
            env=self.env,
            interactive=self.interactive,
            entrypoint=self.entrypoint,
            log_config=self.log_config,
            volumes=volume_config,
            public_ipv6=self.public_ipv6,
            **self.solution_metadata,
            solution_uuid=self.solution_id,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            raise DeploymentFailed(
                f"Failed to deploy workload {self.resv_id}", solution_uuid=self.solution_id, wid=self.resv_id
            )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        if self.interactive == "YES":
            message = f"""\
            # Congratulations! Your own container deployed successfully:
            <br />\n
            - <a href="https://github.com/threefoldtech/corex" target="_blank">COREX</a> enabled.
            <br />\n
            - You can monitor processes from the browser: <a href="http://{self.ip_address}:7681" target="_blank">http://{self.ip_address}:7681</a>
            <br />\n
            - And can start `bash` process from here: <a href="http://{self.ip_address}:7681/api/process/start?arg[]=/bin/bash" target="_blank">http://{self.ip_address}:7681/api/process/start?arg[]=/bin/bash</a>
            <br />\n
            """
        else:
            message = f"""\
            # Congratulations! Your own container deployed successfully:
            <br />\n
            - Your ip address: `{self.ip_address}`
            """
        self.md_show(dedent(message), md=True)


chat = FlistDeploy
