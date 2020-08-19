import math
from textwrap import dedent
import uuid
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
from jumpscale.data.nacl.jsnacl import NACL
from jumpscale.sals.reservation_chatflow import deployer, solutions


class ThreebotDeploy(GedisChatBot):
    steps = [
        "start",
        "set_threebot_name",
        "container_resources",
        "select_pool",
        "threebot_network",
        "set_backup_password",
        "threebot_branch",
        "upload_public_key",
        "domain_select",
        "ipv6_config",
        "overview",
        "deploy",
        "intializing",
        "success",
    ]
    title = "3Bot"

    @chatflow_step()
    def start(self):
        self.flist = "https://hub.grid.tf/ahmedelsayed.3bot/threefoldtech-js-sdk-latest.flist"
        self.solution_id = uuid.uuid4().hex
        self.threebot_name = j.data.text.removesuffix(self.user_info()["username"], ".3bot")
        self.md_show("This wizard will help you deploy a 3Bot container", md=True)
        self.explorer = j.core.identity.me.explorer
        self.solution_metadata = {}

    @chatflow_step(title="Solution name")
    def set_threebot_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            threebot_solutions = solutions.list_threebot_solutions(sync=False)
            valid = True
            for sol in threebot_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True

    @chatflow_step(title="Container resources")
    def container_resources(self):
        self.resources = deployer.ask_container_resources(self, default_disk_size=2048, default_memory=2048)

    @chatflow_step(title="Pool")
    def select_pool(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        cu, su = deployer.calculate_capacity_units(**query)
        self.pool_id = deployer.select_pool(self, cu=cu, su=su, **query)
        self.selected_node = deployer.schedule_container(self.pool_id, **query)

    @chatflow_step(title="Network")
    def threebot_network(self):
        self.network_view = deployer.select_network(self)

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
        messege = "Please enter the password (using this password, you can recover any 3Bot you deploy online)"
        self.backup_password = self.secret_ask(messege, required=True, max_length=32)

        while not self._verify_password(self.backup_password):
            error = messege + f"<br><br><code>Incorrect password for 3Bot name {self.solution_name}</code>"
            self.backup_password = self.secret_ask(error, required=True, max_length=32, md=True)

    @chatflow_step(title="3Bot version")
    def threebot_branch(self):
        self.branch = self.string_ask("Please type branch name", required=True, default="development")

    @chatflow_step(title="Access key")
    def upload_public_key(self):
        self.public_key = self.upload_file(
            "Please upload your public ssh key, this will allow you to access your 3Bot container using ssh",
            required=True,
        ).strip()

    @chatflow_step(title="Domain")
    def domain_select(self):
        gateways = deployer.list_all_gateways()
        if not gateways:
            raise StopChatFlow("There are no available gateways in the farms bound to your pools.")

        domains = dict()
        for gw_dict in gateways.values():
            gateway = gw_dict["gateway"]
            for domain in gateway.managed_domains:
                domains[domain] = gw_dict

        self.domain = self.single_choice(
            "Please choose the domain you wish to use", list(domains.keys()), required=True
        )

        self.gateway = domains[self.domain]["gateway"]
        self.gateway_pool = domains[self.domain]["pool"]
        self.domain = f"{self.threebot_name}-{self.solution_name}.{self.domain}"

        self.addresses = []
        for ns in self.gateway.dns_nameserver:
            self.addresses.append(j.sals.nettools.get_host_by_name(ns))

        self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

    @chatflow_step(title="Global IPv6 Address")
    def ipv6_config(self):
        self.public_ipv6 = deployer.ask_ipv6(self)

    @chatflow_step(title="Confirmation")
    def overview(self):
        info = {
            "Solution name": self.solution_name,
            "Threebot version": self.branch,
            "Number of cpu cores": self.resources["cpu"],
            "Memory": self.resources["memory"],
            "Root filesystem type": "SSD",
            "Root filesystem size": self.resources["disk_size"],
        }
        self.md_show_confirm(info)

    @chatflow_step(title="Reservation", disable_previous=True)
    def deploy(self):
        # 1- add node to network
        metadata = {
            "form_info": {"Solution name": self.solution_name, "chatflow": "threebot"},
        }
        self.solution_metadata.update(metadata)
        self.workload_ids = []
        result = deployer.add_network_node(
            self.network_view.name,
            self.selected_node,
            self.pool_id,
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

        # 3- deploy threebot container
        environment_vars = {
            "SDK_VERSION": self.branch,
            "INSTANCE_NAME": self.solution_name,
            "THREEBOT_NAME": self.threebot_name,
            "DOMAIN": self.domain,
            "SSHKEY": self.public_key,
        }
        self.network_view = self.network_view.copy()
        entry_point = "/bin/bash jumpscale/packages/tfgrid_solutions/scripts/threebot/entrypoint.sh"
        self.workload_ids.append(
            deployer.deploy_container(
                pool_id=self.pool_id,
                node_id=self.selected_node.node_id,
                network_name=self.network_view.name,
                ip_address=self.ip_address,
                flist=self.flist,
                env=environment_vars,
                cpu=self.resources["cpu"],
                memory=self.resources["memory"],
                disk_size=self.resources["disk_size"],
                entrypoint=entry_point,
                secret_env={"BACKUP_PASSWORD": self.backup_password},
                interactive=False,
                solution_uuid=self.solution_id,
                public_ipv6=self.public_ipv6,
                **self.solution_metadata,
            )
        )
        success = deployer.wait_workload(self.workload_ids[1], self)
        if not success:
            solutions.cancel_solution(self.workload_ids)
            raise StopChatFlow(
                f"Failed to create container on node {self.selected_node.node_id} {self.workload_ids[1]}"
            )

        # 4- expose threebot container
        self.workload_ids.append(
            deployer.expose_address(
                pool_id=self.pool_id,
                gateway_id=self.gateway.node_id,
                network_name=self.network_view.name,
                local_ip=self.ip_address,
                port=80,
                tls_port=443,
                trc_secret=self.secret,
                node_id=self.selected_node.node_id,
                reserve_proxy=True,
                domain_name=self.domain,
                proxy_pool_id=self.gateway_pool.pool_id,
                solution_uuid=self.solution_id,
                **self.solution_metadata,
            )
        )
        success = deployer.wait_workload(self.workload_ids[2], self)
        if not success:
            solutions.cancel_solution(self.workload_ids)
            raise StopChatFlow(
                f"Failed to create trc container on node {self.selected_node.node_id} {self.workload_ids[2]}"
            )
        self.threebot_url = f"https://{self.domain}/admin"

    @chatflow_step(title="Initializing", disable_previous=True)
    def intializing(self):
        self.md_show_update("Initializing your 3Bot ...")
        if not j.sals.nettools.wait_http_test(self.threebot_url, timeout=600):
            self.stop("Failed to initialize 3Bot, please contact support")

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        message = f"""# Your 3Bot has been deployed successfully.
\n<br>\n

- Reservation ID  : `{self.workload_ids[-1]}`

- Domain          : <a href="{self.threebot_url}" target="_blank">{self.threebot_url}</a>

- IP Address      : `{self.ip_address}`
        """
        self.md_show(dedent(message), md=True)


chat = ThreebotDeploy
