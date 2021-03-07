from jumpscale.sals.chatflows.chatflows import chatflow_step
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer
from jumpscale.sals.reservation_chatflow import DeploymentFailed, deployment_context


class CryptpadDeploy(MarketPlaceAppsChatflow):
    FLIST_URL = "https://hub.grid.tf/waleedhammam.3bot/waleedhammam-cryptpad-latest.flist"
    SOLUTION_TYPE = "cryptpad"
    title = "Cryptpad"
    steps = [
        "get_solution_name",
        "upload_public_key",
        "set_expiration",
        "cryptpad_info",
        "backup_credentials",
        "infrastructure_setup",
        "reservation",
        "initializing",
        "init_backup",
        "success",
    ]

    # main container + nginx container
    query = {"cru": 2, "mru": 2, "sru": 1.5}

    resources = {"cru": 1, "mru": 1, "sru": 1}

    def _init_solution(self):
        super()._init_solution()
        self.allow_custom_domain = True

    @chatflow_step(title="Cryptpad Information")
    def cryptpad_info(self):
        self.user_email = self.user_info()["email"]
        self._choose_flavor()
        self.vol_size = self.flavor_resources["sru"]
        self.vol_mount_point = "/persistent-data"
        self.query["sru"] += self.vol_size

    @deployment_context()
    def _deploy(self):
        self.workload_ids = []
        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": self.SOLUTION_TYPE, "Solution name": self.solution_name},
        }
        self.solution_metadata.update(metadata)
        if not self.custom_domain:
            # reserve subdomain
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

        # deploy volume
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
        volume_config = {self.vol_mount_point: vol_id}

        # deploy container
        var_dict = {"size": str(self.vol_size * 1024), "pub_key": self.public_key}  # in MBs
        secret_env = {
            "AWS_ACCESS_KEY_ID": self.aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": self.aws_secret_access_key,
            "RESTIC_PASSWORD": self.restic_password,
            "RESTIC_REPOSITORY": self.restic_repository,
            "BACKUP_PATHS": "/persistent-data",
            "CRON_FREQUENCY": "0 0 * * *",  # every 1 day
        }
        self.workload_ids.append(
            deployer.deploy_container(
                pool_id=self.pool_id,
                node_id=self.selected_node.node_id,
                network_name=self.network_view.name,
                ip_address=self.ip_address,
                flist=self.FLIST_URL,
                cpu=self.resources["cru"],
                memory=self.resources["mru"] * 1024,
                disk_size=self.resources["sru"] * 1024,
                volumes=volume_config,
                env=var_dict,
                secret_env=secret_env,
                interactive=False,
                entrypoint="/start.sh",
                solution_uuid=self.solution_id,
                **self.solution_metadata,
            )
        )
        self.resv_id = self.workload_ids[-1]
        success = deployer.wait_workload(self.workload_ids[-1], self)
        if not success:
            raise DeploymentFailed(
                f"Failed to create container on node {self.selected_node.node_id} {self.workload_ids[-1]}. The resources you paid for will be re-used in your upcoming deployments.",
                solution_uuid=self.solution_id,
                wid=self.workload_ids[-1],
            )
        # expose solution on nginx container
        _id, _ = deployer.expose_and_create_certificate(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            network_name=self.network_view.name,
            trc_secret=self.secret,
            domain=self.domain,
            email=self.user_email,
            solution_ip=self.ip_address,
            solution_port=3000,
            enforce_https=False,
            proxy_pool_id=self.gateway_pool.pool_id,
            node_id=self.selected_node.node_id,
            solution_uuid=self.solution_id,
            log_config=self.nginx_log_config,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(_id, self)
        if not success:
            raise DeploymentFailed(
                f"Failed to create TRC container on node {self.selected_node.node_id}"
                f" {_id}. The resources you paid for will be re-used in your upcoming deployments.",
                solution_uuid=self.solution_id,
                wid=self.workload_ids[-1],
            )


chat = CryptpadDeploy
