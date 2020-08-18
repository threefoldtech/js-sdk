import math
import uuid
import random

from jumpscale.loader import j

# from jumpscale.packages.tfgrid_solutions.chats.cryptpad_deploy import CryptpadDeploy as BaseCryptpadDeploy
from jumpscale.sals.chatflows.chatflows import chatflow_step, StopChatFlow
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions

FARM_NAMES = ["freefarm"]


class CryptpadDeploy(MarketPlaceChatflow):

    steps = [
        "cryptpad_start",
        "cryptpad_name",
        "cryptpad_info",
        "cryptpad_expiration",
        "cryptpad_deployment",
        "overview",
        "reservation",
        "container_access",
    ]
    title = "Cryptpad"

    @chatflow_step()
    def cryptpad_start(self):
        self._validate_user()
        self.solution_id = uuid.uuid4().hex
        self.flist_url = "https://hub.grid.tf/bola.3bot/3bot-cryptopad-latest.flist"
        self.threebot_name = j.data.text.removesuffix(self.user_info()["username"], ".3bot")
        self.solution_metadata = {}
        self.solution_metadata["owner"] = self.user_info()["username"]
        self.md_show("# This wizard will help you deploy a cryptpad solution", md=True)

    @chatflow_step(title="Solution name")
    def cryptpad_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            cryptpad_solutions = solutions.list_cryptpad_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in cryptpad_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True
        self.solution_name = f"{self.solution_metadata['owner']}_{self.solution_name}"

    @chatflow_step()
    def cryptpad_info(self):
        #  # set default resources
        # self.resources = dict()
        # self.resources["cpu"] = 1
        # self.resources["memory"] = 1024
        # self.resources["disk_size"] = 256
        # self.resources["default_disk_type"] = "SSD"

        form = self.new_form()
        vol_disk_size = form.single_choice(
            "Please specify the cryptpad storage size in GBs", ["5", "10", "15"], default="10", required=True,
        )
        self.currency = form.single_choice(
            "Please select the currency you want to pay with.", ["TFT", "TFTA"], required=True
        )
        form.ask()
        self.vol_size = int(vol_disk_size.value)
        self.vol_mount_point = "/persistent-data"
        self.currency = self.currency.value
        self.query = {"cru": 1, "mru": 1, "sru": self.vol_size + 1}

    @chatflow_step(title="Expiration")
    def cryptpad_expiration(self):
        self.expiration = deployer.ask_expiration(self)
        # print(self.expiration)

    @chatflow_step(title="Deployment")
    def cryptpad_deployment(self):
        # this step provisions the pool for the solution and network if he is new user.
        # depends on:
        # create solution pool
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
            self.selected_node = deployer.schedule_container(self.pool_info.reservation_id, **self.query)
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

        self.md_show_update("Preparing gateways ...")
        gateways = deployer.list_all_gateways(self.solution_metadata["owner"])
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
            "CPU": self.query["cru"],
            "Memory": self.query["mru"],
            "Disk Size": (self.query["sru"] - self.vol_size) * 1024,
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
            raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {vol_id}")
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
