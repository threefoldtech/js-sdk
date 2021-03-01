from textwrap import dedent

from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer, solutions
from jumpscale.sals.reservation_chatflow import DeploymentFailed, deployment_context


class Gitea(MarketPlaceAppsChatflow):
    FLIST_URL = "https://hub.grid.tf/magidentfinal.3bot/mmotawea-gitea-restic-latest.flist"
    SOLUTION_TYPE = "gitea"
    title = "Gitea"
    steps = [
        "get_solution_name",
        "gitea_info",
        "upload_public_key",
        "set_expiration",
        "backup_credentials",
        "infrastructure_setup",
        "reservation",
        "initializing",
        "init_backup",
        "success",
    ]

    query = {"cru": 3, "mru": 2, "sru": 6.5}
    resources = {"cru": 2, "mru": 1, "sru": 6}

    def _init_solution(self):
        super()._init_solution()
        self.allow_custom_domain = True

    @chatflow_step(title="Cryptpad Information")
    def gitea_info(self):
        form = self.new_form()
        self.database_name = form.string_ask(
            "Enter a database name", default="gitea", required=True, is_identifier=True
        )
        self.database_user = form.string_ask(
            "Enter a database username", default="root", required=True, is_identifier=True
        )
        self.database_password = form.secret_ask("Enter a database user password", required=True)
        self.repository_name = form.string_ask("Enter a repository name", required=True, default=self.solution_name)
        form.ask("Setup Information")
        self.database_name = self.database_name.value
        self.database_user = self.database_user.value
        self.database_password = self.database_password.value
        self.repository_name = self.repository_name.value
        self.user_email = self.user_info()["email"]

    @deployment_context()
    def _deploy(self):
        var_dict = {
            "POSTGRES_DB": self.database_name,
            "DB_TYPE": "postgres",
            "DB_HOST": "localhost:5432",
            "POSTGRES_USER": self.database_user,
            "APP_NAME": self.repository_name,
            "ROOT_URL": f"https://{self.domain}",
            "HTTP_PORT": "3000",
            "DOMAIN": f"{self.domain}",
            "pub_key": self.public_key,
        }
        metadata = {
            "name": self.solution_name,
            "form_info": {"Solution name": self.solution_name, "chatflow": "gitea",},
        }

        self.solution_metadata.update(metadata)
        # reserve subdomain
        if not self.custom_domain:
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
        secret_env = {
            "AWS_ACCESS_KEY_ID": self.aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": self.aws_secret_access_key,
            "RESTIC_PASSWORD": self.restic_password,
            "RESTIC_REPOSITORY": self.restic_repository,
            "CRON_FREQUENCY": "0 0 * * *",  # every 1 day
            "POSTGRES_PASSWORD": self.database_password,
        }
        self.resv_id = deployer.deploy_container(
            pool_id=self.pool_id,
            node_id=self.selected_node.node_id,
            network_name=self.network_view.name,
            ip_address=self.ip_address,
            flist=self.FLIST_URL,
            cpu=self.resources["cru"],
            memory=self.resources["mru"] * 1024,
            env=var_dict,
            interactive=False,
            entrypoint="/start_gitea.sh",
            public_ipv6=True,
            disk_size=self.resources["sru"] * 1024,
            secret_env=secret_env,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            solutions.cancel_solution(self.solution_metadata["owner"], [self.resv_id])
            raise DeploymentFailed(
                f"Failed to deploy workload {self.resv_id}. The resources you paid for will be re-used in your upcoming deployments.",
                solution_uuid=self.solution_id,
                wid=self.resv_id,
            )

        self.reverse_proxy_id, _ = deployer.expose_and_create_certificate(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            network_name=self.network_view.name,
            trc_secret=self.secret,
            domain=self.domain,
            email=self.user_email,
            solution_ip=self.ip_address,
            solution_port=3000,
            enforce_https=True,
            node_id=self.selected_node.node_id,
            solution_uuid=self.solution_id,
            proxy_pool_id=self.gateway_pool.pool_id,
            log_config=self.nginx_log_config,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(self.reverse_proxy_id)
        if not success:
            solutions.cancel_solution(self.solution_metadata["owner"], [self.reverse_proxy_id])
            raise DeploymentFailed(
                f"Failed to reserve TCP Router container workload {self.reverse_proxy_id}. The resources you paid for will be re-used in your upcoming deployments.",
                solution_uuid=self.solution_id,
                wid=self.reverse_proxy_id,
            )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        message = f"""\
        # Congratulations! Your own instance from {self.SOLUTION_TYPE} deployed successfully:
        <br />\n

        - You can access it via the browser using: <a href="https://{self.domain}" target="_blank">https://{self.domain}</a>

        - After installation you can access your admin account at <a href="https://{self.domain}/user/admin" target="_blank">https://{self.domain}/user/admin</a>
        """
        self.md_show(dedent(message), md=True)


chat = Gitea
