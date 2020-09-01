from textwrap import dedent

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import chatflow_step, StopChatFlow
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer, solutions
from jumpscale.sals.reservation_chatflow import StopChatFlowCleanWorkloads


class CryptpadDeploy(MarketPlaceAppsChatflow):
    FLIST_URL = "https://hub.grid.tf/bola.3bot/3bot-cryptopad-latest.flist"
    SOLUTION_TYPE = "cryptpad"
    title = "Cryptpad"
    steps = [
        "get_solution_name",
        "cryptpad_info",
        "solution_expiration",
        "payment_currency",
        "infrastructure_setup",
        "reservation",
        "initializing",
        "success",
    ]

    query = {"cru": 1, "mru": 1, "sru": 1}

    @chatflow_step(title="Cryptpad Information")
    def cryptpad_info(self):
        self.user_email = self.user_info()["email"]
        self._choose_flavor()
        self.vol_size = self.flavor_resources["sru"]
        self.vol_mount_point = "/persistent-data"
        self.query["sru"] += self.vol_size

    @chatflow_step(title="Reservation", disable_previous=True)
    def reservation(self):
        self.workload_ids = []
        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": self.SOLUTION_TYPE, "Solution name": self.solution_name},
        }
        self.solution_metadata.update(metadata)

        # reserve subdomain
        self.workload_ids.append(
            deployer.create_subdomain(
                pool_id=self.pool_id,
                gateway_id=self.gateway.node_id,
                subdomain=self.domain,
                addresses=self.addresses,
                solution_uuid=self.solution_id,
                **self.solution_metadata,
            )
        )
        success = deployer.wait_workload(self.workload_ids[0], self)
        if not success:
            raise StopChatFlowCleanWorkloads(
                f"Failed to create subdomain {self.domain} on gateway {self.gateway.node_id} {self.workload_ids[0]}",
                self.solution_id,
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
            raise StopChatFlowCleanWorkloads(
                f"Failed to deploy volume on node {self.selected_node.node_id} {vol_id}", self.solution_id
            )
        volume_config = {self.vol_mount_point: vol_id}

        # deploy container
        var_dict = {"size": str(self.vol_size * 1024)}  # in MBs
        self.workload_ids.append(
            deployer.deploy_container(
                pool_id=self.pool_id,
                node_id=self.selected_node.node_id,
                network_name=self.network_view.name,
                ip_address=self.ip_address,
                flist=self.FLIST_URL,
                cpu=self.query["cru"],
                memory=self.query["mru"] * 1024,
                disk_size=(self.query["sru"] - self.vol_size) * 1024,
                volumes=volume_config,
                env=var_dict,
                interactive=False,
                entrypoint="/start.sh",
                solution_uuid=self.solution_id,
                **self.solution_metadata,
            )
        )
        self.resv_id = self.workload_ids[-1]
        success = deployer.wait_workload(self.workload_ids[1], self)
        if not success:
            raise StopChatFlowCleanWorkloads(
                f"Failed to create container on node {self.selected_node.node_id} {self.workload_ids[1]}",
                self.solution_id,
            )
        # expose solution on nginx container
        _id = deployer.expose_and_create_certificate(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            network_name=self.network_view.name,
            trc_secret=self.secret,
            domain=self.domain,
            email=self.user_email,
            solution_ip=self.ip_address,
            solution_port=3000,
            enforce_https=False,
            node_id=self.selected_node.node_id,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(_id, self)
        if not success:
            raise StopChatFlowCleanWorkloads(
                f"Failed to create trc container on node {self.selected_node.node_id}" f" {_id}", self.solution_id
            )


chat = CryptpadDeploy
