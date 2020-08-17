from textwrap import dedent

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions


class Publisher(MarketPlaceChatflow):
    FLIST_URL = "https://hub.grid.tf/ahmed_hanafy_1/ahmedhanafy725-pubtools-trc.flist"
    SOLUTION_TYPE = "publisher"
    title = "Publisher"
    publishing_chatflow = "publisher"  # chatflow used to deploy the solution
    welcome_message = "This wizard will help you publish a Wiki, a Website or Blog."
    steps = [
        "start",
        "solution_name",
        "configuration",
        "solution_expiration",
        "payment_currency",
        "infrastructure_setup",
        "overview",
        "deploy",
        "success",
    ]

    @chatflow_step()
    def start(self):
        self._init_solution()
        self.storage_url = "zdb://hub.grid.tf:9900"
        self.query = {"cru": 1, "mru": 1, "sru": 2}
        self.md_show(self.welcome_message, md=True)

    @chatflow_step(title="Solution Settings")
    def configuration(self):
        form = self.new_form()
        ttype = form.single_choice("Choose the type", options=["wiki", "www", "blog"], default="wiki", required=True)
        title = form.string_ask("Title", required=True)
        url = form.string_ask("Repository url", required=True)
        branch = form.string_ask("Branch", required=True)
        form.ask("Set configuration")

        self.envars = {
            "TYPE": ttype.value,
            "NAME": "entrypoint",
            "TITLE": title.value,
            "URL": url.value,
            "BRANCH": branch.value,
            "EMAIL": self.user_info()["email"],
        }

    @chatflow_step(title="Confirmation")
    def overview(self):
        info = {"Solution name": self.solution_name, "domain": self.domain}
        self.md_show_confirm(info)

    @chatflow_step(title="Reservation", disable_previous=True)
    def deploy(self):
        metadata = {
            "name": self.solution_name,
            "form_info": {"Solution name": self.solution_name, "chatflow": self.publishing_chatflow},
        }
        self.solution_metadata.update(metadata)
        self.workload_ids = []
        self.network_view = self.network_view.copy()
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

        # 3- reserve tcp proxy
        self.workload_ids.append(
            deployer.create_proxy(
                pool_id=self.gateway_pool.pool_id,
                gateway_id=self.gateway.node_id,
                domain_name=self.domain,
                trc_secret=self.secret,
                solution_uuid=self.solution_id,
                **self.solution_metadata,
            )
        )
        success = deployer.wait_workload(self.workload_ids[1], self)
        if not success:
            solutions.cancel_solution(self.user_info()["username"], self.workload_ids)
            raise StopChatFlow(
                f"Failed to create reverse proxy {self.domain} on gateway {self.gateway.node_id} {self.workload_ids[1]}"
            )

        # 4- deploy container
        self.envars["TRC_REMOTE"] = f"{self.gateway.dns_nameserver[0]}:{self.gateway.tcp_router_port}"
        secret_env = {"TRC_SECRET": self.secret}
        self.workload_ids.append(
            deployer.deploy_container(
                pool_id=self.pool_id,
                node_id=self.selected_node.node_id,
                network_name=self.network_view.name,
                ip_address=self.ip_address,
                flist=self.FLIST_URL,
                env=self.envars,
                cpu=self.query["cru"],
                memory=self.query["mru"] * 1024,
                disk_size=self.query["sru"] * 1024,
                entrypoint="/bin/bash /start.sh",
                secret_env=secret_env,
                interactive=False,
                solution_uuid=self.solution_id,
                public_ipv6=True,
                **self.solution_metadata,
            )
        )
        if not success:
            solutions.cancel_solution(self.user_info()["username"], self.workload_ids)
            raise StopChatFlow(
                f"Failed to create container on node {self.selected_node.node_id} {self.workload_ids[2]}"
            )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        super().success()
        message = f"""## Deployment success
\n<br>\n
You can access your container using:

- Domain: <a href="https://{self.domain}" target="_blank">https://{self.domain}</a>

- IP address: `{self.ip_address}`
        """
        self.md_show(dedent(message), md=True)


chat = Publisher
