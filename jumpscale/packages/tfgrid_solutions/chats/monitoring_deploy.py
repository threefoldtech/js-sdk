import math

from jumpscale.clients.explorer.models import DiskType
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.reservation_chatflow import deployer, solutions
import uuid


class MonitoringDeploy(GedisChatBot):
    steps = [
        "deployment_start",
        "choose_name",
        "public_key_get",
        "prometheus_container_resources",
        "prometheus_volume_details",
        "grafana_container_resources",
        "redis_container_resources",
        "container_node_ids",
        "network_selection",
        "ip_selection",
        "overview",
        "reservation",
        "success",
    ]
    title = "Monitoring"

    @chatflow_step()
    def deployment_start(self):
        self.tools_names = ["Redis", "Prometheus", "Grafana"]
        self.flists = [
            "https://hub.grid.tf/tf-official-apps/redis_zinit.flist",
            "https://hub.grid.tf/tf-official-apps/prometheus:latest.flist",
            "https://hub.grid.tf/azmy.3bot/grafana-grafana-latest.flist",
        ]
        self.solution_id = uuid.uuid4().hex
        self.env_var_dict = dict()
        self.prometheus_query = dict()
        self.grafana_query = dict()
        self.redis_query = dict()
        self.query = {"Prometheus": self.prometheus_query, "Grafana": self.grafana_query, "Redis": self.redis_query}
        self.ip_addresses = {"Prometheus": "", "Grafana": "", "Redis": ""}
        self.md_show(
            "## This wizard will help you deploy a monitoring system that includes Prometheus, Grafana, and redis",
            md=True,
        )
        self.solution_metadata = {}

    @chatflow_step(title="Solution name")
    def choose_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            monitoring_solutions = solutions.list_monitoring_solutions(sync=False)
            valid = True
            for sol in monitoring_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True

    @chatflow_step(title="SSH Key")
    def public_key_get(self):
        self.env_var_dict["SSH_KEY"] = self.upload_file(
            """Please add your public ssh key, this will allow you to access the deployed containers using ssh.
                Just upload the file with the key.
                Note: please use keys compatible with Dropbear server eg: rsa """,
            required=True,
        ).split("\n")[0]

    @chatflow_step(title="Prometheus container resources")
    def prometheus_container_resources(self):
        self.prometheus_query = deployer.ask_container_resources(self)
        self.query["Prometheus"] = self.prometheus_query

    @chatflow_step(title="Prometheus volume details")
    def prometheus_volume_details(self):
        form = self.new_form()
        vol_disk_size = form.int_ask("Please specify the volume size in GiB", required=True, default=10, min=1)
        form.ask()
        self.vol_size = vol_disk_size.value
        self.query["Prometheus"]["disk_size"] += self.vol_size
        self.vol_mount_point = "/data"

    @chatflow_step(title="Grafana container resources")
    def grafana_container_resources(self):
        self.grafana_query = deployer.ask_container_resources(self)
        self.query["Grafana"] = self.grafana_query

    @chatflow_step(title="Redis container resources")
    def redis_container_resources(self):
        self.redis_query = deployer.ask_container_resources(self)
        self.query["Redis"] = self.redis_query

    @chatflow_step(title="Container's node ids")
    def container_node_ids(self):
        queries = []
        for name in self.tools_names:
            queries.append(
                {
                    "cru": self.query[name]["cpu"],
                    "mru": math.ceil(self.query[name]["memory"] / 1024),
                    "sru": math.ceil(self.query[name]["disk_size"] / 1024),
                }
            )
        self.selected_nodes, self.selected_pool_ids = deployer.ask_multi_pool_placement(
            self, 3, queries, workload_names=self.tools_names
        )

    @chatflow_step(title="Network")
    def network_selection(self):
        self.network_view = deployer.select_network(self)

    @chatflow_step(title="IP selection")
    def ip_selection(self):
        self.md_show_update("Deploying Network on Nodes....")
        # deploy network on nodes
        for i in range(len(self.selected_nodes)):
            node = self.selected_nodes[i]
            pool_id = self.selected_pool_ids[i]
            result = deployer.add_network_node(
                self.network_view.name, node, pool_id, self.network_view, bot=self, **self.solution_metadata
            )
            if not result:
                continue
            for wid in result["ids"]:
                success = deployer.wait_workload(wid)
                if not success:
                    raise StopChatFlow(f"Failed to add node {node.node_id} to network {wid}")
            self.network_view = self.network_view.copy()

        # get ip addresses
        self.ip_addresses = []
        for i in range(3):
            free_ips = self.network_view.get_node_free_ips(self.selected_nodes[i])
            self.ip_addresses.append(
                self.drop_down_choice(
                    f"Please choose IP Address for {self.tools_names[i]}", free_ips, required=True, default=free_ips[0]
                )
            )
            self.network_view.used_ips.append(self.ip_addresses[i])

    @chatflow_step(title="Confirmation")
    def overview(self):
        self.metatata = {
            "Solution Name": self.solution_name,
            "Network": self.network_view.name,
            "Prometheus Node ID": self.selected_nodes[1].node_id,
            "Prometheus CPU": self.query["Prometheus"]["cpu"],
            "Prometheus Memory": self.query["Prometheus"]["memory"],
            "Prometheus Disk Size": self.query["Prometheus"]["disk_size"],
            "Prometheus IP Address": self.ip_addresses[1],
            "Grafana Node ID": self.selected_nodes[2].node_id,
            "Grafana CPU": self.query["Grafana"]["cpu"],
            "Grafana Memory": self.query["Grafana"]["memory"],
            "Grafana Disk Size": self.query["Grafana"]["disk_size"],
            "Grafana IP Address": self.ip_addresses[2],
            "Redis Node ID": self.selected_nodes[0].node_id,
            "Redis CPU": self.query["Redis"]["cpu"],
            "Redis Memory": self.query["Redis"]["memory"],
            "Redis Disk Size": self.query["Redis"]["disk_size"],
            "Redis IP Address": self.ip_addresses[0],
        }
        self.md_show_confirm(self.metatata)

    @chatflow_step(title="Reservation")
    def reservation(self):
        metadata = {
            "name": self.solution_name,
            "form_info": {"chatflow": "monitoring", "Solution name": self.solution_name,},
        }
        self.solution_metadata.update(metadata)
        self.md_show_update("Deploying Volume....")

        vol_id = deployer.deploy_volume(
            self.selected_pool_ids[1],
            self.selected_nodes[1].node_id,
            self.vol_size,
            solution_uuid=self.solution_id,
            **self.solution_metadata,
        )
        success = deployer.wait_workload(vol_id, self)
        if not success:
            raise StopChatFlow(f"Failed to add node {self.nodes_selected['Prometheus'].node_id} to network {vol_id}")
        volume_configs = [{}, {self.vol_mount_point: vol_id}, {}]

        log_configs = [
            {},
            {
                "channel_type": "redis",
                "channel_host": self.ip_addresses[0],
                "channel_port": 6379,
                "channel_name": "prometheus",
            },
            {
                "channel_type": "redis",
                "channel_host": self.ip_addresses[0],
                "channel_port": 6379,
                "channel_name": "grafana",
            },
        ]

        self.reservation_ids = []

        for i in range(3):
            self.md_show_update(f"Deploying {self.tools_names[i]}....")
            flist = self.flists[i]
            node = self.selected_nodes[i]
            pool_id = self.selected_pool_ids[i]
            volume_config = volume_configs[i]
            log_config = log_configs[i]
            ip_address = self.ip_addresses[i]
            self.reservation_ids.append(
                deployer.deploy_container(
                    pool_id=pool_id,
                    node_id=node.node_id,
                    network_name=self.network_view.name,
                    ip_address=ip_address,
                    flist=flist,
                    cpu=self.query[self.tools_names[i]]["cpu"],
                    memory=self.query[self.tools_names[i]]["memory"],
                    disk_size=self.query[self.tools_names[i]]["disk_size"],
                    env=self.env_var_dict,
                    interactive=False,
                    entrypoint="",
                    volumes=volume_config,
                    log_config=log_config,
                    **self.solution_metadata,
                    solution_uuid=self.solution_id,
                )
            )
            success = deployer.wait_workload(self.reservation_ids[i], self)
            if not success:
                solutions.cancel_solution(self.reservation_ids)
                raise StopChatFlow(f"Failed to deploy {self.tools_names[i]}")

    @chatflow_step(title="Success", disable_previous=True)
    def success(self):
        res = f"""\
## Your containers have been deployed successfully. Your reservation ids are:
\n<br/>\n
- `{self.reservation_ids[0]}`, `{self.reservation_ids[1]}`, `{self.reservation_ids[2]}`
\n<br/>\n
### Prometheus
- Access container by `ssh root@{self.ip_addresses[1]}` where you can manually customize the solutions you want to monitor
- Access Prometheus UI through <a href="http://{self.ip_addresses[1]}:9090/graph" target="_blank">http://{self.ip_addresses[1]}:9090/graph</a> which is accessed through your browser
\n<br />\n
### Grafana
- Access Grafana UI through <a href="http://{self.ip_addresses[2]}:3000" target="_blank">http://{self.ip_addresses[2]}:3000</a> which is accessed through your browser where you can manually configure to use prometheus
\n<br />\n
### Redis
- Access redis cli via: `redis-cli -h {self.ip_addresses[0]}`
\n<br />\n
#### It may take a few minutes.
            """
        self.md_show(res, md=True)


chat = MonitoringDeploy
