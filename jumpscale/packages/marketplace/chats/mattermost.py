from textwrap import dedent

from jumpscale.packages.tfgrid_solutions.chats.mattermost import MattermostDeploy as BaseMattermostDeploy
from jumpscale.sals.chatflows.chatflows import chatflow_step, StopChatFlow
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions
from jumpscale.loader import j


class MattermostDeploy(MarketPlaceChatflow):
    FLIST_URL = "https://hub.grid.tf/ayoubm.3bot/rafyamgadbenjamin-mattermost-latest.flist"
    SOLUTION_TYPE = "mattermost"
    title = "Mattermost"
    steps = [
        "start",
        "solution_name",
        "mattermost_info",
        "solution_expiration",
        "payment_currency",
        "infrastructure_setup",
        "overview",
        "reservation",
        "success",
    ]

    @chatflow_step()
    def start(self):
        self._init_solution()
        self.query = {"cru": 1, "mru": 1, "sru": 1}
        self.md_show("# This wizard wil help you deploy an mattermost container", md=True)

    @chatflow_step(title="Mattermost Information")
    def mattermost_info(self):
        form = self.new_form()
        disk_sizes = [2, 5, 10]
        volume_size = form.single_choice("choose the disk size", disk_sizes, required=True, default=disk_sizes[0])
        form.ask()
        self.vol_size = int(volume_size.value)
        self.query["sru"] += self.vol_size

    @chatflow_step(title="Confirmation")
    def overview(self):
        self.metadata = {
            "Solution Name": self.solution_name,
            "Network": self.network_view.name,
            "Node ID": self.selected_node.node_id,
            "Pool": self.pool_info.reservation_id,
            "CPU": self.query["cru"],
            "Memory": self.query["mru"],
            "Disk Size": (self.query["sru"] - self.vol_size) * 1024,
            "IP Address": self.ip_address,
        }
        self.md_show_confirm(self.metadata)

    @chatflow_step(title="Reservation", disable_previous=True)
    def reservation(self):
        var_dict = {
            "MYSQL_ROOT_PASSWORD": "mostest",
            "MYSQL_USER": "mmuser",
            "MYSQL_PASSWORD": "mostest",
            "MYSQL_DATABASE": "mattermost_db",
        }
        metadata = {
            "name": self.solution_name,
            "form_info": {
                "Solution name": self.solution_name,
                "Domain name": self.domain,
                "chatflow": self.SOLUTION_TYPE,
            },
        }
        self.solution_metadata.update(metadata)

        # reserve subdomain
        _id = deployer.create_subdomain(
            pool_id=self.gateway_pool.pool_id,
            gateway_id=self.gateway.node_id,
            subdomain=self.domain,
            addresses=self.addresses,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )

        success = deployer.wait_workload(_id, self)
        if not success:
            raise StopChatFlow(f"Failed to create subdomain {self.domain} on gateway" f" {self.gateway.node_id} {_id}")
        self.solution_url = f"https://{self.domain}"

        # create volume
        vol_mount_point = "/var/lib/mysql/"
        volume_config = {}
        vol_id = deployer.deploy_volume(
            self.pool_id,
            self.selected_node.node_id,
            self.vol_size,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(vol_id, self)
        if not success:
            raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {vol_id}")
        volume_config[vol_mount_point] = vol_id

        # Create container
        self.resv_id = deployer.deploy_container(
            pool_id=self.pool_id,
            node_id=self.selected_node.node_id,
            network_name=self.network_view.name,
            ip_address=self.ip_address,
            flist=self.FLIST_URL,
            cpu=self.query["cru"],
            memory=self.query["mru"] * 1024,
            disk_size=(self.query["sru"] - self.vol_size) * 1024,
            env=var_dict,
            interactive=False,
            entrypoint="/start_mattermost.sh",
            volumes=volume_config,
            public_ipv6=True,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            solutions.cancel_solution([self.resv_id])
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

        # expose threebot container
        _id = deployer.expose_and_create_certificate(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            network_name=self.network_view.name,
            trc_secret=self.secret,
            domain=self.domain,
            email=self.user_info()["email"],
            solution_ip=self.ip_address,
            solution_port=8065,
            enforce_https=False,
            node_id=self.selected_node.node_id,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(_id, self)
        if not success:
            # solutions.cancel_solution(self.workload_ids)
            raise StopChatFlow(f"Failed to create trc container on node {self.selected_node.node_id}" f" {_id}")

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        self._wgconf_show_check()
        message = f"""\
# mattermost has been deployed successfully:
\n<br />\n
your reservation id is: {self.resv_id}
\n<br />\n
your container ip is: `{self.ip_address}`
\n<br />\n
open Mattermost from browser at <a href="http://{self.domain}" target="_blank">https://{self.domain}</a>
\n<br />\n
- It may take few minutes to load.
                """
        self.md_show(dedent(message), md=True)


chat = MattermostDeploy
