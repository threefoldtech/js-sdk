import random
import math
from textwrap import dedent
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow import deployer, solutions, StopChatFlowCleanWorkloads
import uuid


class Publisher(GedisChatBot):
    steps = [
        "publisher_name",
        "select_pool",
        "publisher_network",
        "configuration",
        "domain_select",
        "overview",
        "deploy",
        "success",
    ]

    title = "Publisher"
    publishing_chatflow = "publisher"  # chatflow used to deploy the solution

    @chatflow_step()
    def _publisher_start(self):
        self.flist = "https://hub.grid.tf/ahmed_hanafy_1/ahmedhanafy725-pubtools-trc.flist"
        self.solution_id = uuid.uuid4().hex
        self.solution_currency = "TFT"
        self.storage_url = "zdb://hub.grid.tf:9900"
        self.resources = {"cpu": 1, "memory": 1024, "disk_size": 2048}
        self.solution_metadata = {}
        self.user_email = self.user_info()["email"]

    @chatflow_step(title="Solution name")
    def publisher_name(self):
        self._publisher_start()
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

    @chatflow_step()
    def publisher_info(self):
        form = self.new_form()
        self.solution_name = form.string_ask(
            "Please enter a name for your solution", required=True, is_identifier=True,
        )
        disk_sizes = [2, 5, 10]
        self.vol_size = form.single_choice("choose the disk size", disk_sizes, required=True, default=disk_sizes[0])
        self.currency = form.single_choice(
            "Please select the currency you want to pay with.", ["FreeTFT", "TFT", "TFTA"], required=True
        )
        form.ask()
        self.currency = self.currency.value
        self.query = {"cru": 1, "mru": 1, "sru": int(self.vol_size.value) + 1}

    @chatflow_step(title="Solution Settings")
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
            "EMAIL": self.user_email,
        }

        self.query = {
            "cru": self.resources["cpu"],
            "mru": math.ceil(self.resources["memory"] / 1024),
            "sru": math.ceil(self.resources["disk_size"] / 1024),
        }
        self.md_show_update("Preparing a node to deploy on ...")
        self.selected_node = deployer.schedule_container(self.pool_id, **self.query)

    @chatflow_step(title="Domain")
    def domain_select(self):
        self.md_show_update("Preparing gateways ...")
        gateways = deployer.list_all_gateways()
        if not gateways:
            raise StopChatFlowCleanWorkloads(
                "There are no available gateways in the farms bound to your pools.", self.solution_id
            )

        domains = dict()
        for gw_dict in gateways.values():
            gateway = gw_dict["gateway"]
            for domain in gateway.managed_domains:
                domains[domain] = gw_dict

        self.domain = random.choice(list(domains.keys()))

        while True:
            self.sub_domain = self.string_ask(
                f"Please choose the sub domain you wish to use, eg <subdomain>.{self.domain}", required=True
            )
            if "." in self.sub_domain:
                self.md_show("you can't nest domains. please try again")
                continue
            if j.tools.dnstool.is_free(self.sub_domain + "." + self.domain):
                break
            else:
                self.md_show(f"the specified domain {self.sub_domain + '.' + self.domain} is already registered")
        self.gateway = domains[self.domain]["gateway"]
        self.gateway_pool = domains[self.domain]["pool"]

        self.domain = f"{self.sub_domain}.{self.domain}"
        self.envars["DOMAIN"] = self.domain
        self.addresses = []
        for ns in self.gateway.dns_nameserver:
            self.addresses.append(j.sals.nettools.get_host_by_name(ns))

        self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

    @chatflow_step(title="Confirmation")
    def overview(self):
        info = {"Solution name": self.solution_name, "domain": self.domain}
        self.md_show_confirm(info)

    @chatflow_step(title="Reservation", disable_previous=True)
    def deploy(self):
        # 1- deploy network on selected node
        metadata = {
            "name": self.solution_name,
            "form_info": {"Solution name": self.solution_name, "chatflow": self.publishing_chatflow},
        }
        self.solution_metadata.update(metadata)
        self.workload_ids = []
        self.network_view = self.network_view.copy()
        result = deployer.add_network_node(
            self.network_view.name,
            self.selected_node,
            self.pool_id,
            self.network_view,
            bot=self,
            owner=self.solution_metadata.get("owner"),
        )
        if result:
            for wid in result["ids"]:
                success = deployer.wait_workload(wid, self, breaking_node_id=self.selected_node.node_id)
                if not success:
                    raise StopChatFlowCleanWorkloads(
                        f"Failed to add node {self.selected_node.node_id} to network {wid}", self.solution_id
                    )
        self.network_view_copy = self.network_view.copy()
        self.ip_address = self.network_view_copy.get_free_ip(self.selected_node)

        # 2- reserve subdomain
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
            raise StopChatFlowCleanWorkloads(
                f"Failed to create subdomain {self.domain} on gateway {self.gateway.node_id} {self.workload_ids[0]}",
                self.solution_id,
            )

        # 3- reserve tcp proxy
        self.workload_ids.append(
            deployer.create_proxy(
                pool_id=self.gateway_pool.pool_id,
                gateway_id=self.gateway.node_id,
                domain_name=self.domain,
                trc_secret=self.secret,
                solution_uuid=self.solution_id,
                **self.solution_metadata,
            )
        )
        success = deployer.wait_workload(self.workload_ids[1], self)
        if not success:
            raise StopChatFlowCleanWorkloads(
                f"Failed to create reverse proxy {self.domain} on gateway {self.gateway.node_id} {self.workload_ids[1]}",
                self.solution_id,
            )

        # 4- deploy container
        self.envars["TRC_REMOTE"] = f"{self.gateway.dns_nameserver[0]}:{self.gateway.tcp_router_port}"
        self.envars["DOMAIN"] = self.domain
        self.envars["TEST_CERT"] = "true" if j.config.get("TEST_CERT") else "false"
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
                public_ipv6=True,
                **self.solution_metadata,
            )
        )
        if not success:
            raise StopChatFlowCleanWorkloads(
                f"Failed to create container on node {self.selected_node.node_id} {self.workload_ids[2]}",
                self.solution_id,
            )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        message = f"""\
# Congratulations! Your own {self.publishing_chatflow}  deployed successfully:
\n<br />\n
- You can access it via the browser using: <a href="https://{self.domain}" target="_blank">https://{self.domain}</a>
\n<br />\n
- This domain maps to your container with ip: `{self.ip_address}`
                """
        self.md_show(dedent(message), md=True)


chat = Publisher
