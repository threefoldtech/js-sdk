import math

from jumpscale.clients.explorer.models import DiskType
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
from jumpscale.sals.reservation_chatflow.models import SolutionType
import uuid
from jumpscale.sals.reservation_chatflow import deployer, solutions


class MastodonDeploy(GedisChatBot):
    HUB_URL = "https://hub.grid.tf/tf-bootable"

    steps = [
        "mastodon_start",
        "mastodon_name",
        "container_resources",
        "container_configurations",
        "select_pool",
        "mastodon_network",
        # "container_logs",
        "container_node_id",
        "container_ip",
        "ipv6_config",
        "overview",
        "reservation",
        "mastodon_access",
    ]

    title = "Mastodon"

    @chatflow_step()
    def mastodon_start(self):
        self.solution_id = uuid.uuid4().hex
        self.md_show("# This wizard will help you deploy a mastodon container", md=True)
        self.solution_metadata = {}

    @chatflow_step(title="Solution name")
    def mastodon_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            mastodon_solutions = solutions.list_mastodon_solutions(sync=False)
            valid = True
            for sol in mastodon_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True

    @chatflow_step(title="Container resources")
    def container_resources(self):
        self.resources = deployer.ask_container_resources(self)

    @chatflow_step(title="Mastodon configurations")
    def container_configurations(self):
        # self.domain = self.string_ask("Please add domain/url", default="64.227.1.81", required=True)
        db_user = self.string_ask("Please add the database username", default="mastodon", required=True)
        db_name = self.string_ask("Please add the database name", default="mastodon_production", required=True)
        smtp_server = self.string_ask("Please add the smtp server", default="smtp.sendgrid.net", required=True)
        smtp_port = self.string_ask("Please add the smtp server port", default="587", required=True)
        smtp_login = self.string_ask("Please add smtp login name", default="apikey", required=True)
        smtp_password = self.string_ask("Please add smtp login password", default="urpass", required=True)
        smtp_from_address = self.string_ask(
            "Please add address email will be sent from", default="urlmal", required=True
        )

        self.env = {
            "DOMAIN": "64.227.1.81",  # TODO create subdomain
            "DB_USER": db_user,
            "DB_NAME": db_name,
            "SMTP_SERVER": smtp_server,
            "SMTP_PORT": smtp_port,
            "SMTP_LOGIN": smtp_login,
            "SMTP_PASSWORD": smtp_password,
            "SMTP_FROM_ADDRESS": smtp_from_address,
        }

    @chatflow_step(title="Pool")
    def select_pool(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        cu, su = deployer.calculate_capacity_units(**query)
        self.pool_id = deployer.select_pool(self, cu=cu, su=su, **query)

    @chatflow_step(title="Network")
    def mastodon_network(self):
        self.network_view = deployer.select_network(self)

    # @chatflow_step(title="Container logs")
    # def container_logs(self):
    #     self.container_logs_option = self.single_choice(
    #         "Do you want to push the container logs (stdout and stderr) onto an external redis channel",
    #         ["YES", "NO"],
    #         default="NO",
    #         required=True,
    #     )
    #     if self.container_logs_option == "YES":
    #         self.log_config = deployer.ask_container_logs(self, self.solution_name)
    #     else:
    #         self.log_config = {}

    @chatflow_step(title="Container node id")
    def container_node_id(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        self.selected_node = deployer.ask_container_placement(self, self.pool_id, **query)
        if not self.selected_node:
            self.selected_node = deployer.schedule_container(self.pool_id, **query)

    @chatflow_step(title="Container IP")
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
            self.md_show_update("Deploying Network on Nodes....")
            for wid in result["ids"]:
                success = deployer.wait_workload(wid)
                if not success:
                    raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {wid}")
            self.network_view_copy = self.network_view_copy.copy()
        free_ips = self.network_view_copy.get_node_free_ips(self.selected_node)
        self.ip_address = self.drop_down_choice(
            "Please choose IP Address for your solution", free_ips, default=free_ips[0], required=True
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
            "Database User": self.env["DB_USER"],
            "Database name": self.env["DB_NAME"],
            "SMTP Server name": self.env["SMTP_SERVER"],
            "SMTP port": self.env["SMTP_PORT"],
            "SMTP login user": self.env["SMTP_LOGIN"],
            "SMTP address to send from": self.env["SMTP_FROM_ADDRESS"],
        }
        # self.metadata.update(self.log_config)
        self.md_show_confirm(self.metadata)

    @chatflow_step(title="Reservation")
    def reservation(self):
        container_flist = f"https://hub.grid.tf/bishoy.3bot/threefolddev-mastodon-latest.flist"
        # if self.domain:
        #     self.subdomain_workload_id = deployer.create_subdomain(
        #         pool_id=self.gateway_pool.pool_id,
        #         gateway_id=self.gateway.node_id,
        #         subdomain=self.domain,
        #         addresses=self.addresses,
        #         solution_uuid=self.solution_id,
        #         **self.solution_metadata,
        #     )
        #     success = deployer.wait_workload(self.c, self)
        #     if not success:
        #         raise StopChatFlow(
        #             f"Failed to create subdomain {self.domain} on gateway {self.gateway.node_id} {self.subdomain_workload_id}"
        #         )

        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": "mastodon", "Solution name": self.solution_name},
        }
        self.solution_metadata.update(metadata)
        self.resv_id = deployer.deploy_container(
            pool_id=self.pool_id,
            node_id=self.selected_node.node_id,
            network_name=self.network_view.name,
            ip_address=self.ip_address,
            flist=container_flist,
            cpu=self.resources["cpu"],
            memory=self.resources["memory"],
            disk_size=self.resources["disk_size"],
            interactive=False,
            env=self.env,
            entrypoint="/start_mastodon.sh",
            # log_config=self.log_config,
            public_ipv6=self.public_ipv6,
            **self.solution_metadata,
            solution_uuid=self.solution_id,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

    @chatflow_step(title="Success", disable_previous=True)
    def mastodon_access(self):
        res = f"""\
# mastodon has been deployed successfully: your reservation id is: {self.resv_id}
\n<br />\n
To connect ```ssh root@{self.ip_address}``` .It may take a few minutes.
                """
        self.md_show(res, md=True)


chat = MastodonDeploy
