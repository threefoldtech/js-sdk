from textwrap import dedent

from jumpscale.sals.chatflows.chatflows import chatflow_step, StopChatFlow
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer, solutions
from jumpscale.loader import j
import nacl


class Discourse(MarketPlaceAppsChatflow):
    FLIST_URL = "https://hub.grid.tf/omar0.3bot/omarelawady-discourse-http.flist"
    SOLUTION_TYPE = "discourse"
    steps = [
        "start",
        "get_solution_name",
        "discourse_smtp_info",
        "solution_expiration",
        "payment_currency",
        "infrastructure_setup",
        "overview",
        "reservation",
        "success",
    ]

    title = "Discourse"

    @chatflow_step()
    def start(self):
        self._init_solution()
        self.query = {"cru": 1, "mru": 2, "sru": 2}
        self.md_show("# This wizard will help you deploy discourse", md=True)

    @chatflow_step(title="SMTP information")
    def discourse_smtp_info(self):
        form = self.new_form()
        self.smtp_server = form.string_ask("SMTP server address", required=True)
        self.smtp_username = form.string_ask("SMTP server username", required=True)
        self.smtp_password = form.secret_ask("SMTP server password", required=True)
        form.ask()
        self.smtp_server = self.smtp_server.value
        self.smtp_username = self.smtp_username.value
        self.smtp_password = self.smtp_password.value

    @chatflow_step(title="Deployment Information", disable_previous=True)
    def overview(self):
        self.metadata = {
            "Solution Name": self.solution_name,
            "Network": self.network_view.name,
            "Node ID": self.selected_node.node_id,
            "Pool": self.pool_id,
            "CPU": self.query["cru"],
            "Memory": self.query["mru"],
            "Disk Size": self.query["sru"],
            "IP Address": self.ip_address,
            "Domain Name": self.domain,
        }
        self.md_show_confirm(self.metadata)

    @chatflow_step(title="Reservation", disable_previous=True)
    def reservation(self):
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
            "DISCOURSE_DEVELOPER_EMAILS": self.user_info()["email"],
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
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            subdomain=self.domain,
            addresses=self.addresses,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )

        success = deployer.wait_workload(_id, self)
        if not success:
            raise StopChatFlow(f"Failed to create subdomain {self.domain} on gateway" f" {self.gateway.node_id} {_id}")
        self.threebot_url = f"https://{self.domain}"

        entrypoint = f"/.start_discourse.sh"

        # reserve container
        self.resv_id = deployer.deploy_container(
            pool_id=self.pool_id,
            node_id=self.selected_node.node_id,
            network_name=self.network_view.name,
            ip_address=self.ip_address,
            flist=self.FLIST_URL,
            cpu=self.query["cru"],
            memory=self.query["mru"] * 1024,
            disk_size=self.query["sru"] * 1024,
            entrypoint=entrypoint,
            env=env,
            secret_env=secret_env,
            interactive=False,
            **self.solution_metadata,
            solution_uuid=self.solution_id,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

        _id = deployer.expose_and_create_certificate(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            network_name=self.network_view.name,
            trc_secret=self.secret,
            domain=self.domain,
            email=self.user_info()["email"],
            solution_ip=self.ip_address,
            solution_port=80,
            enforce_https=True,
            node_id=self.selected_node.node_id,
            solution_uuid=self.solution_id,
            proxy_pool_id=self.gateway_pool.pool_id,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(_id, self)
        if not success:
            solutions.cancel_solution(self.user_info()["username"], self.workload_ids)
            raise StopChatFlow(f"Failed to create trc container on node {self.selected_node.node_id} {_id}")

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        self._wgconf_show_check()
        message = f"""\
# Discourse has been deployed successfully: your reservation id is: {self.resv_id}
  ``` {self.threebot_url}```.It may take a few minutes.
                """
        self.md_show(dedent(message), md=True)


chat = Discourse
