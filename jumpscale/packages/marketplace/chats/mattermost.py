from jumpscale.packages.tfgrid_solutions.chats.mattermost import MattermostDeploy as BaseMattermostDeploy
from jumpscale.sals.chatflows.chatflows import chatflow_step, StopChatFlow
from jumpscale.sals.marketplace import MarketPlaceChatflow, deployer, solutions
from jumpscale.loader import j
import uuid
import random

FARM_NAMES = ["freefarm"]


class MattermostDeploy(MarketPlaceChatflow):
    steps = [
        "mattermost_start",
        "mattermost_info",
        "mattermost_expiration",
        "mattermost_deployment",
        "reservation",
        "mattermost_acess",
    ]
    title = "Mattermost"

    @chatflow_step()
    def mattermost_start(self):
        self._validate_user()
        self.solution_metadata = dict()
        self.threebot_name = j.data.text.removesuffix(self.user_info()["username"], ".3bot")
        self.HUB_URL = "https://hub.grid.tf/ayoubm.3bot/rafyamgadbenjamin-mattermost-latest.flist"
        self.solution_id = uuid.uuid4().hex
        self.solution_metadata["owner"] = self.user_info()["username"]
        self.md_show("# This wizard wil help you deploy an mattermost container", md=True)

    @chatflow_step(title="Solution name")
    def mattermost_info(self):
        valid = False
        while not valid:
            self.solution_name = self.string_ask("Please enter a name for your mattermost", required=True)
            mattermost_solutions = solutions.list_mattermost_solutions(self.solution_metadata["owner"], sync=False)
            valid = True
            for sol in mattermost_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True
        self.solution_name = f"{self.solution_metadata['owner']}_{self.solution_name}"

        form = self.new_form()
        disk_sizes = [2, 5, 10]
        self.vol_size = form.single_choice("choose the disk size", disk_sizes, required=True, default=disk_sizes[0])
        self.currency = form.single_choice("please select the currency you wish ", ["TFT", "TFTA"], required=True)
        form.ask()
        self.currency = self.currency.value
        self.query = {"sru": int(self.vol_size.value) + 1}

    @chatflow_step()
    def mattermost_expiration(self):
        self.expiration = deployer.ask_expiration(self)

    @chatflow_step()
    def mattermost_deployment(self):
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

            result = deployer.wait_pool_payment(self, self.pool_info.reservation_id)
            if not result:
                raise StopChatFlow(f"Failed to reserve pool {self.pool_info.reservation_id}")
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
            raise StopChatFlow("Failed to find pool")

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

        self.md_show_update("Configuring node domain ...")
        gateways = deployer.list_all_gateways(f"{self.threebot_name}.3bot")
        if not gateways:
            raise StopChatFlow("There are no available gateways in the farms bound to your pools.")

        domains = dict()
        for gw_dict in gateways.values():
            gateway = gw_dict["gateway"]
            for domain in gateway.managed_domains:
                domains[domain] = gw_dict

        self.domain = self.single_choice(
            "Please choose the domain you wish to use", list(domains.keys()), required=True
        )
        self.gateway = domains[self.domain]["gateway"]
        self.gateway_pool = domains[self.domain]["pool"]

        solution_name = self.solution_name.replace(".", "")
        full_domain = f"{self.threebot_name}-{solution_name}.{self.domain}"
        while True:
            if j.tools.dnstool.is_free(full_domain):
                self.domain = full_domain
                break
            else:
                random_number = random.randint(1000, 100000)
                full_domain = f"{self.threebot_name}-{solution_name}-{random_number}.{self.domain}"

        self.addresses = []
        for ns in self.gateway.dns_nameserver:
            self.addresses.append(j.sals.nettools.get_host_by_name(ns))

        self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

    @chatflow_step(title="Reservation")
    def reservation(self):
        self.pool_id = self.pool_info.reservation_id
        var_dict = {
            "MYSQL_ROOT_PASSWORD": "mostest",
            "MYSQL_USER": "mmuser",
            "MYSQL_PASSWORD": "mostest",
            "MYSQL_DATABASE": "mattermost_db",
        }
        metadata = {
            "name": self.solution_name,
            "form_info": {"Solution name": self.solution_name, "Domain name": self.domain, "chatflow": "mattermost",},
        }
        self.solution_metadata.update(metadata)

        # reserve subdomain
        _id = deployer.create_subdomain(
            pool_id=self.gateway_pool.pool_id,
            gateway_id=self.gateway.node_id,
            subdomain=self.domain,
            addresses=self.addresses,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )

        success = deployer.wait_workload(_id, self)
        if not success:
            raise StopChatFlow(f"Failed to create subdomain {self.domain} on gateway" f" {self.gateway.node_id} {_id}")
        self.solution_url = f"https://{self.domain}"

        # create volume
        vol_mount_point = "/var/lib/mysql/"
        volume_config = {}
        vol_id = deployer.deploy_volume(
            self.pool_id,
            self.selected_node.node_id,
            int(self.vol_size.value),
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(vol_id, self)
        if not success:
            raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {vol_id}")
        volume_config[vol_mount_point] = vol_id

        # Create container
        self.resv_id = deployer.deploy_container(
            pool_id=self.pool_id,
            node_id=self.selected_node.node_id,
            network_name=self.network_view.name,
            ip_address=self.ip_address,
            flist=self.HUB_URL,
            cpu=1,
            memory=1024,
            env=var_dict,
            interactive=False,
            entrypoint="/start_mattermost.sh",
            volumes=volume_config,
            public_ipv6=True,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            solutions.cancel_solution([self.resv_id])
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

        # expose threebot container
        _id = deployer.expose_and_create_certificate(
            pool_id=self.pool_id,
            gateway_id=self.gateway.node_id,
            network_name=self.network_view.name,
            trc_secret=self.secret,
            domain=self.domain,
            email=self.user_info()["email"],
            solution_ip=self.ip_address,
            solution_port=8065,
            enforce_https=False,
            node_id=self.selected_node.node_id,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(_id, self)
        if not success:
            # solutions.cancel_solution(self.workload_ids)
            raise StopChatFlow(f"Failed to create trc container on node {self.selected_node.node_id}" f" {_id}")

    @chatflow_step(title="Success", disable_previous=True)
    def mattermost_acess(self):
        res = f"""\
# mattermost has been deployed successfully:
\n<br />\n
your reservation id is: {self.resv_id}
\n<br />\n
your container ip is: `{self.ip_address}`
\n<br />\n
open Mattermost from browser at <a href="http://{self.domain}" target="_blank">https://{self.domain}</a>
\n<br />\n
- It may take few minutes to load.
                """
        self.md_show(res, md=True)


chat = MattermostDeploy
