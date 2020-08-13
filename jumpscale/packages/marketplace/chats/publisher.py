import math
import random
import uuid
from textwrap import dedent

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions

FARM_NAMES = ["freefarm"]


class Publisher(MarketPlaceChatflow):
    steps = [
        "start",
        "publisher_name",
        "configuration",
        "publisher_expiration",
        "publisher_payment",
        "infrastructure_setup",
        "domain_select",
        "overview",
        "deploy",
        "success",
    ]
    title = "Publisher"
    welcome_message = "This wizard will help you publish a Wiki, a Website or Blog"
    publishing_chatflow = "publisher"  # chatflow used to deploy the solution

    @chatflow_step()
    def start(self):
        self._validate_user()
        self.flist = "https://hub.grid.tf/ahmed_hanafy_1/ahmedhanafy725-pubtools-trc.flist"
        self.threebot_name = j.data.text.removesuffix(self.user_info()["username"], ".3bot")
        self.solution_id = uuid.uuid4().hex
        self.storage_url = "zdb://hub.grid.tf:9900"
        self.resources = {"cpu": 1, "memory": 1024, "disk_size": 2048}
        self.query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        self.md_show(self.welcome_message, md=True)
        self.solution_metadata = {}
        self.solution_metadata["owner"] = self.user_info()["username"]

    @chatflow_step(title="Solution name")
    def publisher_name(self):
        valid = False
        while not valid:
            self.solution_name_original = deployer.ask_name(self)
            publisher_solutions = solutions.list_publisher_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in publisher_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True
        self.solution_name = f"{self.solution_metadata['owner']}_{self.solution_name_original}"

    @chatflow_step(title="Solution Settings")
    def configuration(self):
        form = self.new_form()
        ttype = form.single_choice("Choose the type", options=["wiki", "www", "blog"], default="wiki", required=True)
        title = form.string_ask("Title", required=True)
        url = form.string_ask("Repository url", required=True)
        branch = form.string_ask("Branch", required=True)
        form.ask("Set configuration")

        self.envars = {
            "TYPE": ttype.value,
            "NAME": "entrypoint",
            "TITLE": title.value,
            "URL": url.value,
            "BRANCH": branch.value,
            "EMAIL": self.user_info()["email"],
        }

    @chatflow_step(title="Expiration Time")
    def publisher_expiration(self):
        self.expiration = deployer.ask_expiration(self)
        print(self.expiration)

    @chatflow_step(title="Payment currency")
    def publisher_payment(self):
        self.solution_currency = self.single_choice(
            "Please select the currency you want to pay with.", ["FreeTFT", "TFT", "TFTA"], required=True
        )

    @chatflow_step(title="Setup")
    def infrastructure_setup(self):
        available_farms = []
        for farm_name in FARM_NAMES:
            available, _, _, _, _ = deployer.check_farm_capacity(
                farm_name, currencies=[self.solution_currency], **self.query
            )
            if available:
                available_farms.append(farm_name)

        self.farm_name = random.choice(available_farms)

        user_networks = solutions.list_network_solutions(self.solution_metadata["owner"])
        networks_names = [n["Name"] for n in user_networks]
        if "apps" in networks_names:
            # old user
            self.pool_info = deployer.create_solution_pool(
                bot=self,
                username=self.solution_metadata["owner"],
                farm_name=self.farm_name,
                expiration=self.expiration,
                currency=self.solution_currency,
                **self.query,
            )
        else:
            # new user
            self.pool_info, self.wgconf = deployer.init_new_user(
                bot=self,
                username=self.solution_metadata["owner"],
                farm_name=self.farm_name,
                expiration=self.expiration,
                currency=self.solution_currency,
                **self.query,
            )

        if not self.pool_info:
            raise StopChatFlow(f"Failed to deploy solution {self.pool_info}")

        # get ip address
        self.network_view = deployer.get_network_view(f"{self.solution_metadata['owner']}_apps")
        self.ip_address = None
        while not self.ip_address:
            self.selected_node = deployer.schedule_container(self.pool_info.reservation_id, **self.query)
            result = deployer.add_network_node(
                self.network_view.name,
                self.selected_node,
                self.pool_info.reservation_id,
                self.network_view,
                bot=self,
                owner=self.solution_metadata.get("owner"),
            )
            if result:
                self.md_show_update("Deploying Network on Nodes....")
                for wid in result["ids"]:
                    success = deployer.wait_workload(wid)
                    if not success:
                        raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {wid}")
                self.network_view = self.network_view.copy()
            self.ip_address = self.network_view.get_free_ip(self.selected_node)

    @chatflow_step(title="Domain")
    def domain_select(self):
        self.md_show_update("Preparing a node to deploy on ...")
        self.selected_node = deployer.schedule_container(self.pool_info.reservation_id, **self.query)
        self.md_show_update("Preparing gateways ...")
        gateways = deployer.list_all_gateways(self.user_info()["username"])
        if not gateways:
            raise StopChatFlow("There are no available gateways in the farms bound to your pools.")

        domains = dict()
        for gw_dict in gateways.values():
            gateway = gw_dict["gateway"]
            for domain in gateway.managed_domains:
                domains[domain] = gw_dict

        self.domain = random.choice(list(domains.keys()))

        self.gateway = domains[self.domain]["gateway"]
        self.gateway_pool = domains[self.domain]["pool"]

        full_domain = f"{self.threebot_name}-{self.publishing_chatflow}-{self.solution_name_original}.{self.domain}"
        while True:
            if j.tools.dnstool.is_free(full_domain):
                self.domain = full_domain
                break
            else:
                random_number = random.randint(1000, 100000)
                full_domain = f"{self.threebot_name}-{self.publishing_chatflow}-{self.solution_name_original}-{random_number}.{self.domain}"

        self.envars["DOMAIN"] = self.domain
        self.addresses = []
        for ns in self.gateway.dns_nameserver:
            self.addresses.append(j.sals.nettools.get_host_by_name(ns))

        self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

    @chatflow_step(title="Confirmation")
    def overview(self):
        info = {"Solution name": self.solution_name, "domain": self.domain}
        self.md_show_confirm(info)

    @chatflow_step(title="Reservation", disable_previous=True)
    def deploy(self):
        # 1- deploy network on selected node
        metadata = {
            "name": self.solution_name,
            "form_info": {"Solution name": self.solution_name, "chatflow": self.publishing_chatflow},
        }
        self.solution_metadata.update(metadata)
        self.workload_ids = []
        self.network_view = self.network_view.copy()
        result = deployer.add_network_node(
            self.network_view.name,
            self.selected_node,
            self.pool_info.reservation_id,
            self.network_view,
            bot=self,
            owner=self.solution_metadata.get("owner"),
        )
        if result:
            for wid in result["ids"]:
                success = deployer.wait_workload(wid, self)
                if not success:
                    raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {wid}")
        self.network_view_copy = self.network_view.copy()
        self.ip_address = self.network_view_copy.get_free_ip(self.selected_node)

        # 2- reserve subdomain
        self.workload_ids.append(
            deployer.create_subdomain(
                pool_id=self.gateway_pool.pool_id,
                gateway_id=self.gateway.node_id,
                subdomain=self.domain,
                addresses=self.addresses,
                solution_uuid=self.solution_id,
                **self.solution_metadata,
            )
        )
        success = deployer.wait_workload(self.workload_ids[0], self)
        if not success:
            raise StopChatFlow(
                f"Failed to create subdomain {self.domain} on gateway {self.gateway.node_id} {self.workload_ids[0]}"
            )

        # 3- reserve tcp proxy
        self.workload_ids.append(
            deployer.create_proxy(
                pool_id=self.gateway_pool.pool_id,
                gateway_id=self.gateway.node_id,
                domain_name=self.domain,
                trc_secret=self.secret,
                solution_uuid=self.solution_id,
                **self.solution_metadata,
            )
        )
        success = deployer.wait_workload(self.workload_ids[1], self)
        if not success:
            solutions.cancel_solution(self.user_info()["username"], self.workload_ids)
            raise StopChatFlow(
                f"Failed to create reverse proxy {self.domain} on gateway {self.gateway.node_id} {self.workload_ids[1]}"
            )

        # 4- deploy container
        self.envars["TRC_REMOTE"] = f"{self.gateway.dns_nameserver[0]}:{self.gateway.tcp_router_port}"
        secret_env = {"TRC_SECRET": self.secret}
        self.workload_ids.append(
            deployer.deploy_container(
                pool_id=self.pool_info.reservation_id,
                node_id=self.selected_node.node_id,
                network_name=self.network_view.name,
                ip_address=self.ip_address,
                flist=self.flist,
                env=self.envars,
                cpu=self.resources["cpu"],
                memory=self.resources["memory"],
                disk_size=self.resources["disk_size"],
                entrypoint="/bin/bash /start.sh",
                secret_env=secret_env,
                interactive=False,
                solution_uuid=self.solution_id,
                public_ipv6=True,
                **self.solution_metadata,
            )
        )
        if not success:
            solutions.cancel_solution(self.user_info()["username"], self.workload_ids)
            raise StopChatFlow(
                f"Failed to create container on node {self.selected_node.node_id} {self.workload_ids[2]}"
            )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        if hasattr(self, "wgconf"):
            self.download_file(msg=f"<pre>{self.wgconf}</pre>", data=self.wgconf, filename="apps.conf", html=True)
        message = f"""## Deployment success
\n<br>\n
You can access your container using:

- Domain: <a href="https://{self.domain}" target="_blank">https://{self.domain}</a>

- IP address: `{self.ip_address}`
        """
        self.md_show(dedent(message), md=True)


chat = Publisher
