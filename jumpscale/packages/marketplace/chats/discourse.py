from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer
from jumpscale.loader import j
import nacl
from jumpscale.sals.reservation_chatflow import deployment_context, DeploymentFailed


class Discourse(MarketPlaceAppsChatflow):
    FLIST_URL = "https://hub.grid.tf/omar0.3bot/omarelawady-discourse-http.flist"
    SOLUTION_TYPE = "discourse"
    steps = [
        "get_solution_name",
        "discourse_smtp_info",
        "infrastructure_setup",
        "reservation",
        "initializing",
        "success",
    ]

    title = "Discourse"
    container_resources = {"cru": 1, "mru": 2, "sru": 2}
    # main container + nginx container
    query = {"cru": 2, "mru": 3, "sru": 2.5}

    @chatflow_step(title="Discourse Setup")
    def discourse_smtp_info(self):
        user_info = self.user_info()
        self.user_email = user_info["email"]
        self.username = user_info["username"]
        form = self.new_form()
        self.smtp_server = form.string_ask("Please add the host e-mail address for your solution", required=True)
        self.smtp_username = form.string_ask(
            "Please add the smtp host example: `smtp.gmail.com`", default="smtp.gmail.com", required=True, md=True
        )
        self.smtp_password = form.secret_ask("Please add the host e-mail password", required=True)

        form.ask()
        self.smtp_server = self.smtp_server.value
        self.smtp_username = self.smtp_username.value
        self.smtp_password = self.smtp_password.value

    @deployment_context()
    def _deploy(self):
        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": self.SOLUTION_TYPE, "Solution name": self.solution_name},
        }
        self.solution_metadata.update(metadata)

        env = {
            "pub_key": "",
            "DISCOURSE_VERSION": "staging",
            "RAILS_ENV": "production",
            "DISCOURSE_HOSTNAME": self.domain,
            "DISCOURSE_SMTP_USER_NAME": self.smtp_username,
            "DISCOURSE_SMTP_ADDRESS": self.smtp_server,
            "DISCOURSE_DEVELOPER_EMAILS": self.user_email,
            "DISCOURSE_SMTP_PORT": "587",
            "THREEBOT_URL": "https://login.threefold.me",
            "OPEN_KYC_URL": "https://openkyc.live/verification/verify-sei",
            "UNICORN_BIND_ALL": "true",
        }
        threebot_private_key = nacl.signing.SigningKey.generate().encode(nacl.encoding.Base64Encoder).decode("utf-8")

        secret_env = {
            "THREEBOT_PRIVATE_KEY": threebot_private_key,
            "FLASK_SECRET_KEY": j.data.idgenerator.guid(),
            "DISCOURSE_SMTP_PASSWORD": self.smtp_password,
        }

        # reserve subdomain
        _id = deployer.create_subdomain(
            pool_id=self.gateway_pool.pool_id,
            gateway_id=self.gateway.node_id,
            subdomain=self.domain,
            addresses=self.addresses,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )

        success = deployer.wait_workload(_id, self)
        if not success:
            raise DeploymentFailed(
                f"Failed to create subdomain {self.domain} on gateway"
                f" {self.gateway.node_id} {_id}. The resources you paid for will be re-used in your upcoming deployments.",
                wid=_id,
            )
        self.threebot_url = f"https://{self.domain}"

        entrypoint = f"/.start_discourse.sh"

        # reserve container
        self.resv_id = deployer.deploy_container(
            pool_id=self.pool_id,
            node_id=self.selected_node.node_id,
            network_name=self.network_view.name,
            ip_address=self.ip_address,
            flist=self.FLIST_URL,
            cpu=self.container_resources["cru"],
            memory=self.container_resources["mru"] * 1024,
            disk_size=self.container_resources["sru"] * 1024,
            entrypoint=entrypoint,
            env=env,
            secret_env=secret_env,
            interactive=False,
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

        _id, _ = deployer.expose_and_create_certificate(
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


chat = Discourse
