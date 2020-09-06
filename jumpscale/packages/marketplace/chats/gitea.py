from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer, solutions
import uuid
from jumpscale.sals.reservation_chatflow import deployment_context, DeploymentFailed


class GiteaDeploy(MarketPlaceAppsChatflow):
    FLIST_URL = "https://hub.grid.tf/omar0.3bot/omarelawady-gitea_all_in_one-latest.flist"
    SOLUTION_TYPE = "gitea"
    title = "Gitea"
    steps = [
        "get_solution_name",
        "solution_expiration",
        "payment_currency",
        "infrastructure_setup",
        "reservation",
        "initializing",
        "success",
    ]

    query = {"cru": 2, "mru": 1, "sru": 6}

    @chatflow_step(title="Reservation", disable_previous=True)
    @deployment_context()
    def reservation(self):
        self.database_name = "gitea"
        self.database_user = "root"
        self.database_password = uuid.uuid4().hex
        self.repository_name = self.solution_name
        var_dict = {
            "POSTGRES_DB": self.database_name,
            "DB_TYPE": "postgres",
            "DB_HOST": "localhost:5432",
            "POSTGRES_USER": self.database_user,
            "APP_NAME": self.repository_name,
            "ROOT_URL": f"https://{self.domain}",
            "HTTP_PORT": "3000",
            "DOMAIN": f"{self.domain}",
        }
        metadata = {
            "name": self.solution_name,
            "form_info": {
                "Solution name": self.solution_name,
                "chatflow": "gitea",
            },
        }
        self.solution_metadata.update(metadata)
        # reserve subdomain
        subdomain_wid = deployer.create_subdomain(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            subdomain=self.domain,
            addresses=self.addresses,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )
        subdomain_wid = deployer.wait_workload(subdomain_wid, self)

        if not subdomain_wid:
            raise DeploymentFailed(
                f"Failed to create subdomain {self.domain} on gateway {self.gateway.node_id} {subdomain_wid}"
            )

        self.resv_id = deployer.deploy_container(
            pool_id=self.pool_id,
            node_id=self.selected_node.node_id,
            network_name=self.network_view.name,
            ip_address=self.ip_address,
            flist=self.FLIST_URL,
            cpu=self.query["cru"],
            memory=self.query["mru"] * 1024,
            env=var_dict,
            interactive=False,
            entrypoint="/start_gitea.sh",
            public_ipv6=True,
            disk_size=self.query["sru"] * 1024,
            secret_env={"POSTGRES_PASSWORD": self.database_password},
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            solutions.cancel_solution(self.solution_metadata["owner"], [self.resv_id])
            raise DeploymentFailed(f"Failed to deploy workload {self.resv_id}", solution_uuid=self.solution_id)

        self.reverse_proxy_id = deployer.expose_and_create_certificate(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            network_name=self.network_view.name,
            trc_secret=self.secret,
            domain=self.domain,
            email=self.user_info()["email"],
            solution_ip=self.ip_address,
            solution_port=3000,
            enforce_https=True,
            node_id=self.selected_node.node_id,
            solution_uuid=self.solution_id,
            proxy_pool_id=self.gateway_pool.pool_id,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(self.reverse_proxy_id)
        if not success:
            solutions.cancel_solution(self.solution_metadata["owner"], [self.reverse_proxy_id])
            raise DeploymentFailed(
                f"Failed to reserve TCP Router container workload {self.reverse_proxy_id}",
                solution_uuid=self.solution_id,
            )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        message = f"""\
# Congratulations! Your own instance from {self.SOLUTION_TYPE} deployed successfully:
\n<br />\n
- You can access it via the browser using: <a href="https://{self.domain}" target="_blank">https://{self.domain}</a>
\n<br />\n
- After installation you can access your admin account at <a href="https://{self.domain}/user/admin" target="_blank">https://{self.domain}/user/admin</a>
\n<br />\n
                """
        self.md_show(message, md=True)


chat = GiteaDeploy
