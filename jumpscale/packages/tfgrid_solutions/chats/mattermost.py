import random
import uuid
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
from jumpscale.sals.reservation_chatflow import deployer, solutions


class MattermostDeploy(GedisChatBot):
    """
    Mattermost container deploy
    """

    steps = [
        "mattermost_name",
        "select_pool",
        "mattermost_network",
        "domain_select",
        "overview",
        "reservation",
        "container_acess",
    ]
    title = "Mattermost"

    def _mattermost_start(self):
        self.solution_id = uuid.uuid4().hex
        self.HUB_URL = "https://hub.grid.tf/ayoubm.3bot/rafyamgadbenjamin-mattermost-latest.flist"
        self.query = {"mru": 1, "cru": 2, "sru": 6}
        self.threebot_name = j.data.text.removesuffix(self.user_info()["username"], ".3bot")
        self.solution_metadata = {}

    @chatflow_step(title="Solution name")
    def mattermost_name(self):
        self._mattermost_start()
        self.solution_name = deployer.ask_name(self)

    @chatflow_step(title="Pool")
    def select_pool(self):
        cu, su = deployer.calculate_capacity_units(**self.query)
        self.pool_id = deployer.select_pool(self, cu=cu, su=su)

    @chatflow_step(title="Network")
    def mattermost_network(self):
        self.network_view = deployer.select_network(self)

    @chatflow_step(title="Domain")
    def domain_select(self):
        # select node
        self.md_show_update("Preparing a node to deploy on ...")
        self.selected_node = deployer.schedule_container(self.pool_id, **self.query)

        # select ip address
        self.md_show_update("Configuring node ip address ...")
        self.network_view_copy = self.network_view.copy()
        result = deployer.add_network_node(
            self.network_view.name, self.selected_node, self.pool_id, self.network_view_copy
        )
        if result:
            for wid in result["ids"]:
                success = deployer.wait_workload(wid, self)
                if not success:
                    raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {wid}")
            self.network_view_copy = self.network_view_copy.copy()
        free_ips = self.network_view_copy.get_node_free_ips(self.selected_node)
        self.ip_address = random.choice(free_ips)

        self.md_show_update("Configuring node domain ...")
        gateways = deployer.list_all_gateways()
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
        full_domain = j.sals.zos.gateway.correct_domain(full_domain)
        while True:
            if j.tools.dnstool.is_free(full_domain):
                self.domain = full_domain
                break
            else:
                random_number = random.randint(1000, 100000)
                full_domain = f"{self.threebot_name}-{solution_name}-{random_number}.{self.domain}"
                full_domain = j.sals.zos.gateway.correct_domain(full_domain)

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
            "Domain": self.domain,
            "IP Address": self.ip_address,
        }
        self.md_show_confirm(self.metadata)

    @chatflow_step(title="Reservation")
    def reservation(self):
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
        vol_size = 20
        vol_mount_point = "/var/lib/mysql/"
        volume_config = {}
        vol_id = deployer.deploy_volume(
            self.pool_id, self.selected_node.node_id, vol_size, solution_uuid=self.solution_id, **self.metadata,
        )
        success = deployer.wait_workload(vol_id, self)
        if not success:
            raise StopChatFlow(f"Failed to deploy volume on node {self.selected_node.node_id} {vol_id}")
        volume_config[vol_mount_point] = vol_id

        # Create container
        self.resv_id = deployer.deploy_container(
            pool_id=self.pool_id,
            node_id=self.selected_node.node_id,
            network_name=self.network_view.name,
            ip_address=self.ip_address,
            flist=self.HUB_URL,
            cpu=2,
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
    def container_acess(self):
        res = f"""\
# mattermost has been deployed successfully: your reservation id is: {self.resv_id}
It may take a few minutes.
open mattermost from browser at ```{self.domain}```
                """
        self.md_show(res, md=True)


chat = MattermostDeploy
