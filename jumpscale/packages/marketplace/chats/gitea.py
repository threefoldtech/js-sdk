from jumpscale.sals.chatflows.chatflows import StopChatFlow, chatflow_step
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer, solutions
import uuid


class GiteaDeploy(MarketPlaceAppsChatflow):
    FLIST_URL = "https://hub.grid.tf/omar0.3bot/omarelawady-gitea_all_in_one-latest.flist"
    SOLUTION_TYPE = "gitea"
    title = "Gitea"
    steps = [
        "get_solution_name",
        "solution_expiration",
        "payment_currency",
        "infrastructure_setup",
        "overview",
        "reservation",
        "initializing",
        "success",
    ]

    query = {"cru": 2, "mru": 1, "sru": 6}

    @chatflow_step(title="Confirmation")
    def overview(self):
        self.database_name = "gitea"
        self.database_user = "root"
        self.database_password = uuid.uuid4().hex
        self.repository_name = self.solution_name
        self.metadata = {
            "Solution Name": self.solution_name,
            "Network": self.network_view.name,
            "Node ID": self.selected_node.node_id,
            "Pool": self.pool_id,
            "IP Address": self.ip_address,
            "Domain": self.domain,
        }
        self.md_show_confirm(self.metadata)

    @chatflow_step(title="Reservation", disable_previous=True)
    def reservation(self):
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
            "form_info": {"Solution name": self.solution_name, "chatflow": "gitea",},
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
            raise StopChatFlow(
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
            **self.solution_metadata,
            solution_uuid=self.solution_id,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            solutions.cancel_solution([self.resv_id])
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

        self.proxy_id = deployer.create_proxy(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            domain_name=self.domain,
            trc_secret=self.secret,
            **self.solution_metadata,
            solution_uuid=self.solution_id,
        )
        success = deployer.wait_workload(self.proxy_id, self)
        if not success:
            solutions.cancel_solution([self.proxy_id])
            raise StopChatFlow(f"Failed to reserve reverse proxy workload {self.proxy_id}")

        self.tcprouter_id = deployer.expose_address(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            network_name=self.network_view.name,
            local_ip=self.ip_address,
            port=3000,
            tls_port=3000,
            trc_secret=self.secret,
            bot=self,
            **self.solution_metadata,
            solution_uuid=self.solution_id,
        )
        success = deployer.wait_workload(self.tcprouter_id)
        if not success:
            solutions.cancel_solution([self.tcprouter_id])
            raise StopChatFlow(f"Failed to reserve tcprouter container workload {self.tcprouter_id}")
        self.container_url_https = f"https://{self.domain}"

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        self._wgconf_show_check()
        message = f"""\
# Congratulations! Your own instance from {self.SOLUTION_TYPE} deployed successfully:
\n<br />\n
- You can access it via the browser using: <a href="https://{self.domain}" target="_blank">https://{self.domain}</a>
\n<br />\n
- This domain maps to your container with ip: `{self.ip_address}`
\n<br />\n
- After installation you can access your admin account at <a href="https://{self.domain}/user/admin" target="_blank">https://{self.domain}/user/admin</a>
\n<br />\n
- Your database password is {self.database_password}
\n<br />\n
                """
        self.md_show(message, md=True)


chat = GiteaDeploy
