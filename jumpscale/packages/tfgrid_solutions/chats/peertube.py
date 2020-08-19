import math

from jumpscale.clients.explorer.models import DiskType
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
from jumpscale.sals.reservation_chatflow.models import SolutionType
import uuid
from jumpscale.sals.reservation_chatflow import deployer, solutions


class Peertube(GedisChatBot):
    FLIST_URL = "https://hub.grid.tf/ashraf.3bot/threefoldtech-peertube-latest.flist"

    steps = [
        "peertube_start",
        "peertube_name",
        "peertube_email",
        "container_resources",
        "select_pool",
        "peertube_network",
        "container_logs",
        "public_key_get",
        "select_domain",
        "container_node_id",
        "container_ip",
        "overview",
        "reservation",
        "peertube_access",
    ]

    title = "Peertube"

    @chatflow_step()
    def peertube_start(self):
        self.solution_id = uuid.uuid4().hex
        self.user_form_data = dict()
        self.query = dict()
        self.user_form_data["chatflow"] = "peertube"
        self.md_show("# This wizard will help you deploy peertube", md=True)
        self.threebot_name = j.data.text.removesuffix(
            self.user_info()["username"], ".3bot"
        )
        self.solution_metadata = {}

    @chatflow_step(title="Solution name")
    def peertube_name(self):
        valid = False
        self.solution_name = deployer.ask_name(self)

    @chatflow_step(title="Email")
    def peertube_email(self):
        self.email = deployer.ask_email(self)

    @chatflow_step(title="Container resources")
    def container_resources(self):
        self.resources = deployer.ask_container_resources(self)

    @chatflow_step(title="Pool")
    def select_pool(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        cu, su = deployer.calculate_capacity_units(**query)
        self.pool_id = deployer.select_pool(self, cu=cu, su=su)

    @chatflow_step(title="Network")
    def peertube_network(self):
        self.network_view = deployer.select_network(self)

    @chatflow_step(title="Container logs")
    def container_logs(self):
        self.container_logs_option = self.single_choice(
            "Do you want to push the container logs (stdout and stderr) onto an"
            " external redis channel",
            ["YES", "NO"],
            default="NO",
        )
        if self.container_logs_option == "YES":
            self.log_config = deployer.ask_container_logs(self, self.solution_name)
        else:
            self.log_config = {}

    @chatflow_step(title="Access keys")
    def public_key_get(self):
        self.public_key = self.upload_file(
            """Please add your public ssh key, this will allow you to access the deployed container using ssh.
                    Just upload the file with the key""",
            required=True,
        ).split("\n")[0]

    @chatflow_step(title="Container node id")
    def container_node_id(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        self.selected_node = deployer.ask_container_placement(
            self, self.pool_id, **query
        )
        if not self.selected_node:
            self.selected_node = deployer.schedule_container(self.pool_id, **query)

    @chatflow_step(title="Container IP")
    def container_ip(self):
        self.network_view_copy = self.network_view.copy()
        result = deployer.add_network_node(
            self.network_view.name,
            self.selected_node,
            self.pool_id,
            self.network_view_copy,
            bot=self,
        )
        if result:
            self.md_show_update("Deploying Network on Nodes....")
            for wid in result["ids"]:
                success = deployer.wait_workload(wid)
                if not success:
                    raise StopChatFlow(
                        f"Failed to add node {self.selected_node.node_id} to network"
                        f" {wid}"
                    )
            self.network_view_copy = self.network_view_copy.copy()
        free_ips = self.network_view_copy.get_node_free_ips(self.selected_node)
        self.ip_address = self.drop_down_choice(
            "Please choose IP Address for your solution", free_ips, default=free_ips[0]
        )

    @chatflow_step(title="Domain")
    def select_domain(self):
        self.gateways = {
            g.node_id: g
            for g in j.sals.zos._explorer.gateway.list()
            if j.sals.zos.nodes_finder.filter_is_up(g)
        }

        domains = dict()
        for gateway in self.gateways.values():
            for domain in gateway.managed_domains:
                domains[domain] = gateway

        self.domain = self.single_choice(
            "Please choose the domain you wish to use",
            list(domains.keys()),
            required=True,
        )

        self.gateway = domains[self.domain]
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
        self.metadata.update(self.log_config)
        self.md_show_confirm(self.metadata)

    @chatflow_step(title="Reservation")
    def reservation(self):
        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": "peertube", "Solution name": self.solution_name},
        }
        # reserve subdomain
        _id = deployer.create_subdomain(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            subdomain=self.domain,
            addresses=self.addresses,
            solution_uuid=self.solution_id,
            **metadata,
        )

        success = deployer.wait_workload(_id, self)
        if not success:
            raise StopChatFlow(
                f"Failed to create subdomain {self.domain} on gateway"
                f" {self.gateway.node_id} {_id}"
            )
        self.threebot_url = f"https://{self.domain}"

        # expose threebot container
        _id = deployer.expose_address(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            network_name=self.network_view.name,
            local_ip=self.ip_address,
            port=80,
            tls_port=443,
            trc_secret=self.secret,
            node_id=self.selected_node.node_id,
            reserve_proxy=True,
            domain_name=self.domain,
            solution_uuid=self.solution_id,
            **metadata,
        )
        success = deployer.wait_workload(_id, self)
        if not success:
            # solutions.cancel_solution(self.workload_ids)
            raise StopChatFlow(
                f"Failed to create trc container on node {self.selected_node.node_id}"
                f" {_id}"
            )

        entrypoint = f'/usr/local/bin/startup.sh "{self.domain}" "{self.email}"'
        self.entrypoint = entrypoint
        # reserve container
        self.resv_id = deployer.deploy_container(
            pool_id=self.pool_id,
            node_id=self.selected_node.node_id,
            network_name=self.network_view.name,
            ip_address=self.ip_address,
            flist=self.FLIST_URL,
            cpu=self.resources["cpu"],
            memory=self.resources["memory"],
            disk_size=self.resources["disk_size"],
            entrypoint=entrypoint,
            env={"pub_key": self.public_key},
            interactive=False,
            log_config=self.log_config,
            **metadata,
            solution_uuid=self.solution_id,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

    @chatflow_step(title="Success", disable_previous=True)
    def peertube_access(self):
        res = f"""\
# Peertube has been deployed successfully: your reservation id is: {self.resv_id}
To connect ```ssh root@{self.ip_address}```  ``` {self.threebot_url}```.It may take a few minutes.
                """
        self.md_show(res, md=True)


chat = Peertube
