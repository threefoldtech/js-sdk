import time
import uuid
import math
import random

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.reservation_chatflow import deployer, solutions


class CryptpadDeploy(GedisChatBot):
    steps = [
        "cryptpad_start",
        "cryptpad_name",
        "solution_specs",
        "select_pool",
        "cryptpad_network",
        "configuring_node",
        "overview",
        "reservation",
        "container_access",
    ]
    title = "Cryptpad"

    @chatflow_step()
    def cryptpad_start(self):
        self.solution_id = uuid.uuid4().hex
        self.flist_url = "https://hub.grid.tf/bola.3bot/3bot-cryptopad-latest.flist"
        self.user_form_data = dict()
        self.user_form_data["chatflow"] = "cryptpad"
        self.threebot_name = j.data.text.removesuffix(self.user_info()["username"], ".3bot")
        self.solution_metadata = {}
        self.md_show("# This wizard will help you deploy a cryptpad container", md=True)

    @chatflow_step(title="Solution name")
    def cryptpad_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            cryptpad_solutions = solutions.list_cryptpad_solutions(sync=False)
            valid = True
            for sol in cryptpad_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True

    @chatflow_step(title="Cryptpad storage size")
    def solution_specs(self):
        # set default resources
        self.resources = dict()
        self.resources["cpu"] = 1
        self.resources["memory"] = 1024
        self.resources["disk_size"] = 256
        self.resources["default_disk_type"] = "SSD"

        form = self.new_form()
        vol_disk_size = form.single_choice(
            "Please specify the cryptpad storage size in GBs", ["5", "10", "15"], default="10", required=True,
        )
        form.ask()
        self.vol_size = int(vol_disk_size.value)
        self.vol_mount_point = "/persistent-data"

    @chatflow_step(title="Pool")
    def select_pool(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024) + self.vol_size,
        }
        cu, su = deployer.calculate_capacity_units(**query)
        self.pool_id = deployer.select_pool(self, cu=cu, su=su)

    @chatflow_step(title="Network")
    def cryptpad_network(self):
        self.network_view = deployer.select_network(self)

    @chatflow_step(title="Configuring your cryptpad")
    def configuring_node(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": self.resources["disk_size"],
        }
        self.md_show_update("Preparing a node to deploy on ...")
        self.selected_node = deployer.schedule_container(self.pool_id, **query)

        self.md_show_update("Configuring node ip ...")
        self.network_view_copy = self.network_view.copy()
        result = deployer.add_network_node(
            self.network_view.name,
            self.selected_node,
            self.pool_id,
            self.network_view_copy,
            bot=self,
            **self.solution_metadata,
        )
        if result:
            for wid in result["ids"]:
                success = deployer.wait_workload(wid, self)
                if not success:
                    raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {wid}")
            self.network_view_copy = self.network_view_copy.copy()
        free_ips = self.network_view_copy.get_node_free_ips(self.selected_node)
        self.ip_address = random.choice(free_ips)

        self.md_show_update("Preparing gateways ...")
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
        self.solution_name = self.solution_name.replace(".", "").replace("_", "-")
        self.domain = f"{self.threebot_name}-{self.solution_name}.{self.domain}"

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
        }
        self.md_show_confirm(self.metadata)

    @chatflow_step(title="Reservation")
    def reservation(self):
        self.workload_ids = []
        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": "cryptpad", "Solution name": self.solution_name},
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
                flist=self.flist_url,
                cpu=self.resources["cpu"],
                memory=self.resources["memory"],
                disk_size=self.resources["disk_size"],
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

    @chatflow_step(title="Success", disable_previous=True)
    def container_access(self):
        res = f"""\
# Cryptpad has been deployed successfully:\n<br>
Reservation id: {self.workload_ids[-1]}\n
You can access your container from browser at {self.container_url_https} \n or \n {self.container_url_http}\n
# It may take a few minutes.
        """
        self.md_show(res, md=True)


chat = CryptpadDeploy
