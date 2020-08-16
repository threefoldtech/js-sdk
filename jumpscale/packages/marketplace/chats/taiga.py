import math
import random
import uuid

from nacl.encoding import Base64Encoder
from nacl.public import PrivateKey

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions

FARM_NAMES = ["freefarm"]


class TaigaDeploy(MarketPlaceChatflow):
    """
    taiga container deploy
    """

    steps = [
        "taiga_start",
        "taiga_name",
        "taiga_credentials",
        "taiga_expiration",
        "taiga_payment",
        "infrastructure_setup",
        "overview",
        "reservation",
        "container_acess",
    ]
    title = "Taiga"

    @chatflow_step()
    def taiga_start(self):
        self._validate_user()
        self.solution_id = uuid.uuid4().hex
        self.user_form_data = dict()
        self.threebot_name = j.data.text.removesuffix(self.user_info()["username"], ".3bot")
        self.HUB_URL = "https://hub.grid.tf/waleedhammam.3bot/waleedhammam-taiga-latest.flist"
        self.md_show("# This wizard wil help you deploy an taiga solution", md=True)
        self.resources = {"cpu": 1, "memory": 2 * 1024, "disk_size": 4 * 1024}
        self.query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        self.solution_metadata = {}
        self.solution_metadata["owner"] = self.user_info()["username"]

    @chatflow_step(title="Solution name")
    def taiga_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            monitoring_solutions = solutions.list_taiga_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in monitoring_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True
        self.solution_name = f"{self.solution_metadata['owner']}_{self.solution_name}"

    @chatflow_step(title="Taiga Setup")
    def taiga_credentials(self):
        form = self.new_form()
        EMAIL_HOST_USER = form.string_ask("Please add the host email name for your solution.", required=True)
        EMAIL_HOST = form.string_ask(
            "Please add the smtp host example: `smtp.gmail.com`", default="smtp.gmail.com", required=True, md=True
        )
        EMAIL_HOST_PASSWORD = form.secret_ask("Please add the host email password", required=True)

        SECRET_KEY = form.secret_ask("Please add the secret for your solution", required=True)
        form.ask()
        self.EMAIL_HOST_USER = EMAIL_HOST_USER.value
        self.EMAIL_HOST = EMAIL_HOST.value
        self.EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD.value
        self.SECRET_KEY = SECRET_KEY.value

    @chatflow_step(title="Expiration Time")
    def taiga_expiration(self):
        self.expiration = deployer.ask_expiration(self)
        print(self.expiration)

    @chatflow_step(title="Payment currency")
    def taiga_payment(self):
        self.solution_currency = self.single_choice(
            "Please select the currency you want to pay with.", ["FreeTFT", "TFT", "TFTA"], required=True
        )

    @chatflow_step(title="Setup")
    def infrastructure_setup(self):
        self.md_show_update("Setup network and domain settings...")
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
            result = deployer.wait_pool_payment(self, self.pool_info.reservation_id)
            if not result:
                raise StopChatFlow(f"Failed to reserve pool {self.pool_info.reservation_id}")
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
        self.container_ip()

    def container_ip(self):
        self.selected_node = deployer.schedule_container(self.pool_info.reservation_id, **self.query)
        self.network_view_copy = self.network_view.copy()
        result = deployer.add_network_node(
            self.network_view.name,
            self.selected_node,
            self.pool_info.reservation_id,
            self.network_view_copy,
            bot=self,
            owner=self.solution_metadata.get("owner"),
        )
        if result:
            for wid in result["ids"]:
                success = deployer.wait_workload(wid, self)
                if not success:
                    raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {wid}")
            self.network_view_copy = self.network_view_copy.copy()
        free_ips = self.network_view_copy.get_node_free_ips(self.selected_node)
        self.ip_address = random.choice(free_ips)

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
        self.solution_name = self.solution_name.replace(".", "").replace("_", "-")
        full_domain = f"{self.title.lower()}-{self.solution_name}.{self.domain}"
        while True:
            if j.tools.dnstool.is_free(full_domain):
                self.domain = full_domain
                break
            else:
                random_number = random.randint(1000, 100000)
                full_domain = f"{self.title.lower()}-{self.solution_name}-{random_number}.{self.domain}"

        self.addresses = []
        for ns in self.gateway.dns_nameserver:
            self.addresses.append(j.sals.nettools.get_host_by_name(ns))

        self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

    @chatflow_step(title="Confirmation")
    def overview(self):
        self.metadata = {
            "Solution Name": self.solution_name,
            "Network": self.network_view.name,
            "Node ID": self.selected_node.node_id,
            "Pool": self.pool_info.reservation_id,
            "IP Address": self.ip_address,
            "Domain": self.domain,
        }
        self.md_show_confirm(self.metadata)

    @chatflow_step(title="Reservation")
    def reservation(self):
        self.workload_ids = []

        # reserve subdomain
        subdomain_wid = self.workload_ids.append(
            deployer.create_subdomain(
                pool_id=self.pool_info.reservation_id,
                gateway_id=self.gateway.node_id,
                subdomain=self.domain,
                addresses=self.addresses,
                solution_uuid=self.solution_id,
                **self.solution_metadata,
            )
        )
        subdomain_wid = deployer.wait_workload(self.workload_ids[0], self)

        if not subdomain_wid:
            raise StopChatFlow(
                f"Failed to create subdomain {self.domain} on gateway {self.gateway.node_id} {self.workload_ids[0]}"
            )

        private_key = PrivateKey.generate().encode(Base64Encoder).decode()
        var_dict = {
            "EMAIL_HOST_USER": self.EMAIL_HOST_USER,
            "EMAIL_HOST": self.EMAIL_HOST,
            "TAIGA_HOSTNAME": self.domain,
            "HTTP_PORT": "80",
            "FLASK_SECRET_KEY": "flask",
            "THREEBOT_URL": "https://login.threefold.me",
            "OPEN_KYC_URL": "https://openkyc.live/verification/verify-sei",
        }
        metadata = {
            "name": self.solution_name,
            "form_info": {"Solution name": self.solution_name, "chatflow": "taiga",},
        }
        self.solution_metadata.update(metadata)

        self.workload_ids.append(
            deployer.deploy_container(
                pool_id=self.pool_info.reservation_id,
                node_id=self.selected_node.node_id,
                network_name=self.network_view.name,
                ip_address=self.ip_address,
                flist=self.HUB_URL,
                cpu=self.resources["cpu"],
                memory=self.resources["memory"],
                disk_size=self.resources["disk_size"],
                env=var_dict,
                interactive=False,
                entrypoint="/start_taiga.sh",
                public_ipv6=True,
                secret_env={
                    "EMAIL_HOST_PASSWORD": self.EMAIL_HOST_PASSWORD,
                    "PRIVATE_KEY": private_key,
                    "SECRET_KEY": self.SECRET_KEY,
                },
                **self.solution_metadata,
                solution_uuid=self.solution_id,
            )
        )
        self.resv_id = deployer.wait_workload(self.workload_ids[1], self)
        if not self.resv_id:
            solutions.cancel_solution(self.user_info()["username"], self.workload_ids)
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

        # expose threebot container
        self.workload_ids.append(
            deployer.expose_and_create_certificate(
                pool_id=self.pool_info.reservation_id,
                gateway_id=self.gateway.node_id,
                network_name=self.network_view.name,
                trc_secret=self.secret,
                domain=self.domain,
                email=self.user_info()["email"],
                solution_ip=self.ip_address,
                solution_port=80,
                enforce_https=True,
                test_cert=False,
                node_id=self.selected_node.node_id,
                solution_uuid=self.solution_id,
                proxy_pool_id=self.gateway_pool.pool_id,
                **metadata,
            )
        )
        nginx_wid = deployer.wait_workload(self.workload_ids[2], self)
        if not nginx_wid:
            solutions.cancel_solution(self.user_info()["username"], self.workload_ids)
            raise StopChatFlow(f"Failed to create trc container on node {self.selected_node.node_id} {nginx_wid}")

    @chatflow_step(title="Success", disable_previous=True)
    def container_acess(self):
        res = f"""\
# Taiga has been deployed successfully:
\n<br />\n
your reservation id is: `{self.workload_ids[1]}`
\n<br />\n
your container ip is: `{self.ip_address}`
\n<br />\n
open Taiga from browser at <a href="https://{self.domain}" target="_blank">https://{self.domain}</a>
\n<br />\n
- It may take few minutes to load.
                """
        self.md_show(res, md=True)


chat = TaigaDeploy
