import math
import uuid
import requests
from textwrap import dedent

from jumpscale.clients.explorer.models import DiskType
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.reservation_chatflow import (
    DeploymentFailed,
    deployer,
    solutions,
    deployment_context,
)


class EtcdDeploy(GedisChatBot):
    steps = [
        "etcd_name",
        "etcd_no_nodes",
        "containers_resources",
        "select_pool",
        "etcd_network",
        "ipv6_config",
        "container_node_id",
        "etcd_ip",
        "reservation",
        "success",
    ]
    title = "ETCD"

    def _cluster_start(self):
        deployer.chatflow_pools_check()
        deployer.chatflow_network_check(self)
        self.solution_id = uuid.uuid4().hex
        self.env = dict()
        self.solution_metadata = {}

    @chatflow_step(title="Solution Name")
    def etcd_name(self):
        self._cluster_start()
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            etcd_solutions = solutions.list_etcd_solutions(sync=False)
            valid = True
            for sol in etcd_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another name.")
                    break
                valid = True

    @chatflow_step(title="ETCD Number of Nodes")
    def etcd_no_nodes(self):
        form = self.new_form()
        self.no_nodes = form.int_ask("Enter number of etcd nodes", default=1, required=True, min=1)
        form.ask()

    @chatflow_step(title="Container(s)' Resources")
    def containers_resources(self):
        self.resources = deployer.ask_container_resources(self, default_disk_size=1024)

    @chatflow_step(title="Pool")
    def select_pool(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        cu, su = deployer.calculate_capacity_units(**query)
        self.pool_id = deployer.select_pool(self, cu=cu, su=su, **query)

    @chatflow_step(title="Global IPv6 Address")
    def ipv6_config(self):
        self.public_ipv6 = deployer.ask_ipv6(self)
        if self.public_ipv6:
            self.ip_version = "IPv6"
        else:
            self.ip_version = None

    @chatflow_step(title="Container(s) Node ID")
    def container_node_id(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        self.selected_node = deployer.ask_container_placement(self, self.pool_id, ip_version=self.ip_version, **query)
        if not self.selected_node:
            self.selected_node = deployer.schedule_container(self.pool_id, ip_version=self.ip_version, **query)

    @chatflow_step(title="Network")
    def etcd_network(self):
        self.network_view = deployer.select_network(self, self.all_network_viewes)

    @chatflow_step(title="ETCD Node(s) IP")
    @deployment_context()
    def etcd_ip(self):
        result = deployer.add_network_node(
            self.network_view.name,
            self.selected_node,
            self.pool_id,
            self.network_view,
            bot=self,
            owner=self.solution_metadata.get("owner"),
        )
        if result:
            self.md_show_update("Deploying Network on Nodes....")
            for wid in result["ids"]:
                success = deployer.wait_workload(wid, self, breaking_node_id=self.selected_node.node_id)
                if not success:
                    raise DeploymentFailed(f"Failed to add node {self.selected_node.node_id} to network {wid}", wid=wid)
            self.network_view = self.network_view.copy()

        self.ip_addresses = []
        self.etcd_clutser = ""
        for n in range(self.no_nodes.value):
            free_ips = self.network_view.get_node_free_ips(self.selected_node)
            ip = self.drop_down_choice(
                f"Please choose IP Address for ETCD Node {n+1}", free_ips, default=free_ips[0], required=True,
            )
            self.network_view.used_ips.append(ip)
            self.ip_addresses.append(ip)
            self.etcd_clutser = self.etcd_clutser + f"etcd_{n+1}=http://{ip}:2380,"

    @chatflow_step(title="Reservation")
    @deployment_context()
    def reservation(self):
        self.etcd_flist = "https://hub.grid.tf/essam.3bot/bitnami-etcd-latest.flist"
        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": "etcd", "Solution name": self.solution_name},
        }
        self.solution_metadata.update(metadata)

        self.resv_ids = deployer.deploy_etcd_containers(
            self.pool_id,
            self.selected_node.node_id,
            self.network_view.name,
            self.ip_addresses,
            self.etcd_clutser,
            self.etcd_flist,
            self.resources["cpu"],
            self.resources["memory"],
            self.resources["disk_size"],
            self.public_ipv6,
            **self.solution_metadata,
            solution_uuid=self.solution_id,
        )
        for resv_id in self.resv_ids:
            success = deployer.wait_workload(resv_id, self)
            if not success:
                raise DeploymentFailed(
                    f"Failed to deploy workload {resv_id}", solution_uuid=self.solution_id, wid=resv_id
                )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        success_msg = ""
        for ip_address in self.ip_addresses:
            success_msg = success_msg + (
                f"<br />-`etcdctl --endpoints=http://{ip_address}:2379 put from:{ip_address} Hello`"
            )

        message = f"""\
        # Your ETCD has been deployed successfully:
        <br /> To try in your terminal:
        {success_msg}
        <br />`OK` message will appear after each put command
        """
        self.md_show(dedent(message), md=True)


chat = EtcdDeploy
