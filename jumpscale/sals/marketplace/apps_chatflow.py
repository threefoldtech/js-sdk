import uuid
import random
import requests
from textwrap import dedent

from jumpscale.core.base import StoredFactory
from jumpscale.loader import j
from .solutions import solutions
from .deployer import deployer
from .chatflow import MarketPlaceChatflow
from jumpscale.packages.marketplace.bottle.models import UserEntry
from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step


class MarketPlaceAppsChatflow(MarketPlaceChatflow):
    def _init_solution(self):
        self._validate_user()
        self.solution_id = uuid.uuid4().hex
        self.solution_metadata = {}
        self.solution_metadata["owner"] = self.user_info()["username"]
        self.threebot_name = j.data.text.removesuffix(self.user_info()["username"], ".3bot")

    def _wgconf_show_check(self):
        if hasattr(self, "wgconf"):
            msg = f"""<h3> Use the following template to configure your wireguard connection. This will give you access to your network. </h3>
<h3> Make sure you have <a target="_blank" href="https://www.wireguard.com/install/">wireguard</a> installed </h3>
<br>
<pre style="text-align:center">{self.wgconf}</pre>
<br>
<h3>navigate to where the config is downloaded and start your connection using "wg-quick up ./apps.conf"</h3>
"""
            self.download_file(msg=msg, data=self.wgconf, filename="apps.conf", html=True)

    def _get_pool(self):
        available_farms = []
        farm_names = [f.name for f in j.sals.zos._explorer.farms.list()]
        for farm_name in farm_names:
            available, _, _, _, _ = deployer.check_farm_capacity(farm_name, currencies=[self.currency], **self.query)
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
                currency=self.currency,
                **self.query,
            )
            result = deployer.wait_pool_payment(self, self.pool_info.reservation_id)
            if not result:
                raise StopChatFlow(f"Waiting for pool payment timedout. pool_id: {self.pool_info.reservation_id}")
        else:
            # new user
            self.pool_info, self.wgconf = deployer.init_new_user(
                bot=self,
                username=self.solution_metadata["owner"],
                farm_name=self.farm_name,
                expiration=self.expiration,
                currency=self.currency,
                **self.query,
            )

        if not self.pool_info:
            raise StopChatFlow(f"Failed to deploy solution {self.pool_info}")
        self.pool_id = self.pool_info.reservation_id
        return self.pool_id

    def _deploy_network(self):
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
                    success = deployer.wait_workload(wid, self, breaking_node_id=self.selected_node.node_id)
                    if not success:
                        raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {wid}")
                self.network_view = self.network_view.copy()
            self.ip_address = self.network_view.get_free_ip(self.selected_node)
        return self.ip_address

    def _get_domain(self):
        # get domain for the ip address
        self.md_show_update("Preparing gateways ...")
        gateways = deployer.list_all_gateways(self.user_info()["username"])
        if not gateways:
            raise StopChatFlow("There are no available gateways in the farms bound to your pools.")

        domains = dict()
        for gw_dict in gateways.values():
            gateway = gw_dict["gateway"]
            for domain in gateway.managed_domains:
                try:
                    if j.sals.crtsh.has_reached_limit(domain):
                        continue
                except requests.exceptions.HTTPError:
                    continue
                domains[domain] = gw_dict

        if not domains:
            raise StopChatFlow("Letsencrypt limit has been reached on all gateways")

        self.domain = random.choice(list(domains.keys()))

        self.gateway = domains[self.domain]["gateway"]
        self.gateway_pool = domains[self.domain]["pool"]

        solution_name = self.solution_name.replace(".", "").replace("_", "-")
        # check if domain name is free or append random number
        full_domain = f"{solution_name}.{self.domain}"
        while True:
            if j.tools.dnstool.is_free(full_domain):
                self.domain = full_domain
                break
            else:
                random_number = random.randint(1000, 100000)
                full_domain = f"{solution_name}-{random_number}.{self.domain}"

        self.addresses = []
        for ns in self.gateway.dns_nameserver:
            self.addresses.append(j.sals.nettools.get_host_by_name(ns))

        self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"
        return self.domain

    @chatflow_step(title="Solution Name")
    def get_solution_name(self):
        self._init_solution()
        valid = False
        while not valid:
            self.solution_name = self.string_ask(
                "Please enter a name for your solution (Can be used to prepare domain for you and needed to track your solution on the grid )",
                required=True,
                is_identifier=True,
            )
            method = getattr(solutions, f"list_{self.SOLUTION_TYPE}_solutions")
            solutions_list = method(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in solutions_list:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True
        self.solution_name = f"{self.solution_metadata['owner']}-{self.solution_name}"

    @chatflow_step(title="Payment currency")
    def payment_currency(self):
        self.currency = self.single_choice(
            "Please select the currency you want to pay with.", ["FreeTFT", "TFT", "TFTA"], required=True
        )

    @chatflow_step(title="Expiration Time")
    def solution_expiration(self):
        self.expiration = deployer.ask_expiration(self)

    @chatflow_step(title="Setup")
    def infrastructure_setup(self):
        self._get_pool()
        self._deploy_network()
        self._get_domain()

    @chatflow_step(title="Initializing", disable_previous=True)
    def initializing(self):
        self.md_show_update(f"Initializing your {self.SOLUTION_TYPE}...")

        if not j.sals.reservation_chatflow.wait_http_test(
            f"https://{self.domain}", timeout=600, verify=not j.config.get("TEST_CERT")
        ):
            self.stop(
                f"""\
Failed to initialize Mattermost, please contact support with this information:
Node:{self.selected_node.node_id},
Ip Address: {self.ip_address},
Reservation Id: {self.resv_id},
Pool Id : {self.pool_id},
Domain : {self.domain}
                """
            )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        self._wgconf_show_check()
        message = f"""\
# Congratulations! Your own instance from {self.SOLUTION_TYPE} deployed successfully:
\n<br />\n
- You can access it via the browser using: <a href="https://{self.domain}" target="_blank">https://{self.domain}</a>
\n<br />\n
- This domain maps to your container with ip: `{self.ip_address}`
                """
        self.md_show(dedent(message), md=True)
