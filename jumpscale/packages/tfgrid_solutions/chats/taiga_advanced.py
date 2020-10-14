from nacl.encoding import Base64Encoder
from nacl.public import PrivateKey

from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer
from jumpscale.loader import j
from jumpscale.sals.reservation_chatflow import deployment_context, DeploymentFailed


class TaigaDeploy(MarketPlaceAppsChatflow):
    FLIST_URL = "https://hub.grid.tf/waleedhammam.3bot/waleedhammam-taiga-latest.flist"
    SOLUTION_TYPE = "taiga"
    title = "Taiga"
    steps = [
        "get_solution_name",
        "taiga_credentials",
        "upload_public_key",
        "backup_credentials",
        "set_expiration",
        "infrastructure_setup",
        "reservation",
        "initializing",
        "init_backup",
        "success",
    ]

    resources = {"cru": 1, "mru": 1, "sru": 4}
    # main container + nginx container
    query = {"cru": 2, "mru": 2, "sru": 4.25}

    def _init_solution(self):
        super()._init_solution()
        self.allow_custom_domain = True

    @chatflow_step(title="Taiga Setup")
    def taiga_credentials(self):
        user_info = self.user_info()
        self.user_email = user_info["email"]
        self.username = user_info["username"]
        form = self.new_form()
        EMAIL_HOST_USER = form.string_ask("Please add the host e-mail address for your solution", required=True)
        EMAIL_HOST = form.string_ask(
            "Please add the smtp host example: `smtp.gmail.com`", default="smtp.gmail.com", required=True, md=True
        )
        EMAIL_HOST_PASSWORD = form.secret_ask("Please add the host e-mail password", required=True)

        SECRET_KEY = form.secret_ask("Please add a secret key for your solution", required=True)

        form.ask()
        self.EMAIL_HOST_USER = EMAIL_HOST_USER.value
        self.EMAIL_HOST = EMAIL_HOST.value
        self.EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD.value
        self.SECRET_KEY = SECRET_KEY.value

    @chatflow_step(title="SSH key (Optional)")
    def upload_public_key(self):
        self.public_key = (
            self.upload_file(
                "Please upload your public ssh key, this will allow you to access your threebot container using ssh",
            )
            or ""
        )
        self.public_key = self.public_key.strip()

    @chatflow_step(title="Backup credentials")
    def backup_credentials(self):
        form = self.new_form()
        aws_access_key_id = form.string_ask("AWS access key id", required=True)
        aws_secret_access_key = form.secret_ask("AWS secret access key", required=True)
        restic_password = form.secret_ask("Restic Password", required=True)
        restic_repository = form.string_ask(
            "Restic Repository Example: `s3:s3backup.tfgw-testnet-01.gateway.tf/testbucket`", required=True, md=True
        )  # TODO: AUTOMATE THAT
        form.ask("These credentials will be used to backup your solution.", md=True)
        self.aws_access_key_id = aws_access_key_id.value
        self.aws_secret_access_key = aws_secret_access_key.value
        self.restic_password = restic_password.value
        self.restic_repository = restic_repository.value

    @chatflow_step(title="New Expiration")
    def set_expiration(self):
        self.expiration = deployer.ask_expiration(self)

    @deployment_context()
    def _deploy(self):
        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": self.SOLUTION_TYPE, "Solution name": self.solution_name},
        }
        self.solution_metadata.update(metadata)

        self.workload_ids = []

        # reserve subdomain
        subdomain_wid = deployer.create_subdomain(
            pool_id=self.gateway_pool.pool_id,
            gateway_id=self.gateway.node_id,
            subdomain=self.domain,
            addresses=self.addresses,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )

        subdomain_wid = deployer.wait_workload(subdomain_wid, self)

        if not subdomain_wid:
            raise DeploymentFailed(
                f"Failed to create subdomain {self.domain} on gateway {self.gateway.node_id} {subdomain_wid}. The resources you paid for will be re-used in your upcoming deployments.",
                wid=subdomain_wid,
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
            "public_key": self.public_key,
        }
        secret_env = {
            "AWS_ACCESS_KEY_ID": self.aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": self.aws_secret_access_key,
            "RESTIC_PASSWORD": self.restic_password,
            "RESTIC_REPOSITORY": self.restic_repository,
            "CRON_FREQUENCY": "0 0 * * *",  # every 1 day
            "EMAIL_HOST_PASSWORD": self.EMAIL_HOST_PASSWORD,
            "PRIVATE_KEY": private_key,
            "SECRET_KEY": self.SECRET_KEY,
            "FLASK_SECRET_KEY": flask_secret,
        }

        self.resv_id = deployer.deploy_container(
            pool_id=self.pool_id,
            node_id=self.selected_node.node_id,
            network_name=self.network_view.name,
            ip_address=self.ip_address,
            flist=self.FLIST_URL,
            cpu=self.resources["cru"],
            memory=self.resources["mru"] * 1024,
            disk_size=self.resources["sru"] * 1024,
            env=var_dict,
            interactive=False,
            entrypoint="/start_taiga.sh",
            public_ipv6=True,
            secret_env=secret_env,
            **self.solution_metadata,
            solution_uuid=self.solution_id,
        )

        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            raise DeploymentFailed(
                f"Failed to deploy workload {self.resv_id}. The resources you paid for will be re-used in your upcoming deployments.",
                solution_uuid=self.solution_id,
                wid=self.resv_id,
            )

        # expose taiga container
        _id = deployer.expose_and_create_certificate(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            network_name=self.network_view.name,
            trc_secret=self.secret,
            domain=self.domain,
            email=self.user_email,
            solution_ip=self.ip_address,
            solution_port=80,
            enforce_https=True,
            node_id=self.selected_node.node_id,
            solution_uuid=self.solution_id,
            proxy_pool_id=self.gateway_pool.pool_id,
            log_config=self.nginx_log_config,
            **self.solution_metadata,
        )

        success = deployer.wait_workload(_id, self)
        if not success:
            raise DeploymentFailed(
                f"Failed to create TRC container on node {self.selected_node.node_id} {_id}. The resources you paid for will be re-used in your upcoming deployments.",
                solution_uuid=self.solution_id,
                wid=_id,
            )

    @chatflow_step(title="Initializing backup")
    def init_backup(self):
        solution_name = self.solution_name.replace(".", "_").replace("-", "_")
        self.md_show_update("Setting container backup")
        SOLUTIONS_WATCHDOG_PATHS = j.sals.fs.join_paths(j.core.dirs.VARDIR, "solutions_watchdog")
        if not j.sals.fs.exists(SOLUTIONS_WATCHDOG_PATHS):
            j.sals.fs.mkdirs(SOLUTIONS_WATCHDOG_PATHS)

        restic_instance = j.tools.restic.get(solution_name)
        restic_instance.password = self.restic_password
        restic_instance.repo = self.restic_repository
        restic_instance.extra_env = {
            "AWS_ACCESS_KEY_ID": self.aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": self.aws_secret_access_key,
        }
        restic_instance.save()
        try:
            restic_instance.init_repo()
        except Exception as e:
            j.tools.restic.delete(solution_name)
            raise j.exceptions.Input(f"Error: Failed to reach repo {self.restic_repository} due to {str(e)}")
        restic_instance.start_watch_backup(SOLUTIONS_WATCHDOG_PATHS)


chat = TaigaDeploy
