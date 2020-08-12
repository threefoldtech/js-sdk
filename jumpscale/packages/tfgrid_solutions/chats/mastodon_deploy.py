import math
import random
import uuid

from jumpscale.clients.explorer.models import DiskType
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow import deployer, solutions
from jumpscale.sals.reservation_chatflow.models import SolutionType


class MastodonDeploy(GedisChatBot):
    HUB_URL = "https://hub.grid.tf/tf-bootable"

    steps = [
        "mastodon_start",
        "mastodon_name",
        "smtp_credentials",
        "select_pool",
        "mastodon_network",
        "container_node_id",
        "overview",
        "subdomain_select",
        "reservation",
        "mastodon_access",
    ]

    title = "Mastodon"

    @chatflow_step()
    def mastodon_start(self):
        self.solution_id = uuid.uuid4().hex
        self.md_show("# This wizard will help you deploy a mastodon container", md=True)
        self.solution_metadata = {}
        self.user_info_dict = self.user_info()

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

    @chatflow_step(title="SMTP server credentials")
    def smtp_credentials(self):
        # self.domain = self.string_ask("Please add domain/url", default="64.227.1.81", required=True)
        form = self.new_form()
        smtp_server = form.string_ask("Please add the SMTP server", default="smtp.sendgrid.net", required=True)
        smtp_port = form.string_ask("Please add the port the SMTP server exposes", default="587", required=True)
        smtp_login = form.string_ask("Please add the SMTP login name", default="apikey", required=True)
        smtp_password = form.string_ask("Please add the SMTP login password", required=True)
        smtp_from_address = form.string_ask("Please add the email address mastodon will be sending from", required=True)
        form.ask()

        self.env = {
            # "DOMAIN": "64.227.1.81",  # TODO create subdomain
            "DB_USER": self.user_info_dict["username"],
            "DB_NAME": "mastodon_" + self.user_info_dict["username"],
            "SMTP_SERVER": smtp_server.value,
            "SMTP_PORT": smtp_port.value,
            "SMTP_LOGIN": smtp_login.value,
            "SMTP_FROM_ADDRESS": smtp_from_address.value,
            "pub_key": "",
        }
        self.secret_env = {"SMTP_PASSWORD": smtp_password.value}

    @chatflow_step(title="Pool")
    def select_pool(self):
        query = {"cru": 1, "mru": 1, "sru": 10}
        cu, su = deployer.calculate_capacity_units(**query)
        self.pool_id = deployer.select_pool(self, cu=cu, su=su, **query)

    @chatflow_step(title="Network")
    def mastodon_network(self):
        self.network_view = deployer.select_network(self)

    @chatflow_step(title="Container node id")
    def container_node_id(self):
        query = {"cru": 1, "mru": 1, "sru": 10}
        self.selected_node = deployer.schedule_container(self.pool_id, **query)

    @chatflow_step(title="Confirmation")
    def overview(self):
        self.metadata = {
            "Solution Name": self.solution_name,
            "Network": self.network_view.name,
            "Node ID": self.selected_node.node_id,
            "Pool": self.pool_id,
            "SMTP Server name": self.env["SMTP_SERVER"],
            "SMTP port": self.env["SMTP_PORT"],
            "SMTP login user": self.env["SMTP_LOGIN"],
            "SMTP address to send from": self.env["SMTP_FROM_ADDRESS"],
        }
        self.md_show_confirm(self.metadata)

    @chatflow_step(title="Domain selection")
    def subdomain_select(self):
        # select ip address
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
        self.ip_address = random.choice(free_ips)

        # select domain
        gateways = deployer.list_all_gateways()
        if not gateways:
            raise StopChatFlow("There are no available gateways in the farms bound to your pools.")

        domains = dict()
        for gw_dict in gateways.values():
            gateway = gw_dict["gateway"]
            for domain in gateway.managed_domains:
                domains[domain] = gw_dict

        self.domain = random.choice(list(domains.keys()))
        # self.single_choice("Please choose the domain you wish to use", list(domains.keys()), required=True)

        self.gateway = domains[self.domain]["gateway"]
        self.gateway_pool = domains[self.domain]["pool"]
        self.subdomain = self.string_ask(
            "Please specify a subdomain that you will use to access mastodon from the browser. It will be in the form `<YOUR_SUBDOMAIN>.{self.domain}`",
            required=True,
        )
        self.domain = f"{self.subdomain}.{self.domain}"

        self.addresses = []
        for ns in self.gateway.dns_nameserver:
            self.addresses.append(j.sals.nettools.get_host_by_name(ns))

        self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

        self.metadata.update(
            {
                "IP Address": self.ip_address,
                "CPU": 1,
                "Memory": 1024,
                "Disk Size": 10000,
                "Database User": self.env["DB_USER"],
                "Database name": self.env["DB_NAME"],
            }
        )

    @chatflow_step(title="Reservation")
    def reservation(self):
        container_flist = f"https://hub.grid.tf/bishoy.3bot/threefolddev-mastodon-latest.flist"
        # reserve subdomain
        if self.domain:
            self.subdomain_workload_id = deployer.create_subdomain(
                pool_id=self.gateway_pool.pool_id,
                gateway_id=self.gateway.node_id,
                subdomain=self.domain,
                addresses=self.addresses,
                solution_uuid=self.solution_id,
                **self.solution_metadata,
            )
            success = deployer.wait_workload(self.subdomain_workload_id, self)
            if not success:
                raise StopChatFlow(
                    f"Failed to create subdomain {self.domain} on gateway {self.gateway.node_id} {self.subdomain_workload_id}"
                )
            self.env.update({"DOMAIN": self.domain})

        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": "mastodon", "Solution name": self.solution_name},
        }
        self.solution_metadata.update(metadata)

        # deploy container
        self.resv_id = deployer.deploy_container(
            pool_id=self.pool_id,
            node_id=self.selected_node.node_id,
            network_name=self.network_view.name,
            ip_address=self.ip_address,
            flist=container_flist,
            cpu=1,
            memory=1024,
            disk_size=10000,
            interactive=True,  # TODO change to False
            env=self.env,
            secret_env=self.secret_env,
            entrypoint="/start_mastodon.sh",
            public_ipv6=True,
            **self.solution_metadata,
            solution_uuid=self.solution_id,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

        # expose threebot container
        _id = deployer.expose_and_create_certificate(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            network_name=self.network_view.name,
            trc_secret=self.secret,
            domain=self.domain,
            email=self.user_info_dict["email"],
            solution_ip=self.ip_address,
            solution_port=443,
            enforce_https=False,
            node_id=self.selected_node.node_id,
            solution_uuid=self.solution_id,
            public_key=self.public_key,
            **metadata,
        )
        success = deployer.wait_workload(_id, self)
        if not success:
            raise StopChatFlow(f"Failed to create trc container on node {self.selected_node.node_id}" f" {_id}")

    @chatflow_step(title="Success", disable_previous=True)
    def mastodon_access(self):
        res = f"""\
# mastodon has been deployed successfully: your reservation id is: {self.resv_id}
\n<br />\n
To access  ```ssh root@{self.ip_address}``` .It may take a few minutes.
                """
        self.md_show(res, md=True)


chat = MastodonDeploy
