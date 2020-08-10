import math
import uuid
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.reservation_chatflow import deployer, solutions


class MattermostDeploy(GedisChatBot):
    """
    Mattermost container deploy
    """

    steps = [
        "mattermost_start",
        "mattermost_name",
        "select_pool",
        "mattermost_network",
        "public_key_get",
        "container_logs",
        "container_node_id",
        "container_ip",
        # "domain_select",
        "overview",
        "reservation",
        "intializing",
        "container_acess",
    ]
    title = "Mattermost"

    @chatflow_step()
    def mattermost_start(self):
        self.solution_id = uuid.uuid4().hex
        self.user_form_data = dict()
        self.HUB_URL = "https://hub.grid.tf/ayoubm.3bot/rafyamgadbenjamin-mattermost-latest.flist"
        self.md_show("# This wizard wil help you deploy an mattermost container", md=True)
        self.query = {"mru": 1, "cru": 2, "sru": 6}

    @chatflow_step(title="Solution name")
    def mattermost_name(self):
        self.solution_name = deployer.ask_name(self)

    @chatflow_step(title="Pool")
    def select_pool(self):
        cu, su = deployer.calculate_capacity_units(**self.query)
        self.pool_id = deployer.select_pool(self, cu=cu, su=su)

    @chatflow_step(title="Network")
    def mattermost_network(self):
        self.network_view = deployer.select_network(self)

    @chatflow_step(title="Access keys")
    def public_key_get(self):
        self.public_key = self.upload_file(
            """Please add your public ssh key, this will allow you to access the deployed container using ssh.
                    Just upload the file with the key""",
            required=True,
        ).split("\n")[0]

    @chatflow_step(title="Container logs")
    def container_logs(self):
        self.container_logs_option = self.single_choice(
            "Do you want to push the container logs (stdout and stderr) onto an external redis channel",
            ["YES", "NO"],
            default="NO",
        )
        if self.container_logs_option == "YES":
            self.log_config = deployer.ask_container_logs(self, self.solution_name)
        else:
            self.log_config = {}

    @chatflow_step(title="Container node id")
    def container_node_id(self):
        self.selected_node = deployer.ask_container_placement(self, self.pool_id, **self.query)
        if not self.selected_node:
            self.selected_node = deployer.schedule_container(self.pool_id, **self.query)

    @chatflow_step(title="Container IP")
    def container_ip(self):
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
        self.ip_address = self.drop_down_choice("Please choose IP Address for your solution", free_ips)

    # @chatflow_step(title="Domain")
    # def domain_select(self):
    #     gateways = deployer.list_all_gateways()
    #     if not gateways:
    #         raise StopChatFlow("There are no available gateways in the farms bound to your pools.")

    #     domains = dict()
    #     for gw_dict in gateways.values():
    #         gateway = gw_dict["gateway"]
    #         for domain in gateway.managed_domains:
    #             domains[domain] = gw_dict

    #     self.domain = self.single_choice(
    #         "Please choose the domain you wish to use", list(domains.keys()), required=True
    #     )
    #     while True:
    #         self.sub_domain = self.string_ask(
    #             f"Please choose the sub domain you wish to use, eg <subdomain>.{self.domain}", required=True
    #         )
    #         if "." in self.sub_domain:
    #             self.md_show("you can't nest domains. please try again")
    #             continue
    #         if j.tools.dnstool.is_free(self.sub_domain + "." + self.domain):
    #             break
    #         else:
    #             self.md_show(f"the specified domain {self.sub_domain + '.' + self.domain} is already registered")
    #     self.gateway = domains[self.domain]["gateway"]
    #     self.gateway_pool = domains[self.domain]["pool"]
    #     self.domain = f"{self.sub_domain}.{self.domain}"

    #     self.envars["DOMAIN"] = self.domain

    #     self.addresses = []
    #     for ns in self.gateway.dns_nameserver:
    #         self.addresses.append(j.sals.nettools.get_host_by_name(ns))

    #     self.secret = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

    @chatflow_step(title="Confirmation")
    def overview(self):
        self.metadata = {
            "Solution Name": self.solution_name,
            "Network": self.network_view.name,
            "Node ID": self.selected_node.node_id,
            "Pool": self.pool_id,
            "IP Address": self.ip_address,
        }
        self.md_show_confirm(self.metadata)

    @chatflow_step(title="Reservation")
    def reservation(self):
        var_dict = {
            "pub_key": self.public_key,
            "MYSQL_ROOT_PASSWORD": "mostest",
            "MYSQL_USER": "mmuser",
            "MYSQL_PASSWORD": "mostest",
            "MYSQL_DATABASE": "mattermost_test",
        }
        metadata = {
            "name": self.solution_name,
            "form_info": {"Solution name": self.solution_name, "chatflow": "mattermost",},
        }

        vol_size = 20
        vol_mount_point = "/var/lib/mysql/"
        volume_config = {}
        vol_id = deployer.deploy_volume(
            self.pool_id, self.selected_node.node_id, vol_size, solution_uuid=self.solution_id, **self.metadata,
        )
        success = deployer.wait_workload(vol_id, self)
        if not success:
            raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {vol_id}")
        volume_config[vol_mount_point] = vol_id

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
            entrypoint="/mm/docker-entry.sh",
            volumes=volume_config,
            log_config=self.log_config,
            public_ipv6=True,
            **metadata,
            solution_uuid=self.solution_id,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            solutions.cancel_solution([self.resv_id])
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

    @chatflow_step(title="Initializing", disable_previous=True)
    def intializing(self):
        self.md_show_update("Initializing your Threebot ...")
        if not j.sals.nettools.wait_http_test(self.ip_address, timeout=600):
            self.stop("Failed to initialize threebot, please contact support")

    @chatflow_step(title="Success", disable_previous=True)
    def container_acess(self):
        res = f"""\
# mattermost has been deployed successfully: your reservation id is: {self.resv_id}
To connect ```ssh root@{self.ip_address}``` .It may take a few minutes.
open mattermost from browser at ```{self.ip_address}:8065```
                """
        self.md_show(res, md=True)


chat = MattermostDeploy
