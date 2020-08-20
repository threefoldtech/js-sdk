from jumpscale.packages.tfgrid_solutions.chats.solution_expose import SolutionExpose as BaseSolutionExpose, kinds
from jumpscale.sals.marketplace import deployer, Network
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.loader import j
import uuid
from jumpscale.sals.chatflows.chatflows import StopChatFlow
from jumpscale.packages.marketplace.bottle.models import UserEntry
from jumpscale.core.base import StoredFactory


class SolutionExpose(BaseSolutionExpose):
    title = "Solution Expose"

    def get_tid(self):
        if not self._tid:
            user = j.sals.reservation_chatflow.validate_user(self.user_info())
            self._tid = user.id
        return self._tid

    @chatflow_step(title="Expiration time")
    def expiration_time(self):
        super().expiration_time()
        # DONT REMOVE THIS until capacity pool migration is done on mainnet
        while self.expiration > 1599091200:
            self.md_show(
                "the maximum expiration in marketplace is currently 09/03/2020 @ 12:00am (UTC). please click next to try again"
            )
            super().expiration_time()

    def _validate_user(self):
        tname = self.user_info()["username"]
        user_factory = StoredFactory(UserEntry)
        explorer_url = j.core.identity.me.explorer.url

        if "testnet" in explorer_url:
            explorer_name = "testnet"
        elif "devnet" in explorer_url:
            explorer_name = "devnet"
        elif "explorer.grid.tf" in explorer_url:
            explorer_name = "mainnet"
        else:
            raise StopChatFlow(f"Unsupported explorer {explorer_url}")
        instance_name = f"{explorer_name}_{tname.replace('.3bot', '')}"
        if instance_name in user_factory.list_all():
            user_entry = user_factory.get(instance_name)
            if not user_entry.has_agreed:
                raise StopChatFlow(
                    f"You must accept terms and conditions before using this solution. please head towards the main page to read our terms"
                )
        else:
            raise StopChatFlow(
                f"You must accept terms and conditions before using this solution. please head towards the main page to read our terms"
            )

    @chatflow_step(title="Welcome")
    def deployment_start(self):
        self._validate_user()
        self._tid = None
        self.user_form_data = dict()
        self.metadata = dict()
        self.query = dict()
        self.env = dict()
        self.secret_env = dict()
        self.md_show(f"### Welcome to solution expose chatflow. click next to proceed to the deployment")

    @chatflow_step(title="Solution type")
    def solution_type(self):
        self.kind = self.single_choice("Please choose the solution type", list(kinds.keys()), required=True)
        self.user_form_data["kind"] = self.kind
        self.md_show_update("Finding Solutions....")

        sol_type = kinds[self.kind]
        solutions = deployer.list_solutions(self.user_info()["username"], sol_type, reload=True)

        self.sols = {sol["name"]: sol for sol in solutions}

    @chatflow_step(title="Solution to be exposed")
    def exposed_solution(self):
        solution_name = self.single_choice(
            "Please choose the solution to expose", list(self.sols.keys()), required=True
        )
        solution = self.sols[solution_name]
        self.user_form_data["Solution name"] = solution_name
        self.reservation_data = solution["reservation_obj"].data_reservation.to_dict()
        self.solution_currency = self.reservation_data["currencies"][0]

    @chatflow_step(title="Domain")
    def domain_1(self):
        # List all available domains
        self.md_show_update("Listing Available Domains....")
        free_to_use = False
        if "FreeTFT" == self.solution_currency:
            self.gateways = {
                g.node_id: g
                for g in j.sals.zos._explorer.gateway.list()
                if g.free_to_use and j.sals.zos.nodes_finder.filter_is_up(g)
            }
        else:
            self.gateways = {
                g.node_id: g for g in j.sals.zos._explorer.gateway.list() if j.sals.zos.nodes_finder.filter_is_up(g)
            }

        user_domains = deployer.list_solutions(self.user_info()["username"], SolutionType.Exposed)
        self.user_domains = {}
        for dom in user_domains:
            if dom["reservation_obj"].data_reservation.currencies[0] == self.solution_currency:
                self.user_domains[dom["name"]] = dom
        domain_ask_list = []
        for dom in self.user_domains:
            if self.gateways.get(self.user_domains[dom]["reservation_obj"].node_id):
                domain_ask_list.append(f"Delegated Domain: {dom}")

        self.managed_domains = dict()
        for g in self.gateways.values():
            for dom in g.managed_domains:
                self.managed_domains[dom] = g
                domain_ask_list.append(f"Managed Domain: {dom}")
        domain_ask_list.append("Custom Domain")

        self.chosen_domain = self.single_choice("Please choose the domain you wish to use", domain_ask_list)

    @chatflow_step(title="Confirmation", disable_previous=True)
    def confirmation(self):
        query = {"mru": 1, "cru": 1, "currency": self.solution_currency, "sru": 1}
        node_selected = j.sals.reservation_chatflow.get_nodes(1, **query)[0]
        self.md_show_update("Preparing Network on Node.....")
        network = j.sals.reservation_chatflow.get_network(self, j.core.identity.me.tid, self.network_name)
        # get MarketPlace Network object
        network = Network(
            network._network,
            network._expiration,
            self,
            j.sals.zos.reservation_list(),
            network.currency,
            network.resv_id,
        )
        network.add_node(node_selected)
        network.update(self.user_info()["username"], currency=self.solution_currency, bot=self)
        self.md_show_update("Preparing TCPRouter Container.....")
        ip_address = network.get_free_ip(node_selected)
        if not ip_address:
            raise j.exceptions.Value("No available free ips")

        secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"
        self.user_form_data["Secret"] = secret
        secret_env = {}
        secret_encrypted = j.sals.zos.container.encrypt_secret(node_selected.node_id, self.user_form_data["Secret"])
        secret_env["TRC_SECRET"] = secret_encrypted
        remote = f"{self.domain_gateway.dns_nameserver[0]}:{self.domain_gateway.tcp_router_port}"
        local = f"{self.container_address}:{self.user_form_data['Port']}"
        localtls = f"{self.container_address}:{self.user_form_data['tls-port']}"
        entrypoint = f"/bin/trc -local {local} -local-tls {localtls} -remote {remote}"

        j.sals.zos.container.create(
            reservation=self.reservation,
            node_id=node_selected.node_id,
            network_name=self.network_name,
            ip_address=ip_address,
            flist="https://hub.grid.tf/tf-official-apps/tcprouter:latest.flist",
            entrypoint=entrypoint,
            secret_env=secret_env,
        )

        message = """
<h4>Click next to proceed with the payment</h4>
Tcp routers are used in the process of being able to expose your solutions. This payment is to deploy a container with a <a target="_blank" href="https://github.com/threefoldtech/tcprouter#reverse-tunneling">tcprouter client</a> on it.
"""
        self.md_show_confirm(self.user_form_data, message=message, html=True)

    @chatflow_step(title="Reserve TCP router container", disable_previous=True)
    def tcp_router_reservation(self):
        # create proxy
        self.md_show_update("Preparing TCP Reverse Proxy.....")
        j.sals.zos._gateway.tcp_proxy_reverse(
            self.reservation, self.domain_gateway.node_id, self.user_form_data["Domain"], self.user_form_data["Secret"]
        )

        metadata = deployer.get_solution_metadata(
            self.user_form_data["Solution name"],
            SolutionType.Exposed,
            self.user_info()["username"],
            {"Solution expiration": self.expiration},
        )
        self.reservation = j.sals.reservation_chatflow.add_reservation_metadata(self.reservation, metadata)

        resv_id = deployer.register_and_pay_reservation(
            self.reservation,
            self.expiration,
            customer_tid=j.core.identity.me.tid,
            currency=self.solution_currency,
            bot=self,
        )

    @chatflow_step(title="Success", disable_previous=True)
    def success(self):
        domain = self.user_form_data["Domain"]
        res_md = f"Use this Gateway to connect to your exposed solutions `{domain}`"
        self.md_show(res_md)


chat = SolutionExpose
