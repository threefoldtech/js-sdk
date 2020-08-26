import random
import uuid

from nacl.encoding import Base64Encoder
from nacl.public import PrivateKey

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow import deployer, solutions


class TaigaDeploy(GedisChatBot):
    """
    taiga container deploy
    """

    steps = [
        "taiga_name",
        "select_pool",
        "taiga_network",
        "taiga_credentials",
        "container_ip",
        "overview",
        "reservation",
        "container_acess",
    ]
    title = "Taiga"

    def _taiga_start(self):
        self.solution_id = uuid.uuid4().hex
        self.user_form_data = dict()
        self.threebot_name = j.data.text.removesuffix(self.user_info()["username"], ".3bot")
        self.HUB_URL = "https://hub.grid.tf/waleedhammam.3bot/waleedhammam-taiga-latest.flist"
        self.query = {"sru": 2}
        self.solution_metadata = {}

    @chatflow_step(title="Solution name")
    def taiga_name(self):
        self._taiga_start()
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            taiga_solutions = solutions.list_taiga_solutions(sync=False)
            valid = True
            for sol in taiga_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True

    @chatflow_step(title="Pool")
    def select_pool(self):
        cu, su = deployer.calculate_capacity_units(**self.query)
        self.pool_id = deployer.select_pool(self, cu=cu, su=su, **self.query)

    @chatflow_step(title="Network")
    def taiga_network(self):
        self.network_view = deployer.select_network(self)

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

        self.md_show_update("Configuring network and domain settings...")
        self.container_ip()

    def container_ip(self):
        self.selected_node = deployer.schedule_container(self.pool_id, **self.query)
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
                success = deployer.wait_workload(wid, self)
                if not success:
                    raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {wid}")
            self.network_view_copy = self.network_view_copy.copy()
        free_ips = self.network_view_copy.get_node_free_ips(self.selected_node)
        self.ip_address = random.choice(free_ips)

        self.md_show_update("Preparing gateways ...")
        gateways = deployer.list_all_gateways()
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
        full_domain = f"{self.threebot_name}-{self.title.lower()}-{self.solution_name}.{self.domain}"
        while True:
            if j.tools.dnstool.is_free(full_domain):
                self.domain = full_domain
                break
            else:
                random_number = random.randint(1000, 100000)
                full_domain = (
                    f"{self.threebot_name}-{self.title.lower()}-{self.solution_name}-{random_number}.{self.domain}"
                )

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
            "Pool": self.pool_id,
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
                pool_id=self.pool_id,
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
        flask_secret = j.data.idgenerator.chars(10)
        var_dict = {
            "EMAIL_HOST_USER": self.EMAIL_HOST_USER,
            "EMAIL_HOST": self.EMAIL_HOST,
            "TAIGA_HOSTNAME": self.domain,
            "HTTP_PORT": "80",
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
                pool_id=self.pool_id,
                node_id=self.selected_node.node_id,
                network_name=self.network_view.name,
                ip_address=self.ip_address,
                flist=self.HUB_URL,
                cpu=1,
                memory=2 * 1024,
                env=var_dict,
                interactive=False,
                entrypoint="/start_taiga.sh",
                public_ipv6=True,
                disk_size=4 * 1024,
                secret_env={
                    "EMAIL_HOST_PASSWORD": self.EMAIL_HOST_PASSWORD,
                    "PRIVATE_KEY": private_key,
                    "SECRET_KEY": self.SECRET_KEY,
                    "FLASK_SECRET_KEY": flask_secret,
                },
                **self.solution_metadata,
                solution_uuid=self.solution_id,
            )
        )
        self.resv_id = deployer.wait_workload(self.workload_ids[1], self)
        if not self.resv_id:
            solutions.cancel_solution(self.workload_ids)
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

        # expose threebot container
        self.workload_ids.append(
            deployer.expose_and_create_certificate(
                pool_id=self.pool_id,
                gateway_id=self.gateway.node_id,
                network_name=self.network_view.name,
                trc_secret=self.secret,
                domain=self.domain,
                email=self.user_info()["email"],
                solution_ip=self.ip_address,
                solution_port=80,
                enforce_https=True,
                node_id=self.selected_node.node_id,
                solution_uuid=self.solution_id,
                proxy_pool_id=self.gateway_pool.pool_id,
                **self.solution_metadata,
            )
        )
        nginx_wid = deployer.wait_workload(self.workload_ids[2], self)
        if not nginx_wid:
            solutions.cancel_solution(self.workload_ids)
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
