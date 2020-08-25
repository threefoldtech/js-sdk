from textwrap import dedent

from jumpscale.sals.chatflows.chatflows import chatflow_step, StopChatFlow
from jumpscale.sals.marketplace import MarketPlaceAppsChatflow, deployer, solutions
from jumpscale.loader import j


class Peertube(MarketPlaceAppsChatflow):
    FLIST_URL = "https://hub.grid.tf/omar0.3bot/omarelawady-peertube-latest.flist"
    SOLUTION_TYPE = "peertube"
    steps = [
        "start",
        "get_solution_name",
        "volume_details",
        "solution_expiration",
        "payment_currency",
        "infrastructure_setup",
        "overview",
        "reservation",
        "success",
    ]

    title = "Peertube"

    @chatflow_step()
    def start(self):
        self._init_solution()
        self.query = {"cru": 1, "mru": 1, "sru": 1}
        self.md_show("# This wizard will help you deploy peertube", md=True)

    @chatflow_step(title="Volume details")
    def volume_details(self):
        form = self.new_form()
        volume_size = form.single_choice(
            "Please specify the peertube storage size in GBs", ["5", "15", "35"], default="5", required=True,
        )
        form.ask()
        self.vol_size = int(volume_size.value)
        self.vol_mount_point = "/var/www/peertube/storage/"
        self.query["sru"] += self.vol_size

    @chatflow_step(title="Deployment Information")
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
        self.threebot_url = f"http://{self.domain}"

        entrypoint = f'/usr/local/bin/startup.sh "{self.domain}"'
        self.entrypoint = entrypoint
        # reserve container
        self.resv_id = deployer.deploy_container(
            pool_id=self.pool_id,
            node_id=self.selected_node.node_id,
            network_name=self.network_view.name,
            ip_address=self.ip_address,
            flist=self.FLIST_URL,
            cpu=self.query["cru"],
            memory=self.query["mru"] * 1024,
            disk_size=(self.query["sru"] - self.vol_size) * 1024,
            entrypoint=entrypoint,
            volumes=volume_config,
            interactive=False,
            **self.solution_metadata,
            solution_uuid=self.solution_id,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

        _id = deployer.expose_and_create_certificate(
            pool_id=self.pool_info.reservation_id,
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
            # FIXME
            # solutions.cancel_solution(self.user_info()["username"], self.workload_ids)
            raise StopChatFlow(f"Failed to create trc container on node {self.selected_node.node_id} {_id}")

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        self._wgconf_show_check()
        message = f"""\
# Peertube has been deployed successfully: your reservation id is: {self.resv_id}

  ``` {self.threebot_url}```.It may take a few minutes.
                """
        self.md_show(dedent(message), md=True)


chat = Peertube
