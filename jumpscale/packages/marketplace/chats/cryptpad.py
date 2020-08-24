from textwrap import dedent

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import chatflow_step, StopChatFlow
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer, solutions


class CryptpadDeploy(MarketPlaceAppsChatflow):
    FLIST_URL = "https://hub.grid.tf/bola.3bot/3bot-cryptopad-latest.flist"
    SOLUTION_TYPE = "cryptpad"
    title = "Cryptpad"
    steps = [
        "start",
        "solution_name",
        "cryptpad_info",
        "solution_expiration",
        "payment_currency",
        "infrastructure_setup",
        "overview",
        "reservation",
        "success",
    ]

    @chatflow_step()
    def start(self):
        self._init_solution()
        self.query = {"cru": 1, "mru": 1, "sru": 1}
        self.md_show("# This wizard will help you deploy a cryptpad solution", md=True)

    @chatflow_step(title="Cryptpad Information")
    def cryptpad_info(self):
        form = self.new_form()
        volume_size = form.single_choice(
            "Please specify the cryptpad storage size in GBs", ["5", "10", "15"], default="10", required=True,
        )
        form.ask()
        self.vol_size = int(volume_size.value)
        self.vol_mount_point = "/persistent-data"
        self.query["sru"] += self.vol_size

    @chatflow_step(title="Deployment Information")
    def overview(self):
        self.metadata = {
            "Solution Name": self.solution_name,
            "Network": self.network_view.name,
            "Node ID": self.selected_node.node_id,
            "Pool": self.pool_info.reservation_id,
            "CPU": self.query["cru"],
            "Memory": self.query["mru"],
            "Disk Size": (self.query["sru"] - self.vol_size) * 1024,
            "IP Address": self.ip_address,
        }
        self.md_show_confirm(self.metadata)

    @chatflow_step(
        title="Reservation", disable_previous=True,
    )
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
            raise StopChatFlow(
                f"Failed to create subdomain {self.domain} on gateway {self.gateway.node_id} {self.workload_ids[0]}"
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
            raise StopChatFlow(f"Failed to deploy volume on node {self.selected_node.node_id} {vol_id}")
        volume_config = {self.vol_mount_point: vol_id}

        # deploy container
        var_dict = {
            "size": str(self.vol_size * 1024),  # in MBs
        }
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
        success = deployer.wait_workload(self.workload_ids[1], self)
        if not success:
            raise StopChatFlow(
                f"Failed to create container on node {self.selected_node.node_id} {self.workload_ids[1]}"
            )
        # expose solution on nginx container
        _id = deployer.expose_and_create_certificate(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            network_name=self.network_view.name,
            trc_secret=self.secret,
            domain=self.domain,
            email=self.user_info()["email"],
            solution_ip=self.ip_address,
            solution_port=3000,
            enforce_https=False,
            node_id=self.selected_node.node_id,
            solution_uuid=self.solution_id,
            **metadata,
        )
        success = deployer.wait_workload(_id, self)
        if not success:
            # solutions.cancel_solution(self.workload_ids)
            raise StopChatFlow(f"Failed to create trc container on node {self.selected_node.node_id}" f" {_id}")
        self.container_url_https = f"https://{self.domain}"
        self.container_url_http = f"http://{self.domain}"

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        self._wgconf_show_check()
        message = f"""\
# Cryptpad has been deployed successfully:\n<br>
Reservation id: {self.workload_ids[-1]}\n
You can access your container from browser at {self.container_url_https} \n or \n {self.container_url_http}\n
# It may take a few minutes.
        """
        self.md_show(dedent(message), md=True)


chat = CryptpadDeploy
