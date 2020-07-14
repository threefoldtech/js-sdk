import math

from jumpscale.clients.explorer.models import DiskType
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType


class MonitoringDeploy(GedisChatBot):
    steps = [
        "deployment_start",
        "network_selection",
        "solution_name",
        "public_key_get",
        "prometheus_container_resources",
        "prometheus_volume_details",
        "grafana_container_resources",
        "redis_container_resources",
        "container_node_id",
        "farm_selection",
        "prometheus_container_ip",
        "grafana_container_ip",
        "redis_container_ip",
        "expiration_time",
        "overview",
        "containers_pay",
        "success",
    ]
    title = "Monitoring"

    @chatflow_step()
    def deployment_start(self):
        self.user_info = self.user_info()
        j.sals.reservation_chatflow.validate_user(self.user_info)
        self.user_form_data = {}
        self.user_form_data["chatflow"] = "monitoring"
        self.md_show(
            "# This wizard will help you deploy a monitoring system that includes Prometheus, Grafana, and redis",
            md=True,
        )
        self.env_var_dict = {}
        self.prometheus_query = {}
        self.grafana_query = {}
        self.redis_query = {}
        self.query = {"Prometheus": self.prometheus_query, "Grafana": self.grafana_query, "Redis": self.redis_query}
        self.ip_addresses = {"Prometheus": "", "Grafana": "", "Redis": ""}

    @chatflow_step(title="Network")
    def network_selection(self):
        self.network = j.sals.reservation_chatflow.select_network(self, j.core.identity.me.tid)

    @chatflow_step(title="Solution name")
    def solution_name(self):
        self.user_form_data["Solution name"] = self.string_ask(
            "Please enter a name for your monitoring solution name", required=True, field="name"
        )

    @chatflow_step(title="Access keys")
    def public_key_get(self):
        self.user_form_data["Public key"] = self.upload_file(
            """Please add your public ssh key, this will allow you to access the deployed containers using ssh.
                    Just upload the file with the key""",
            required=True,
        ).split("\n")[0]

    @chatflow_step(title="Prometheus container resources")
    def prometheus_container_resources(self):
        form = self.new_form()
        cpu = form.int_ask(
            "Please add how many CPU cores are needed for the Prometheus container", default=1, required=True
        )
        memory = form.int_ask("Please add the amount of memory in MB", default=3072, required=True)
        rootfs_size = form.int_ask("Choose the amount of storage for your root filesystem in MiB", default=256)
        form.ask()

        self.prometheus_rootfs_type = DiskType.SSD
        self.user_form_data["Prometheus CPU"] = cpu.value
        self.user_form_data["Prometheus Memory"] = memory.value
        self.user_form_data["Prometheus Root filesystem Type"] = DiskType.SSD.name
        self.user_form_data["Prometheus Root filesystem Size"] = rootfs_size.value

        self.prometheus_query["mru"] = math.ceil(self.user_form_data["Prometheus Memory"] / 1024)
        self.prometheus_query["cru"] = self.user_form_data["Prometheus CPU"]
        storage_units = math.ceil(self.user_form_data["Prometheus Root filesystem Size"] / 1024)
        if self.prometheus_rootfs_type.value == "SSD":
            self.prometheus_query["sru"] = storage_units
        else:
            self.prometheus_query["hru"] = storage_units

    @chatflow_step(title="Prometheus volume details")
    def prometheus_volume_details(self):
        form = self.new_form()
        vol_disk_size = form.int_ask("Please specify the volume size in GiB", required=True, default=10)
        form.ask()
        self.prometheus_vol_disk_type = DiskType.SSD
        self.user_form_data["Prometheus Volume Disk type"] = DiskType.SSD.name
        self.user_form_data["Prometheus Volume Size"] = vol_disk_size.value

    @chatflow_step(title="Grafana container resources")
    def grafana_container_resources(self):
        form = self.new_form()
        cpu = form.int_ask(
            "Please add how many CPU cores are needed for the Grafana container", default=1, required=True
        )
        memory = form.int_ask("Please add the amount of memory in MB", default=1024, required=True)
        rootfs_size = form.int_ask("Choose the amount of storage for your root filesystem in MiB", default=256)
        form.ask()
        self.grafana_rootfs_type = DiskType.SSD
        self.user_form_data["Grafana CPU"] = cpu.value
        self.user_form_data["Grafana Memory"] = memory.value
        self.user_form_data["Grafana Root filesystem Type"] = DiskType.SSD.name
        self.user_form_data["Grafana Root filesystem Size"] = rootfs_size.value

        self.grafana_query["mru"] = math.ceil(self.user_form_data["Grafana Memory"] / 1024)
        self.grafana_query["cru"] = self.user_form_data["Grafana CPU"]
        storage_units = math.ceil(self.user_form_data["Grafana Root filesystem Size"] / 1024)
        if self.grafana_rootfs_type.value == "SSD":
            self.grafana_query["sru"] = storage_units
        else:
            self.grafana_query["hru"] = storage_units

    @chatflow_step(title="Redis container resources")
    def redis_container_resources(self):
        form = self.new_form()
        cpu = form.int_ask("Please add how many CPU cores are needed for the redis container", default=1, required=True)
        memory = form.int_ask("Please add the amount of memory in MB", default=1024, required=True)
        rootfs_size = form.int_ask("Choose the amount of storage for your root filesystem in MiB", default=256)
        form.ask()
        self.redis_rootfs_type = DiskType.SSD
        self.user_form_data["Redis CPU"] = cpu.value
        self.user_form_data["Redis Memory"] = memory.value
        self.user_form_data["Redis Root filesystem Type"] = DiskType.SSD.name
        self.user_form_data["Redis Root filesystem Size"] = rootfs_size.value

        self.redis_query["mru"] = math.ceil(self.user_form_data["Redis Memory"] / 1024)
        self.redis_query["cru"] = self.user_form_data["Redis CPU"]
        storage_units = math.ceil(self.user_form_data["Redis Root filesystem Size"] / 1024)
        if self.redis_rootfs_type.value == "SSD":
            self.redis_query["sru"] = storage_units
        else:
            self.redis_query["hru"] = storage_units

    @chatflow_step(title="Containers' node id")
    def container_node_id(self):
        self.env_var_dict["SSH_KEY"] = self.user_form_data["Public key"]
        # create new reservation
        self.reservation = j.sals.zos.reservation_create()
        self.nodes_selected = {"Prometheus": None, "Grafana": None, "Redis": None}
        self.tools_names = ["Prometheus", "Grafana", "Redis"]
        for name in self.tools_names:
            nodeid = self.string_ask(
                f"Please enter the nodeid you would like to deploy {name} on. If left empty a node will be chosen for you"
            )
            node_selected = None
            while nodeid:
                try:
                    node_selected = j.sals.reservation_chatflow.validate_node(
                        nodeid, self.query[name], self.network.currency
                    )
                    break
                except (j.exceptions.Value, j.exceptions.NotFound) as e:
                    message = f"<br> Please enter a different nodeid to deploy {name} on or leave it empty"
                    nodeid = self.string_ask(str(e) + message, html=True, retry=True)
            self.nodes_selected[name] = node_selected or None
            self.query[name]["currency"] = self.network.currency

    @chatflow_step(title="Container farms for Prometheus Grafana and Redis")
    def farm_selection(self):
        for name, node_id in self.nodes_selected.items():
            if not node_id:
                farms = j.sals.reservation_chatflow.get_farm_names(1, self, **self.query[name], message=name)
                self.nodes_selected[name] = j.sals.reservation_chatflow.get_nodes(
                    1, farm_names=farms, **self.query[name]
                )[0]

    @chatflow_step(title="Prometheus container IP")
    def prometheus_container_ip(self):
        self.prometheus_network = self.network.copy(j.core.identity.me.tid)
        self.prometheus_network.add_node(self.nodes_selected["Prometheus"])
        self.ip_addresses["Prometheus"] = self.prometheus_network.ask_ip_from_node(
            self.nodes_selected["Prometheus"], "Please choose IP Address for your Prometheus container"
        )
        self.user_form_data["Prometheus IP Address"] = self.ip_addresses["Prometheus"]

    @chatflow_step(title="Grafana container IP")
    def grafana_container_ip(self):
        self.grafana_network = self.prometheus_network.copy(j.core.identity.me.tid)
        self.grafana_network.add_node(self.nodes_selected["Grafana"])
        self.ip_addresses["Grafana"] = self.grafana_network.ask_ip_from_node(
            self.nodes_selected["Grafana"], "Please choose IP Address for your Grafana container"
        )
        self.user_form_data["Grafana IP Address"] = self.ip_addresses["Grafana"]

    @chatflow_step(title="Redis container IP")
    def redis_container_ip(self):
        self.redis_network = self.grafana_network.copy(j.core.identity.me.tid)
        self.redis_network.add_node(self.nodes_selected["Redis"])
        self.ip_addresses["Redis"] = self.redis_network.ask_ip_from_node(
            self.nodes_selected["Redis"], "Please choose IP Address for your Redis container"
        )
        self.user_form_data["Redis IP Address"] = self.ip_addresses["Redis"]

    @chatflow_step(title="Expiration time")
    def expiration_time(self):
        self.expiration = self.datetime_picker(
            "Please enter solution expiration time.",
            required=True,
            min_time=[3600, "Date/time should be at least 1 hour from now"],
            default=j.data.time.get().timestamp + 3900,
        )
        self.user_form_data["Solution expiration"] = j.data.time.get(self.expiration).humanize()

    @chatflow_step(title="Confirmation")
    def overview(self):
        self.md_show_confirm(self.user_form_data)

    @chatflow_step(title="Payment", disable_previous=True)
    def containers_pay(self):
        self.network = self.redis_network
        self.network.update(j.core.identity.me.tid, currency=self.network.currency, bot=self)

        storage_url = "zdb://hub.grid.tf:9900"
        redis_ip_address = self.ip_addresses["Redis"]

        # create redis container
        redis_flist = f"https://hub.grid.tf/ranatarek.3bot/redis_zinit.flist"

        redis_cont = j.sals.zos.container.create(
            reservation=self.reservation,
            node_id=self.nodes_selected["Redis"].node_id,
            network_name=self.network.name,
            ip_address=redis_ip_address,
            flist=redis_flist,
            storage_url=storage_url,
            disk_type=self.redis_rootfs_type,
            disk_size=self.user_form_data["Redis Root filesystem Size"],
            env=self.env_var_dict,
            interactive=False,
            entrypoint="",
            cpu=self.user_form_data["Redis CPU"],
            memory=self.user_form_data["Redis Memory"],
        )

        # create prometheus container
        prometheus_flist = "https://hub.grid.tf/tf-official-apps/prometheus:latest.flist"

        prometheus_cont = j.sals.zos.container.create(
            reservation=self.reservation,
            node_id=self.nodes_selected["Prometheus"].node_id,
            network_name=self.network.name,
            ip_address=self.ip_addresses["Prometheus"],
            flist=prometheus_flist,
            storage_url=storage_url,
            disk_type=self.prometheus_rootfs_type,
            disk_size=self.user_form_data["Prometheus Root filesystem Size"],
            env=self.env_var_dict,
            interactive=False,
            entrypoint="",
            cpu=self.user_form_data["Prometheus CPU"],
            memory=self.user_form_data["Prometheus Memory"],
        )
        j.sals.zos.container.add_logs(
            prometheus_cont,
            channel_type="redis",
            channel_host=redis_ip_address,
            channel_port=6379,
            channel_name="prometheus",
        )

        self.prometheus_volume = j.sals.zos.volume.create(
            self.reservation,
            self.nodes_selected["Prometheus"].node_id,
            size=self.user_form_data["Prometheus Volume Size"],
            type=self.prometheus_vol_disk_type,
        )
        j.sals.zos.volume.attach(container=prometheus_cont, volume=self.prometheus_volume, mount_point="/data")

        # create grafana container
        grafana_flist = "https://hub.grid.tf/azmy.3bot/grafana-grafana-latest.flist"

        grafana_cont = j.sals.zos.container.create(
            reservation=self.reservation,
            node_id=self.nodes_selected["Grafana"].node_id,
            network_name=self.network.name,
            ip_address=self.ip_addresses["Grafana"],
            flist=grafana_flist,
            storage_url=storage_url,
            disk_type=self.grafana_rootfs_type,
            disk_size=self.user_form_data["Grafana Root filesystem Size"],
            env={},
            interactive=False,
            entrypoint="",
            cpu=self.user_form_data["Grafana CPU"],
            memory=self.user_form_data["Grafana Memory"],
        )
        j.sals.zos.container.add_logs(
            grafana_cont, channel_type="redis", channel_host=redis_ip_address, channel_port=6379, channel_name="grafana"
        )

        metadata = dict()
        metadata["chatflow"] = self.user_form_data["chatflow"]
        metadata["Solution name"] = self.user_form_data["Solution name"]
        metadata["Solution expiration"] = self.user_form_data["Solution expiration"]
        metadata["Prometheus CPU"] = self.user_form_data["Prometheus CPU"]
        metadata["Prometheus Memory"] = self.user_form_data["Prometheus Memory"]
        metadata["Prometheus Root filesystem Type"] = self.user_form_data["Prometheus Root filesystem Type"]
        metadata["Prometheus Root filesystem Size"] = self.user_form_data["Prometheus Root filesystem Size"]
        metadata["Grafana CPU"] = self.user_form_data["Grafana CPU"]
        metadata["Grafana Memory"] = self.user_form_data["Grafana Memory"]
        metadata["Grafana Root filesystem Type"] = self.user_form_data["Grafana Root filesystem Type"]
        metadata["Grafana Root filesystem Size"] = self.user_form_data["Grafana Root filesystem Size"]
        metadata["Redis CPU"] = self.user_form_data["Redis CPU"]
        metadata["Redis Memory"] = self.user_form_data["Redis Memory"]
        metadata["Redis Root filesystem Type"] = self.user_form_data["Redis Root filesystem Type"]
        metadata["Redis Root filesystem Size"] = self.user_form_data["Redis Root filesystem Size"]

        metadata["Prometheus IP"] = self.user_form_data["Prometheus IP Address"]
        metadata["Grafana IP"] = self.user_form_data["Grafana IP Address"]
        metadata["Redis IP"] = self.user_form_data["Redis IP Address"]

        res = j.sals.reservation_chatflow.get_solution_metadata(
            self.user_form_data["Solution name"], SolutionType.Monitoring, metadata
        )
        reservation = j.sals.reservation_chatflow.add_reservation_metadata(self.reservation, res)
        self.resv_id = j.sals.reservation_chatflow.register_and_pay_reservation(
            reservation, self.expiration, customer_tid=j.core.identity.me.tid, currency=self.network.currency, bot=self
        )

        j.sals.reservation_chatflow.save_reservation(
            self.resv_id, self.user_form_data["Solution name"], SolutionType.Monitoring, self.user_form_data
        )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        res = f"""\
# Your containers have been deployed successfully. Your reservation id is: {self.resv_id}
## Prometheus
#### Access container by ```ssh root@{self.ip_addresses["Prometheus"]}``` where you can manually customize the solutions you want to monitor <br /><br />

#### Access Prometheus UI through ```{self.ip_addresses["Prometheus"]}:9090/graph``` which is accessed through your browser <br /><br />
## Grafana <br />
#### Access Grafana UI through ```{self.ip_addresses["Grafana"]}:3000``` which is accessed through your browser where you can manually configure to use prometheus <br /><br />
## Redis <br />
#### Access redis cli through ```redis-cli -h {self.ip_addresses["Redis"]}``` <br /><br />
## It may take a few minutes.
            """
        self.md_show(res, md=True)


chat = MonitoringDeploy
