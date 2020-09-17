from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer, solutions
from jumpscale.sals.reservation_chatflow import deployment_context, DeploymentFailed


class MattermostDeploy(MarketPlaceAppsChatflow):
    FLIST_URL = "https://hub.grid.tf/ayoubm.3bot/rafyamgadbenjamin-mattermost-latest.flist"
    SOLUTION_TYPE = "mattermost"
    title = "Mattermost"
    steps = [
        "get_solution_name",
        "mattermost_info",
        "infrastructure_setup",
        "reservation",
        "initializing",
        "success",
    ]

    query = {"cru": 1, "mru": 1, "sru": 1}

    @chatflow_step(title="Mattermost Information")
    def mattermost_info(self):
        self.user_email = self.user_info()["email"]
        self._choose_flavor()
        self.vol_size = self.flavor_resources["sru"]
        self.query["sru"] += self.vol_size

    @chatflow_step(title="Reservation", disable_previous=True)
    @deployment_context()
    def reservation(self):
        var_dict = {
            "MYSQL_ROOT_PASSWORD": "mostest",
            "MYSQL_USER": "mmuser",
            "MYSQL_PASSWORD": "mostest",
            "MYSQL_DATABASE": "mattermost_db",
        }
        metadata = {
            "name": self.solution_name,
            "form_info": {
                "Solution name": self.solution_name,
                "Domain name": self.domain,
                "chatflow": self.SOLUTION_TYPE,
            },
        }
        self.solution_metadata.update(metadata)

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
                f" {self.gateway.node_id} {_id}. The resources you paid for will be re-used in your upcoming deployments."
            )
        self.solution_url = f"https://{self.domain}"

        # create volume
        vol_mount_point = "/var/lib/mysql/"
        volume_config = {}
        vol_id = deployer.deploy_volume(
            self.pool_id,
            self.selected_node.node_id,
            self.vol_size,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(vol_id, self)
        if not success:
            raise DeploymentFailed(
                f"Failed to deploy volume on node {self.selected_node.node_id} {vol_id}. The resources you paid for will be re-used in your upcoming deployments.",
                solution_uuid=self.solution_id,
                wid=vol_id,
            )
        volume_config[vol_mount_point] = vol_id

        # Create container
        self.resv_id = deployer.deploy_container(
            pool_id=self.pool_id,
            node_id=self.selected_node.node_id,
            network_name=self.network_view.name,
            ip_address=self.ip_address,
            flist=self.FLIST_URL,
            cpu=self.query["cru"],
            memory=self.query["mru"] * 1024,
            disk_size=(self.query["sru"] - self.vol_size) * 1024,
            env=var_dict,
            interactive=False,
            entrypoint="/start_mattermost.sh",
            volumes=volume_config,
            public_ipv6=True,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            raise DeploymentFailed(
                f"Failed to deploy workload {self.resv_id}. The resources you paid for will be re-used in your upcoming deployments.",
                solution_uuid=self.solution_id,
                wid=self.resv_id,
            )

        # expose threebot container
        _id = deployer.expose_and_create_certificate(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            network_name=self.network_view.name,
            trc_secret=self.secret,
            domain=self.domain,
            email=self.user_email,
            solution_ip=self.ip_address,
            solution_port=8065,
            enforce_https=False,
            node_id=self.selected_node.node_id,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(_id, self)
        if not success:
            raise DeploymentFailed(
                f"Failed to create TRC container on node {self.selected_node.node_id}"
                f" {_id}. The resources you paid for will be re-used in your upcoming deployments.",
                solution_uuid=self.solution_id,
                wid=_id,
            )


chat = MattermostDeploy
