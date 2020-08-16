import math

from jumpscale.sals.chatflows.chatflows import chatflow_step, StopChatFlow
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions
import uuid
import random
from jumpscale.loader import j

FARM_NAMES = ["freefarm"]


class Peertube(MarketPlaceChatflow):
    FLIST_URL = "https://hub.grid.tf/omar0.3bot/omarelawady-peertube-latest.flist"

    steps = [
        "peertube_start",
        "peertube_name",
        "peertube_currency",
        "peertube_email",
        "peertube_expiration",
        "volume_details",
        # "select_pool",
        # "peertube_network",
        "peertube_deploy",
        "overview",
        "reservation",
        "peertube_access",
    ]

    title = "Peertube"

    @chatflow_step()
    def peertube_start(self):
        self._validate_user()
        self.solution_id = uuid.uuid4().hex
        self.user_form_data = dict()
        self.query = dict()
        self.user_form_data["chatflow"] = "peertube"
        self.md_show("# This wizard will help you deploy peertube", md=True)
        self.threebot_name = j.data.text.removesuffix(self.user_info()["username"], ".3bot")
        self.solution_metadata = {}
        self.solution_metadata["owner"] = self.user_info()["username"]

    @chatflow_step(title="Solution name")
    def peertube_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            peertube_solutions = solutions.list_peertube_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in peertube_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True
        # self.solution_name = f"{self.threebot_name}-{self.solution_name}"

    @chatflow_step(title="Currency")
    def peertube_currency(self):
        self.currency = self.single_choice(
            "please select the currency you wish ", ["FreeTFT", "TFT", "TFTA"], required=True
        )

    @chatflow_step(title="Email")
    def peertube_email(self):
        self.email = deployer.ask_email(self)

    @chatflow_step()
    def peertube_expiration(self):
        self.expiration = deployer.ask_expiration(self)
        print(self.expiration)

    @chatflow_step(title="Volume details")
    def volume_details(self):
        form = self.new_form()
        vol_disk_size = form.single_choice(
            "Please specify the peertube storage size in GBs", ["5", "15", "35"], default="5", required=True,
        )
        form.ask()
        self.vol_size = int(vol_disk_size.value)
        self.vol_mount_point = "/var/www/peertube/storage/"

        # Next steps
        self.container_resources()

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

    @chatflow_step()
    def peertube_deploy(self):
        # this step provisions the pool for the solution and network if he is new user.
        available_farms = []
        for farm_name in FARM_NAMES:
            available, _, _, _, _ = deployer.check_farm_capacity(farm_name, currencies=[self.currency], **self.query)
            if available:
                available_farms.append(farm_name)

        self.farm_name = random.choice(available_farms)

        user_networks = solutions.list_network_solutions(self.solution_metadata["owner"])
        networks_names = [n["Name"] for n in user_networks]
        if "apps" in networks_names:
            # old user
            self.pool_info = deployer.create_solution_pool(
                bot=self,
                username=self.solution_metadata["owner"],
                farm_name=self.farm_name,
                expiration=self.expiration,
                currency=self.currency,
                **self.query,
            )
            result = deployer.wait_pool_payment(self, self.pool_info.reservation_id)
            # import pdb; pdb.set_trace()
            self.wgconf = None
            if not result:
                raise StopChatFlow(f"Waiting for pool payment timedout. pool_id: {self.pool_info.reservation_id}")
        else:
            # new user
            self.pool_info, self.wgconf = deployer.init_new_user(
                bot=self,
                username=self.solution_metadata["owner"],
                farm_name=self.farm_name,
                expiration=self.expiration,
                currency=self.currency,
                **self.query,
            )

        if not self.pool_info:
            raise StopChatFlow("Bye bye")

        self.pool_id = self.pool_info.reservation_id

        # get ip address
        self.network_view = deployer.get_network_view(f"{self.solution_metadata['owner']}_apps")
        self.ip_address = None
        while not self.ip_address:
            self.selected_node = deployer.schedule_container(self.pool_info.reservation_id)
            result = deployer.add_network_node(
                self.network_view.name,
                self.selected_node,
                self.pool_info.reservation_id,
                self.network_view,
                bot=self,
                owner=self.solution_metadata.get("owner"),
            )
            if result:
                self.md_show_update("Deploying Network on Nodes....")
                for wid in result["ids"]:
                    success = deployer.wait_workload(wid)
                    if not success:
                        raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {wid}")
                self.network_view = self.network_view.copy()
            self.ip_address = self.network_view.get_free_ip(self.selected_node)

        # Next steps
        self.select_domain()

    # @chatflow_step(title="Pool")
    # def select_pool(self):
    #     cu, su = deployer.calculate_capacity_units(**self.query)
    #     self.pool_id = deployer.select_pool(self, cu=cu, su=su)

    # @chatflow_step(title="Network")
    # def peertube_network(self):
    #     self.network_view = deployer.select_network(self)
    #     self.container_node_id()
    #     self.select_domain()

    def select_domain(self):
        gateways = deployer.list_all_gateways(self.user_info()["username"])
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
            raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {vol_id}")
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
            **self.solution_metadata,
        )
        success = deployer.wait_workload(_id, self)
        if not success:
            # solutions.cancel_solution(self.workload_ids)
            raise StopChatFlow(f"Failed to create trc container on node {self.selected_node.node_id}" f" {_id}")

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
            env={"pub_key": ""},
            volumes=volume_config,
            interactive=False,
            **self.solution_metadata,
            solution_uuid=self.solution_id,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

    @chatflow_step(title="Success", disable_previous=True)
    def peertube_access(self):
        res = f"""\
# Peertube has been deployed successfully: your reservation id is: {self.resv_id}
  ``` {self.threebot_url}```.It may take a few minutes.
                """
        self.md_show(res, md=True)


chat = Peertube
