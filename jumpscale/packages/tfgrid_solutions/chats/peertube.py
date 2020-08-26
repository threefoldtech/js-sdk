import math
import uuid
import random
from textwrap import dedent

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
from jumpscale.sals.reservation_chatflow import deployer


class Peertube(GedisChatBot):
    FLIST_URL = "https://hub.grid.tf/omar0.3bot/omarelawady-peertube-latest.flist"

    steps = [
        "peertube_name",
        "peertube_email",
        "volume_details",
        "select_pool",
        "peertube_network",
        "overview",
        "reservation",
        "success",
    ]

    title = "Peertube"

    def _peertube_start(self):
        self.solution_id = uuid.uuid4().hex
        self.user_form_data = dict()
        self.query = dict()
        self.user_form_data["chatflow"] = "peertube"
        self.threebot_name = j.data.text.removesuffix(self.user_info()["username"], ".3bot")
        self.solution_metadata = {}

    @chatflow_step(title="Solution name")
    def peertube_name(self):
        self._peertube_start()
        self.solution_name = deployer.ask_name(self)

    @chatflow_step(title="Email")
    def peertube_email(self):
        self.email = deployer.ask_email(self)

    def container_resources(self):
        self.resources = dict()
        self.resources["cpu"] = 1
        self.resources["memory"] = 1024
        self.resources["disk_size"] = 1024
        self.resources["default_disk_type"] = "SSD"
        self.query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024) + self.vol_size,
        }

    @chatflow_step(title="Volume details")
    def volume_details(self):
        form = self.new_form()
        vol_disk_size = form.single_choice(
            "Please specify the peertube storage size in GBs", ["5", "15", "35"], default="5", required=True,
        )
        form.ask()
        self.vol_size = int(vol_disk_size.value)
        self.vol_mount_point = "/var/www/peertube/storage/"
        self.container_resources()

    @chatflow_step(title="Pool")
    def select_pool(self):
        cu, su = deployer.calculate_capacity_units(**self.query)
        self.pool_id = deployer.select_pool(self, cu=cu, su=su)

    @chatflow_step(title="Network")
    def peertube_network(self):
        self.network_view = deployer.select_network(self)
        self.container_node_id()
        self.select_domain()

    def container_node_id(self):
        self.selected_node = deployer.schedule_container(self.pool_id, **self.query)
        self.ip_address = self.network_view.get_free_ip(self.selected_node)

    def select_domain(self):
        gateways = deployer.list_all_gateways()
        if not gateways:
            raise StopChatFlow("There are no available gateways in the farms bound to your pools.")

        domains = dict()
        for gw_dict in gateways.values():
            gateway = gw_dict["gateway"]
            for domain in gateway.managed_domains:
                domains[domain] = gw_dict

        self.domain = random.choice(list(domains.keys()))

        self.gateway = domains[self.domain]["gateway"]
        self.gateway_pool = domains[self.domain]["pool"]
        self.domain = f"{self.threebot_name}-{self.solution_name}.{self.domain}"
        self.domain = j.sals.zos.gateway.correct_domain(self.domain)

        self.addresses = []
        for ns in self.gateway.dns_nameserver:
            self.addresses.append(j.sals.nettools.get_host_by_name(ns))

        self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

    @chatflow_step(title="Confirmation")
    def overview(self):
        self.metadata = {
            "Solution Name": self.solution_name,
            "Network": self.network_view.name,
            "Node ID": self.selected_node.node_id,
            "Pool": self.pool_id,
            "CPU": self.resources["cpu"],
            "Memory": self.resources["memory"],
            "Disk Size": self.resources["disk_size"],
            "IP Address": self.ip_address,
            "Domain Name": self.domain,
        }
        self.md_show_confirm(self.metadata)

    @chatflow_step(title="Reservation")
    def reservation(self):
        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": "peertube", "Solution name": self.solution_name},
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
        self.threebot_url = f"https://{self.domain}"

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
            raise StopChatFlow(f"Failed to create trc container on node {self.selected_node.node_id} {_id}")

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        message = f"""\
# Congratulations! Your own instance from peertube deployed successfully:
\n<br />\n
- You can access it via the browser using: <a href="https://{self.domain}" target="_blank">https://{self.domain}</a>
\n<br />\n
- This domain maps to your container with ip: `{self.ip_address}`
                """
        self.md_show(dedent(message), md=True)


chat = Peertube
