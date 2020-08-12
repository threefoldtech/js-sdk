import math
from textwrap import dedent
import uuid
from jumpscale.clients.explorer.models import DiskType
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.data.nacl.jsnacl import NACL


class ThreebotDeploy(GedisChatBot):
    steps = [
        "start",
        "set_solution_name",
        "set_backup_password",
        "select_network",
        "threebot_branch",
        "container_resources",
        "upload_public_key",
        "domain_select",
        "select_expiration_time",
        "select_farm",
        "overview",
        "deploy",
        "intializing",
        "success",
    ]

    title = "Threebot"

    @chatflow_step()
    def start(self):
        self.user_info = self.user_info()
        self.threebot_name = j.data.text.removesuffix(self.user_info["username"], ".3bot")
        self.md_show("This wizard will help you deploy a Threebot container", md=True)
        j.sals.reservation_chatflow.validate_user(self.user_info)
        self.explorer = j.core.identity.me.explorer

    @chatflow_step(title="Network")
    def select_network(self):
        self.network = j.sals.reservation_chatflow.select_network(self, j.core.identity.me.tid)
        self.solution_currency = self.network.currency

    @chatflow_step(title="Solution name")
    def set_solution_name(self):
        message = "Please enter a name for your threebot (without spaces or special characters)"
        self.solution_name = self.string_ask(message, required=True)

        while not self.solution_name.isidentifier():
            error = message + "<br><br> <code>Invalid name</code>"
            self.solution_name = self.string_ask(error, md=True, required=True)

    def _verify_password(self, password):
        try:
            name = f"{self.threebot_name}_{self.solution_name}"
            user = self.explorer.users.get(name=name)
            words = j.data.encryption.key_to_mnemonic(password.encode().zfill(32))
            seed = j.data.encryption.mnemonic_to_key(words)
            pubkey = NACL(seed).get_verify_key_hex()
            return pubkey == user.pubkey
        except j.exceptions.NotFound:
            return True

    @chatflow_step(title="Password")
    def set_backup_password(self):
        messege = "Please enter the password (using this password, you can recover any 3bot you deploy online)"
        self.backup_password = self.secret_ask(messege, required=True, max_length=32)

        while not self._verify_password(self.backup_password):
            error = messege + f"<br><br><code>Incorrect password for threebot name {self.solution_name}</code>"
            self.backup_password = self.secret_ask(error, required=True, max_length=32, md=True)

    @chatflow_step(title="Threebot version")
    def threebot_branch(self):
        self.branch = self.string_ask("Please type branch name", required=True, default="development")

    @chatflow_step(title="Resources")
    def container_resources(self):
        form = self.new_form()
        cpu = form.int_ask("Please add how many CPU cores are needed", default=2, required=True)
        memory = form.int_ask("Please add the amount of memory in MB", default=2048, required=True)
        rootfs_size = form.int_ask("Choose the amount of storage for your root filesystem in MiB", default=2048)

        form.ask()

        self.container_cpu = cpu.value
        self.container_memory = memory.value
        self.container_rootfs_size = rootfs_size.value
        self.container_fs_type = DiskType.SSD.name

    @chatflow_step(title="Access key")
    def upload_public_key(self):
        self.public_key = self.upload_file(
            "Please upload your public ssh key, this will allow you to access your threebot container using ssh",
            required=True,
        ).strip()

    @chatflow_step(title="Select farm")
    def select_farm(self):
        self.query = dict(
            currency=self.network.currency,
            cru=self.container_cpu + 1,
            mru=math.ceil(self.container_memory / 1024) + 1,
            sru=math.ceil(self.container_rootfs_size / 1024),
            hru=1,
        )
        farms = j.sals.reservation_chatflow.get_farm_names(1, self, **self.query)
        self.node_selected = j.sals.reservation_chatflow.get_nodes(1, farm_names=farms, **self.query)[0]

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

        self.gateway = domains[self.domain]
        self.domain = f"{self.threebot_name}-{self.solution_name}.{self.domain}"

        self.addresses = []
        for ns in self.gateway.dns_nameserver:
            self.addresses.append(j.sals.nettools.get_host_by_name(ns))

        self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

    @chatflow_step(title="Confirmation")
    def overview(self):
        info = {
            "Solution name": self.solution_name,
            "Threebot version": self.branch,
            "Number of cpu cores": self.container_cpu,
            "Memory": self.container_memory,
            "Root filesystem type": DiskType.SSD.name,
            "Root filesystem size": self.container_rootfs_size,
            "Expiration time": j.data.time.get(self.expiration).humanize(),
        }
        self.md_show_confirm(info)

    @chatflow_step(title="Payment", disable_previous=True)
    def deploy(self):
        self.network_copy = self.network.copy(j.core.identity.me.tid)
        self.network_copy.add_node(self.node_selected)
        self.ip_address = self.network_copy.get_free_ip(self.node_selected)

        self.network = self.network_copy
        self.network.update(j.core.identity.me.tid, currency=self.query["currency"], bot=self)

        self.reservation = j.sals.zos.reservation_create()
        j.sals.zos._gateway.sub_domain(self.reservation, self.gateway.node_id, self.domain, self.addresses)
        j.sals.zos._gateway.tcp_proxy_reverse(self.reservation, self.gateway.node_id, self.domain, self.secret)

        flist = "https://hub.grid.tf/ahmedelsayed.3bot/threefoldtech-js-sdk-latest.flist"
        entry_point = "/bin/bash jumpscale/packages/tfgrid_solutions/scripts/threebot/entrypoint.sh"
        environment_vars = {
            "SDK_VERSION": self.branch,
            "INSTANCE_NAME": self.solution_name,
            "THREEBOT_NAME": self.threebot_name,
            "DOMAIN": self.domain,
            "SSHKEY": self.public_key,
        }
        backup_pass_encrypted = j.sals.zos.container.encrypt_secret(self.node_selected.node_id, self.backup_password)

        j.sals.zos.container.create(
            reservation=self.reservation,
            node_id=self.node_selected.node_id,
            network_name=self.network.name,
            ip_address=self.ip_address,
            flist=flist,
            disk_type=DiskType.SSD.value,
            env=environment_vars,
            interactive=False,
            entrypoint=entry_point,
            cpu=self.container_cpu,
            memory=self.container_memory,
            disk_size=self.container_rootfs_size,
            secret_env={"BACKUP_PASSWORD": backup_pass_encrypted},
        )

        network = j.sals.reservation_chatflow.get_network(self, j.core.identity.me.tid, self.network.name)
        network.add_node(self.node_selected)
        network.update(j.core.identity.me.tid, currency=self.solution_currency, bot=self)
        network._used_ips.append(self.ip_address)
        ip_address = network.get_free_ip(self.node_selected)
        if not ip_address:
            raise j.exceptions.Value("No available free ips")

        secret_env = {}
        secret_encrypted = j.sals.zos.container.encrypt_secret(self.node_selected.node_id, self.secret)
        secret_env["TRC_SECRET"] = secret_encrypted
        remote = f"{self.gateway.dns_nameserver[0]}:{self.gateway.tcp_router_port}"
        local = f"{self.ip_address}:80"
        localtls = f"{self.ip_address}:443"
        entrypoint = f"/bin/trc -local {local} -local-tls {localtls} -remote {remote}"

        j.sals.zos.container.create(
            reservation=self.reservation,
            node_id=self.node_selected.node_id,
            network_name=self.network.name,
            ip_address=ip_address,
            flist="https://hub.grid.tf/tf-official-apps/tcprouter:latest.flist",
            entrypoint=entrypoint,
            secret_env=secret_env,
        )

        metadata = {"Solution name": self.solution_name, "Version": self.branch, "chatflow": "threebot"}

        res = j.sals.reservation_chatflow.get_solution_metadata(self.solution_name, SolutionType.Threebot, metadata)
        reservation = j.sals.reservation_chatflow.add_reservation_metadata(self.reservation, res)

        self.reservation_id = j.sals.reservation_chatflow.register_and_pay_reservation(
            reservation, self.expiration, customer_tid=j.core.identity.me.tid, currency=self.query["currency"], bot=self
        )

        j.sals.reservation_chatflow.save_reservation(
            self.reservation_id, self.solution_name, SolutionType.Threebot, metadata
        )

        self.threebot_url = f"https://{self.domain}/admin"

    @chatflow_step(title="Initializing", disable_previous=True)
    def intializing(self):
        self.md_show_update("Initializing your Threebot ...")
        if not j.sals.nettools.wait_http_test(self.threebot_url, timeout=600):
            self.stop("Failed to initialize threebot, please contact support")

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        message = f"""
        Your Threebot has been deployed successfully.
        Reservation ID  : {self.reservation_id}<br>
        Domain          : <a href="{self.threebot_url}" target="_parent">{self.threebot_url}</a><br>
        IP Address      : {self.ip_address}<br>
        """
        self.md_show(dedent(message), md=True)


chat = ThreebotDeploy
