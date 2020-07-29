import math
from textwrap import dedent
import toml
import requests

from jumpscale.clients.explorer.models import DiskType
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.reservation_chatflow import deployer, solutions
import uuid


class Publisher(GedisChatBot):
    steps = [
        "start",
        "publisher_name",
        "select_pool",
        "publisher_network",
        "configuration",
        "upload_public_key",
        "container_node_id",
        "domain_select",
        "ipv6_config",
        "overview",
        "deploy",
        "success",
    ]

    title = "Publisher"

    @chatflow_step()
    def start(self):
        self.flist = "https://hub.grid.tf/ahmed_hanafy_1/ahmedhanafy725-pubtools-trc.flist"
        self.solution_id = uuid.uuid4().hex
        self.solution_currency = "TFT"
        self.storage_url = "zdb://hub.grid.tf:9900"
        self.resources = {"cpu": 1, "memory": 1024, "disk_size": 2048}
        self.md_show("This wizard will help you publish a Wiki, a Website or Blog", md=True)
        self.solution_metadata = {}

    @chatflow_step(title="Solution name")
    def publisher_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            publisher_solutions = solutions.list_publisher_solutions(sync=False)
            valid = True
            for sol in publisher_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True

    @chatflow_step(title="Pool")
    def select_pool(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        cu, su = deployer.calculate_capacity_units(**query)
        self.pool_id = deployer.select_pool(self, cu=cu, su=su, **query)

    @chatflow_step(title="Network")
    def publisher_network(self):
        self.network_view = deployer.select_network(self)

    @chatflow_step(title="Solution name")
    def configuration(self):
        form = self.new_form()
        ttype = form.single_choice("Choose the type", options=["wiki", "www", "blog"], default="wiki", required=True)
        title = form.string_ask("Title", required=True)
        url = form.string_ask("Repository url", required=True)
        branch = form.string_ask("Branch", required=True)
        form.ask("Set configuration")

        self.envars = {
            "TYPE": ttype.value,
            "NAME": "entrypoint",
            "TITLE": title.value,
            "URL": url.value,
            "BRANCH": branch.value,
            "EMAIL": self.user_info()["email"],
        }

    @chatflow_step(title="Access key")
    def upload_public_key(self):
        self.public_key = self.upload_file(
            "Please upload your public ssh key, this will allow you to access your container using ssh", required=True
        ).strip()

    @chatflow_step(title="Container node id")
    def container_node_id(self):
        query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        self.selected_node = deployer.ask_container_placement(self, self.pool_id, **query)
        if not self.selected_node:
            self.selected_node = deployer.schedule_container(self.pool_id, **query)

    @chatflow_step(title="Domain")
    def domain_select(self):
        self.gateways = {
            g.node_id: g for g in j.sals.zos._explorer.gateway.list() if j.sals.zos.nodes_finder.filter_is_up(g)
        }

        domains = dict()
        for gateway in self.gateways.values():
            for domain in gateway.managed_domains:
                domains[domain] = gateway

        self.domain = self.single_choice(
            "Please choose the domain you wish to use", list(domains.keys()), required=True
        )
        while True:
            self.sub_domain = self.string_ask(
                f"Please choose the sub domain you wish to use, eg <subdomain>.{self.domain}", required=True
            )
            if j.tools.dnstool.is_free(self.sub_domain + "." + self.domain):
                break
            else:
                self.md_show(f"the specified domain {self.sub_domain + '.' + self.domain} is already registered")
        self.gateway = domains[self.domain]
        self.domain = f"{self.sub_domain}.{self.domain}"

        self.envars["DOMAIN"] = self.domain

        self.addresses = []
        for ns in self.gateway.dns_nameserver:
            self.addresses.append(j.sals.nettools.get_host_by_name(ns))

        self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

    @chatflow_step(title="Global IPv6 Address")
    def ipv6_config(self):
        self.public_ipv6 = deployer.ask_ipv6(self)

    @chatflow_step(title="Confirmation")
    def overview(self):
        info = {"Solution name": self.solution_name, "domain": self.domain}
        self.md_show_confirm(info)

    @chatflow_step(title="Reservation", disable_previous=True)
    def deploy(self):
        # 1- deploy network on selected node
        metadata = {
            "name": self.solution_name,
            "form_info": {"Solution name": self.solution_name, "chatflow": "publisher"},
        }
        self.solution_metadata.update(metadata)
        self.workload_ids = []
        self.network_view_copy = self.network_view.copy()
        result = deployer.add_network_node(
            self.network_view.name, self.selected_node, self.pool_id, self.network_view_copy, **self.solution_metadata
        )
        if result:
            for wid in result["ids"]:
                success = deployer.wait_workload(wid, self)
                if not success:
                    raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {wid}")
        self.ip_address = self.network_view_copy.get_free_ip(self.selected_node)

        # 2- reserve subdomain
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

        # 3- reserve tcp proxy
        self.workload_ids.append(
            deployer.create_proxy(
                pool_id=self.pool_id,
                gateway_id=self.gateway.node_id,
                domain_name=self.domain,
                trc_secret=self.secret,
                solution_uuid=self.solution_id,
                **self.solution_metadata,
            )
        )
        success = deployer.wait_workload(self.workload_ids[1], self)
        if not success:
            solutions.cancel_solution(self.workload_ids)
            raise StopChatFlow(
                f"Failed to create reverse proxy {self.domain} on gateway {self.gateway.node_id} {self.workload_ids[1]}"
            )

        # 4- deploy container
        self.envars["SSHKEY"] = self.public_key
        self.envars["TRC_REMOTE"] = f"{self.gateway.dns_nameserver[0]}:{self.gateway.tcp_router_port}"
        secret_env = {"TRC_SECRET": self.secret}
        self.workload_ids.append(
            deployer.deploy_container(
                pool_id=self.pool_id,
                node_id=self.selected_node.node_id,
                network_name=self.network_view.name,
                ip_address=self.ip_address,
                flist=self.flist,
                env=self.envars,
                cpu=self.resources["cpu"],
                memory=self.resources["memory"],
                disk_size=self.resources["disk_size"],
                entrypoint="/bin/bash /start.sh",
                secret_env=secret_env,
                interactive=False,
                solution_uuid=self.solution_id,
                public_ipv6=self.public_ipv6,
                **self.solution_metadata,
            )
        )
        if not success:
            solutions.cancel_solution(self.workload_ids)
            raise StopChatFlow(
                f"Failed to create container on node {self.selected_node.node_id} {self.workload_ids[2]}"
            )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        message = f"""
        You can access your container using:
        Domain: {self.domain}
        IP address: {self.ip_address}
        """
        self.md_show(dedent(message), md=True)


chat = Publisher
