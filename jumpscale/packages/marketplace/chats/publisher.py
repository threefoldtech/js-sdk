import math
import toml
import uuid
from textwrap import dedent
from jumpscale.clients.explorer.models import DiskType
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.marketplace import deployer, MarketPlaceChatflow


class Publisher(MarketPlaceChatflow):
    SOLUTION_TYPE = SolutionType.Publisher

    steps = [
        "welcome",
        "solution_name",
        "choose_network",
        "configuration",
        "public_key_get",
        "container_node_id",
        "container_farm",
        "container_ip",
        "expiration_time",
        "domain_select",
        "overview",
        "deploy",
        "success",
    ]

    title = "Publisher"

    @chatflow_step(title="Welcome")
    def welcome(self):
        self.storage_url = "zdb://hub.grid.tf:9900"
        self._validate_user()
        self._tid = None
        self.user_form_data = dict()
        self.metadata = dict()
        self.query = dict()
        self.env = dict()
        self.secret_env = dict()
        self.resources = {"cpu": 1, "memory": 1024, "rootfs": 2048}
        self.flist_url = "https://hub.grid.tf/ahmed_hanafy_1/ahmedhanafy725-pubtools-trc.flist"
        self.md_show("This wizard will help you publish a Wiki, a Website or Blog", md=True)

    @chatflow_step(title="Solution name")
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

    @chatflow_step(title="Domain")
    def domain_select(self):
        self.gateways = {}
        for g in filter(j.sals.zos.nodes_finder.filter_is_up, j.sals.zos._explorer.gateway.list()):
            if self.currency == "FreeTFT" and not g.free_to_use:
                continue
            self.gateways[g.node_id] = g

        if not self.gateways:
            self.stop(f"There are no gateways that support the currency {self.currency}")

        domains = dict()
        for gateway in self.gateways.values():
            for domain in gateway.managed_domains:
                domains[domain] = gateway

        self.domain = self.single_choice(
            "Please choose the domain you wish to use", list(domains.keys()), required=True
        )
        while True:
            self.sub_domain = self.string_ask(
                f"Please choose the sub domain you wish to use, eg <subdomain>.{self.domain}", required=True
            )
            if j.tools.dnstool.is_free(self.sub_domain + "." + self.domain):
                break
            else:
                self.md_show(f"the specified domain {self.sub_domain + '.' + self.domain} is already registered")
        self.gateway = domains[self.domain]
        self.domain = f"{self.sub_domain}.{self.domain}"

        self.envars["DOMAIN"] = self.domain

        self.addresses = []
        for ns in self.gateway.dns_nameserver:
            self.addresses.append(j.sals.nettools.get_host_by_name(ns))

        self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

    @chatflow_step(title="Confirmation")
    def overview(self):
        info = {"Solution name": self.name, "Expiration time": j.data.time.get(self.expiration).humanize()}
        self.md_show_confirm(info)

    @chatflow_step(title="Payment", disable_previous=True)
    def deploy(self):
        self.reservation = j.sals.zos.reservation_create()
        j.sals.zos._gateway.sub_domain(self.reservation, self.gateway.node_id, self.domain, self.addresses)
        j.sals.zos._gateway.tcp_proxy_reverse(self.reservation, self.gateway.node_id, self.domain, self.secret)
        self.md_show_update("Preparing Network on Node.....")
        self.network = self.network_copy
        self.network.update(self.user_info()["username"], currency=self.currency, bot=self)
        self.envars["SSHKEY"] = self.user_form_data["Public key"]
        self.envars["TRC_REMOTE"] = f"{self.gateway.dns_nameserver[0]}:{self.gateway.tcp_router_port}"

        secret_env = {}
        secret_encrypted = j.sals.zos.container.encrypt_secret(self.node_selected.node_id, self.secret)
        secret_env["TRC_SECRET"] = secret_encrypted

        j.sals.zos.container.create(
            reservation=self.reservation,
            node_id=self.node_selected.node_id,
            network_name=self.network.name,
            ip_address=self.ip_address,
            flist=self.flist_url,
            storage_url=self.storage_url,
            disk_type=DiskType.SSD.value,
            disk_size=self.resources["rootfs"],
            env=self.envars,
            interactive=False,
            entrypoint="/bin/bash /start.sh",
            cpu=self.resources["cpu"],
            memory=self.resources["memory"],
            secret_env=secret_env,
        )

        metadata = {"Solution name": self.name, "version": 1, "chatflow": "publisher"}

        res = deployer.get_solution_metadata(self.name, self.SOLUTION_TYPE, self.user_info()["username"], metadata)

        reservation = j.sals.reservation_chatflow.add_reservation_metadata(self.reservation, res)

        self.reservation_id = deployer.register_and_pay_reservation(
            reservation, self.expiration, customer_tid=j.core.identity.me.tid, currency=self.currency, bot=self
        )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        message = f"""
        You can access your container using:
        Reservation ID: {self.reservation_id}
        Domain: {self.domain}
        IP address: {self.ip_address}
        """
        self.md_show(dedent(message), md=True)


chat = Publisher
