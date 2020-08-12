import math
import toml
import uuid
from textwrap import dedent
from jumpscale.clients.explorer.models import DiskType
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType


class Publisher(GedisChatBot):
    steps = [
        "start",
        "select_network",
        "set_solution_name",
        "configuration",
        "upload_public_key",
        "select_node",
        "select_farm",
        "select_ip_address",
        "select_expiration_time",
        "domain_select",
        "overview",
        "deploy",
        "success",
    ]

    title = "Publisher"

    @chatflow_step()
    def start(self):
        self.solution_currency = "TFT"
        self.storage_url = "zdb://hub.grid.tf:9900"
        self.resources = {"cpu": 1, "memory": 1024, "rootfs": 2048}
        self.user_info = self.user_info()
        self.md_show("This wizard will help you publish a Wiki, a Website or Blog", md=True)
        j.sals.reservation_chatflow.validate_user(self.user_info)

    @chatflow_step(title="Network")
    def select_network(self):
        self.network = j.sals.reservation_chatflow.select_network(self, j.core.identity.me.tid)

    @chatflow_step(title="Solution name")
    def set_solution_name(self):
        self.solution_name = self.string_ask("Please enter a name for your container", required=True)

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
            "EMAIL": self.user_info["email"],
        }

    @chatflow_step(title="Access key")
    def upload_public_key(self):
        self.public_key = self.upload_file(
            "Please upload your public ssh key, this will allow you to access your container using ssh", required=True
        ).strip()

    @chatflow_step(title="Select Node")
    def select_node(self):
        self.query = dict(
            currency=self.network.currency,
            cru=self.resources["cpu"],
            mru=math.ceil(self.resources["memory"] / 1024),
            sru=math.ceil(self.resources["rootfs"] / 1024),
        )

        self.nodeid = self.string_ask(
            "Please enter the nodeid you would like to deploy on if left empty a node will be chosen for you"
        )
        while self.nodeid:
            try:
                self.node_selected = j.sals.reservation_chatflow.validate_node(
                    self.nodeid, self.query, self.network.currency
                )
                break

            except (j.exceptions.Value, j.exceptions.NotFound) as e:
                message = "<br> Please enter a different nodeid to deploy on or leave it empty"
                self.nodeid = self.string_ask(str(e) + message, html=True, retry=True)

    @chatflow_step(title="Select farm")
    def select_farm(self):
        if not self.nodeid:
            farms = j.sals.reservation_chatflow.get_farm_names(1, self, **self.query)
            self.node_selected = j.sals.reservation_chatflow.get_nodes(1, farm_names=farms, **self.query)[0]

    @chatflow_step(title="Select IP")
    def select_ip_address(self):
        self.network_copy = self.network.copy(j.core.identity.me.tid)
        self.network_copy.add_node(self.node_selected)
        self.ip_address = self.network_copy.ask_ip_from_node(
            self.node_selected, "Please choose IP Address for your solution"
        )

    @chatflow_step(title="Expiration time")
    def select_expiration_time(self):
        self.expiration = self.datetime_picker(
            "Please enter solution expiration time.",
            required=True,
            min_time=[3600, "Date/time should be at least 1 hour from now"],
            default=j.data.time.get().timestamp + 3900,
        )

    @chatflow_step(title="Domain")
    def domain_select(self):
        self.gateways = {}

        for g in filter(j.sals.zos.nodes_finder.filter_is_up, j.sals.zos._explorer.gateway.list()):
            if self.network.currency == "FreeTFT" and not g.free_to_use:
                continue
            self.gateways[g.node_id] = g
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
        info = {"Solution name": self.solution_name, "Expiration time": j.data.time.get(self.expiration).humanize()}
        self.md_show_confirm(info)

    @chatflow_step(title="Payment", disable_previous=True)
    def deploy(self):
        self.reservation = j.sals.zos.reservation_create()
        j.sals.zos._gateway.sub_domain(self.reservation, self.gateway.node_id, self.domain, self.addresses)
        j.sals.zos._gateway.tcp_proxy_reverse(self.reservation, self.gateway.node_id, self.domain, self.secret)

        self.network = self.network_copy
        self.network.update(j.core.identity.me.tid, currency=self.query["currency"], bot=self)

        flist = "https://hub.grid.tf/ahmed_hanafy_1/ahmedhanafy725-pubtools-trc.flist"
        self.envars["SSHKEY"] = self.public_key
        self.envars["TRC_REMOTE"] = f"{self.gateway.dns_nameserver[0]}:{self.gateway.tcp_router_port}"
        secret_env = {}
        secret_encrypted = j.sals.zos.container.encrypt_secret(self.node_selected.node_id, self.secret)
        secret_env["TRC_SECRET"] = secret_encrypted

        j.sals.zos.container.create(
            reservation=self.reservation,
            node_id=self.node_selected.node_id,
            network_name=self.network.name,
            ip_address=self.ip_address,
            flist=flist,
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

        metadata = {"Solution name": self.solution_name, "version": 1, "chatflow": "publisher"}

        res = j.sals.reservation_chatflow.get_solution_metadata(self.solution_name, SolutionType.Publisher, metadata)
        reservation = j.sals.reservation_chatflow.add_reservation_metadata(self.reservation, res)

        self.reservation_id = j.sals.reservation_chatflow.register_and_pay_reservation(
            reservation, self.expiration, customer_tid=j.core.identity.me.tid, currency=self.query["currency"], bot=self
        )

        j.sals.reservation_chatflow.save_reservation(
            self.reservation_id, self.solution_name, SolutionType.Publisher, metadata
        )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        message = f"""
        You can access your container using:
        Domain: {self.domain}
        IP address: {self.ip_address}
        """
        self.md_show(dedent(message), md=True)


chat = Publisher
