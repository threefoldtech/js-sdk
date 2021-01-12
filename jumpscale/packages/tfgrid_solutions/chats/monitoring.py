import math
import uuid
from textwrap import dedent

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from jumpscale.sals.reservation_chatflow import DeploymentFailed, deployer, deployment_context, solutions


class MonitoringDeploy(GedisChatBot):
    steps = [
        "choose_name",
        "public_key_get",
        "prometheus_container_resources",
        "prometheus_volume_details",
        "grafana_container_resources",
        "redis_container_resources",
        "container_node_ids",
        "network_selection",
        "ip_selection",
        "reservation",
        "success",
    ]
    title = "Monitoring"

    def _deployment_start(self):
        deployer.chatflow_pools_check()
        deployer.chatflow_network_check(self)
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
        self.solution_metadata = {}

    @chatflow_step(title="Solution Name")
    def choose_name(self):
        self._deployment_start()
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            monitoring_solutions = solutions.list_monitoring_solutions(sync=False)
            valid = True
            for sol in monitoring_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another name.")
                    break
                valid = True

    @chatflow_step(title="SSH Key")
    def public_key_get(self):
        self.env_var_dict["SSH_KEY"] = self.upload_file(
            """Please add your public ssh key, this will allow you to access the deployed containers using ssh.
                Just upload the file with the key.
                Note: please use keys compatible with Dropbear server eg: rsa """,
            required=True,
        ).strip()

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
        self.query["Prometheus"]["disk_size"] += self.vol_size * 1024
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
        self.network_view = deployer.select_network(self, self.all_network_viewes)

    @chatflow_step(title="IP selection")
    @deployment_context()
    def ip_selection(self):
        self.md_show_update("Deploying Network on Nodes....")
        # deploy network on nodes
        for i in range(len(self.selected_nodes)):
            node = self.selected_nodes[i]
            pool_id = self.selected_pool_ids[i]
            result = deployer.add_network_node(
                self.network_view.name,
                node,
                pool_id,
                self.network_view,
                bot=self,
                owner=self.solution_metadata.get("owner"),
            )
            if not result:
                continue
            for wid in result["ids"]:
                success = deployer.wait_workload(wid, self, breaking_node_id=node.node_id)
                if not success:
                    raise DeploymentFailed(f"Failed to add node {node.node_id} to network {wid}", wid=wid)
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

    @chatflow_step(title="Reservation")
    @deployment_context()
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
            raise DeploymentFailed(
                f"Failed to deploy volume on node {self.selected_nodes[1].node_id} {vol_id}", wid=vol_id
            )
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
                raise DeploymentFailed(
                    f"Failed to deploy {self.tools_names[i]}",
                    solution_uuid=self.solution_id,
                    wid=self.reservation_ids[i],
                )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        message = f"""\
        ## Your containers have been deployed successfully
        <br />\n
        ### Prometheus

        - Access container by `ssh root@{self.ip_addresses[1]}` where you can manually customize the solutions you want to monitor
        - Access Prometheus UI through <a href="http://{self.ip_addresses[1]}:9090/graph" target="_blank">http://{self.ip_addresses[1]}:9090/graph</a> which is accessed through your browser

        ### Grafana

        - Access Grafana UI through <a href="http://{self.ip_addresses[2]}:3000" target="_blank">http://{self.ip_addresses[2]}:3000</a> which is accessed through your browser where you can manually configure to use prometheus

        ### Redis

        - Access redis cli via: `redis-cli -h {self.ip_addresses[0]}`
        """
        self.md_show(dedent(message), md=True)


chat = MonitoringDeploy
