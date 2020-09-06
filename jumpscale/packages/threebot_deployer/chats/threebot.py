import uuid

from jumpscale.data.nacl.jsnacl import NACL
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer, solutions
from jumpscale.sals.reservation_chatflow import DeploymentFailed, deployment_context
from jumpscale.packages.threebot_deployer.models.backup_tokens_sal import BACKUP_MODEL_FACTORY


class ThreebotDeploy(MarketPlaceAppsChatflow):
    FLIST_URL = "https://hub.grid.tf/ahmedelsayed.3bot/threefoldtech-js-sdk-latest.flist"
    SOLUTION_TYPE = "threebot"  # chatflow used to deploy the solution
    title = "3Bot"
    steps = [
        "get_solution_name",
        "set_backup_password",
        "solution_expiration",
        "payment_currency",
        "infrastructure_setup",
        "deploy",
        "initializing",
        "success",
    ]

    def _threebot_start(self):
        self._validate_user()
        self.branch = "development"
        self.solution_id = uuid.uuid4().hex
        self.threebot_name = j.data.text.removesuffix(self.user_info()["username"], ".3bot")
        self.explorer = j.core.identity.me.explorer
        self.solution_metadata = {}
        self.solution_metadata["owner"] = self.user_info()["username"]
        self.query = {"cru": 2, "mru": 2, "sru": 2}

    @chatflow_step(title="Get a 3Bot Name")
    def get_solution_name(self):
        self._threebot_start()
        valid = False
        while not valid:
            self.solution_name = self.string_ask(
                "Just like humans, each 3Bot needs their own unique identity to exist on top of the Threefold Grid. Please enter a name for your new 3Bot. This name will be used as the web address that could give you access to your 3Bot anytime.",
                required=True,
                field="name",
                is_identifier=True,
            )
            threebot_solutions = solutions.list_threebot_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in threebot_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another name.")
                    break
                valid = True
        self.backup_model = BACKUP_MODEL_FACTORY.get(f"{self.solution_name}_{self.threebot_name}")

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

    @chatflow_step(title="Recovery Secret Key")
    def set_backup_password(self):
        message = (
            "Please enter the recovery secret (using this recovery secret, you can recover any 3Bot you deploy online)"
        )
        self.backup_password = self.secret_ask(message, required=True, max_length=32)

        while not self._verify_password(self.backup_password):
            error = message + f"<br><br><code>Incorrect recovery secret for 3Bot name {self.solution_name}</code>"
            self.backup_password = self.secret_ask(error, required=True, max_length=32, md=True)

    @chatflow_step(title="Select your preferred payment currency")
    def payment_currency(self):
        self.currency = self.single_choice(
            "Please select the currency you would like to pay your 3Bot deployment with.",
            ["FreeTFT", "TFT", "TFTA"],
            required=True,
        )

    @chatflow_step(title="Reservation", disable_previous=True)
    @deployment_context()
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
        deploying_message = f"""
# Deploying your 3Bot...\n\n
<br>It will usually take a few minutes to succeed. Please wait patiently.\n
You will be automatically redirected to the next step once succeeded.
                """
        self.md_show_update(deploying_message, md=True)

        success = deployer.wait_workload(self.workload_ids[0])
        if not success:
            raise DeploymentFailed(
                f"Failed to create subdomain {self.domain} on gateway {self.gateway.node_id} {self.workload_ids[0]}"
            )
        test_cert = j.config.get("TEST_CERT")

        # Generate a one-time token to create a user for backup
        backup_token = str(j.data.idgenerator.idgenerator.uuid.uuid4())
        self.backup_model.token = backup_token
        self.backup_model.tname = self.solution_metadata["owner"]
        self.backup_model.save()
        # 3- deploy threebot container
        environment_vars = {
            "SDK_VERSION": self.branch,
            "INSTANCE_NAME": self.solution_name,
            "THREEBOT_NAME": self.threebot_name,
            "DOMAIN": self.domain,
            # "SSHKEY": self.public_key,
            "TEST_CERT": "true" if test_cert else "false",
            "MARKETPLACE_URL": f"https://{j.sals.nginx.main.websites.threebot_deployer_threebot_deployer_root_proxy_443.domain}/",
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
                secret_env={"BACKUP_PASSWORD": self.backup_password, "BACKUP_TOKEN": backup_token},
                interactive=False,
                solution_uuid=self.solution_id,
                **self.solution_metadata,
            )
        )
        success = deployer.wait_workload(self.workload_ids[1])
        if not success:
            raise DeploymentFailed(
                f"Failed to create container on node {self.selected_node.node_id} {self.workload_ids[-1]}",
                solution_uuid=self.solution_id,
                wid=self.workload_ids[-1],
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
        success = deployer.wait_workload(self.workload_ids[2])
        if not success:
            raise DeploymentFailed(
                f"Failed to create TRC container on node {self.selected_node.node_id} {self.workload_ids[2]}",
                solution_uuid=self.solution_id,
                wid=self.workload_ids[-1],
            )
        self.threebot_url = f"https://{self.domain}/admin"

    @chatflow_step(title="Expiration Date and Time")
    def solution_expiration(self):
        msg = """Please enter the expiration date of your 3Bot. This will be used to calculate the amount of capacity you need to keep your 3Bot alive and build projects on top of the TF Grid. But no worries, you could always extend your 3Bot’s lifetime on 3Bot Deployer's home screen"""
        self.expiration = deployer.ask_expiration(self, j.data.time.get().timestamp + 15552000, msg=msg)

    @chatflow_step(title="Initializing", disable_previous=True)
    def initializing(self):
        self.md_show_update("Initializing your 3Bot ...")
        if not j.sals.reservation_chatflow.wait_http_test(
            self.threebot_url, timeout=600, verify=not j.config.get("TEST_CERT")
        ):
            self.stop(f"Failed to initialize 3Bot on {self.threebot_url} , please contact support")
        self.domain = f"{self.domain}/admin"


chat = ThreebotDeploy
