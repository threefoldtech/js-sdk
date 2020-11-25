from textwrap import dedent

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer
from jumpscale.sals.reservation_chatflow import DeploymentFailed, deployment_context


class Publisher(MarketPlaceAppsChatflow):
    FLIST_URL = "https://hub.grid.tf/ahmed_hanafy_1/ahmedhanafy725-pubtools-trc.flist"
    SOLUTION_TYPE = "publisher"  # chatflow used to deploy the solution
    EXAMPLE_URL = "https://github.com/threefoldfoundation/info_gridmanual"

    title = "Publisher"
    steps = [
        "get_solution_name",
        "configuration",
        "infrastructure_setup",
        "reservation",
        "initializing",
        "success",
    ]

    storage_url = "zdb://hub.grid.tf:9900"
    query = {"cru": 1, "mru": 1, "sru": 2}

    def get_mdconfig_msg(self):
        msg = dedent(
            f"""\
        Few parameters are needed to be able to publish your content online
        - Title  is the title shown up on your published content
        - Repository URL  is a valid git repository URL where your content lives e.g ({self.EXAMPLE_URL})
        - Branch is the deployment branch that exists on your git repository to be used as the version of your content to publish.

        for more information on the publishing tools please check the [manual](https://manual.threefold.io/)
        """
        )
        return msg

    @chatflow_step(title="Solution Settings")
    def configuration(self):
        user_info = self.user_info()
        self.username = user_info["username"]
        self.user_email = user_info["email"]
        form = self.new_form()
        ttype = form.single_choice(
            "Choose the publication type", options=["wiki", "www", "blog"], default="wiki", required=True
        )
        title = form.string_ask("Title", required=True)
        url = form.string_ask("Repository URL", required=True, is_git_url=True)
        branch = form.string_ask("Branch", required=True)
        msg = self.get_mdconfig_msg()
        form.ask(msg, md=True)
        self.envars = {
            "TYPE": ttype.value,
            "NAME": "entrypoint",
            "TITLE": title.value,
            "URL": url.value,
            "BRANCH": branch.value,
            "EMAIL": self.user_email,
        }

    @deployment_context()
    def _deploy(self):
        metadata = {
            "name": self.solution_name,
            "form_info": {"Solution name": self.solution_name, "chatflow": self.SOLUTION_TYPE},
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
                success = deployer.wait_workload(wid, self, breaking_node_id=self.selected_node.node_id)
                if not success:
                    raise DeploymentFailed(
                        f"Failed to add node {self.selected_node.node_id} to network {wid}. The resources you paid for will be re-used in your upcoming deployments.",
                        wid=wid,
                    )
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
            raise DeploymentFailed(
                f"Failed to create subdomain {self.domain} on gateway {self.gateway.node_id} {self.workload_ids[0]}. The resources you paid for will be re-used in your upcoming deployments.",
                wid=self.workload_ids[0],
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
            raise DeploymentFailed(
                f"Failed to create reverse proxy {self.domain} on gateway {self.gateway.node_id} {self.workload_ids[-1]}. The resources you paid for will be re-used in your upcoming deployments.",
                solution_uuid=self.solution_id,
                wid=self.workload_ids[-1],
            )

        # 4- deploy container
        self.envars["TRC_REMOTE"] = f"{self.gateway.dns_nameserver[0]}:{self.gateway.tcp_router_port}"
        self.envars["DOMAIN"] = self.domain
        self.envars["TEST_CERT"] = "true" if j.config.get("TEST_CERT") else "false"
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
                **self.solution_metadata,
            )
        )
        self.resv_id = self.workload_ids[-1]
        if not success:
            raise DeploymentFailed(
                f"Failed to create container on node {self.selected_node.node_id} {self.workload_ids[-1]}. The resources you paid for will be re-used in your upcoming deployments.",
                solution_uuid=self.solution_id,
                wid=self.workload_ids[-1],
            )


chat = Publisher
