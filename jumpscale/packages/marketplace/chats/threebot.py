from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer, solutions
from jumpscale.sals.reservation_chatflow import StopChatFlowCleanWorkloads
import uuid
from jumpscale.data.nacl.jsnacl import NACL


class ThreebotDeploy(MarketPlaceAppsChatflow):
    FLIST_URL = "https://hub.grid.tf/ahmedelsayed.3bot/threefoldtech-js-sdk-latest.flist"
    SOLUTION_TYPE = "3Bot"
    title = "3Bot"
    steps = [
        "get_solution_name",
        "threebot_branch",
        "set_backup_password",
        "solution_expiration",
        "payment_currency",
        "infrastructure_setup",
        "overview",
        "deploy",
        "initializing",
        "success",
    ]

    def _threebot_start(self):
        self._validate_user()
        self.solution_id = uuid.uuid4().hex
        self.username = self.user_info()["username"]
        self.threebot_name = j.data.text.removesuffix(self.username, ".3bot")
        self.explorer = j.core.identity.me.explorer
        self.solution_metadata = {}
        self.solution_metadata["owner"] = self.username
        self.query = {"cru": 2, "mru": 2, "sru": 2}

    @chatflow_step(title="Solution name")
    def get_solution_name(self):
        self._threebot_start()
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            threebot_solutions = solutions.list_threebot_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in threebot_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True

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

    @chatflow_step(title="Deployment Information", disable_previous=True)
    def overview(self):
        self.domain = f"{self.threebot_name}-{self.domain}"
        info = {"Solution name": self.solution_name, "domain": self.domain}
        self.md_show_confirm(info)

    @chatflow_step(title="Reservation", disable_previous=True)
    def deploy(self):
        # 1- add node to network
        metadata = {"form_info": {"Solution name": self.solution_name, "chatflow": "threebot"}}
        self.solution_metadata.update(metadata)
        self.workload_ids = []

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
            raise StopChatFlowCleanWorkloads(
                f"Failed to create subdomain {self.domain} on gateway {self.gateway.node_id} {self.workload_ids[0]}",
                self.solution_id,
            )
        test_cert = j.config.get("TEST_CERT")
        # 3- deploy threebot container
        environment_vars = {
            "SDK_VERSION": self.branch,
            "INSTANCE_NAME": self.solution_name,
            "THREEBOT_NAME": self.threebot_name,
            "DOMAIN": self.domain,
            # "SSHKEY": self.public_key,
            "TEST_CERT": "true" if test_cert else "false",
            "MARKETPLACE_URL": f"https://{j.sals.nginx.main.websites.marketplace_marketplace_root_proxy_443.domain}/",
        }
        self.network_view = self.network_view.copy()
        entry_point = "/bin/bash jumpscale/packages/tfgrid_solutions/scripts/threebot/entrypoint.sh"
        self.workload_ids.append(
            deployer.deploy_container(
                pool_id=self.pool_id,
                node_id=self.selected_node.node_id,
                network_name=self.network_view.name,
                ip_address=self.ip_address,
                flist=self.FLIST_URL,
                env=environment_vars,
                cpu=self.query["cru"],
                memory=self.query["mru"] * 1024,
                disk_size=self.query["sru"] * 1024,
                entrypoint=entry_point,
                secret_env={"BACKUP_PASSWORD": self.backup_password},
                interactive=False,
                solution_uuid=self.solution_id,
                **self.solution_metadata,
            )
        )
        self.resv_id = self.workload_ids[-1]
        success = deployer.wait_workload(self.workload_ids[1], self)
        if not success:
            raise StopChatFlowCleanWorkloads(
                f"Failed to create container on node {self.selected_node.node_id} {self.workload_ids[1]}",
                self.solution_id,
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
            raise StopChatFlowCleanWorkloads(
                f"Failed to create trc container on node {self.selected_node.node_id} {self.workload_ids[2]}",
                self.solution_id,
            )
        self.threebot_url = f"https://{self.domain}/admin"
        self.domain = self.domain + "/admin"


chat = ThreebotDeploy
