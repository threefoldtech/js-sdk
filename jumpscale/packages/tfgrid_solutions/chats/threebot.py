import math
from textwrap import dedent
from jumpscale.clients.explorer.models import DiskType
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType


class ThreebotDeploy(GedisChatBot):
    steps = [
        "start",
        "select_network",
        "set_solution_name",
        "threebot_branch",
        "container_resources",
        "upload_public_key",
        "select_node",
        "select_farm",
        "select_ip_address",
        "select_expiration_time",
        "domain",
        "overview",
        "deploy",
        "success",
    ]

    title = "Threebot"

    @chatflow_step()
    def start(self):
        self.user_info = self.user_info()
        self.md_show("This wizard will help you deploy a Threebot container", md=True)
        j.sals.reservation_chatflow.validate_user(self.user_info)

    @chatflow_step(title="Network")
    def select_network(self):
        self.network = j.sals.reservation_chatflow.select_network(self, j.core.identity.me.tid)

    @chatflow_step(title="Solution name")
    def set_solution_name(self):
        self.solution_name = self.string_ask("Please enter a name for your threebot container", required=True)

    @chatflow_step(title="Threebot version")
    def threebot_branch(self):
        self.branch = self.string_ask("Please type branch name", required=True, default="development")

    @chatflow_step(title="Resources")
    def container_resources(self):
        form = self.new_form()
        cpu = form.int_ask("Please add how many CPU cores are needed", default=2, required=True)
        memory = form.int_ask("Please add the amount of memory in MB", default=2048, required=True)
        rootfs_size = form.int_ask("Choose the amount of storage for your root filesystem in MiB", default=2048)
        
        form.ask()

        self.container_cpu = cpu.value
        self.container_memory = memory.value
        self.container_rootfs_size = rootfs_size.value
        self.container_fs_type = DiskType.SSD.name

    @chatflow_step(title="Access key")
    def upload_public_key(self):
        self.public_key = self.upload_file(
            "Please upload your public ssh key, this will allow you to access your threebot container using ssh", required=True
        ).strip()

    @chatflow_step(title="Select Node")
    def select_node(self):
        self.query = dict(
            currency=self.network.currency,
            cru=self.container_cpu,
            mru=math.ceil(self.container_memory / 1024),
            sru=math.ceil(self.container_rootfs_size / 1024),
        )
        
        self.nodeid = self.string_ask(
            "Please enter the nodeid you would like to deploy on if left empty a node will be chosen for you"
        )
       
        self.reservation = j.sals.zos.reservation_create()
        while self.nodeid:
            try:
                self.node_selected = j.sals.reservation_chatflow.validate_node(
                    self.nodeid, self.query, self.network.currency
                )
                break

            except (j.exceptions.Value, j.exceptions.NotFound) as e:
                message = "<br> Please enter a different nodeid to deploy on or leave it empty"
                self.nodeid = self.string_ask(str(e) + message, html=True, retry=True)
        

    @chatflow_step(title="Select farm")
    def select_farm(self):
        if not self.nodeid:
            farms = j.sals.reservation_chatflow.get_farm_names(1, self, ** self.query)
            self.node_selected = j.sals.reservation_chatflow.get_nodes(1, farm_names=farms, ** self.query)[0]

    @chatflow_step(title="Select IP")
    def select_ip_address(self):
        self.network_copy = self.network.copy(j.core.identity.me.tid)
        self.network_copy.add_node(self.node_selected)
        self.ip_address = self.network_copy.ask_ip_from_node(
            self.node_selected, "Please choose IP Address for your solution"
        )

    @chatflow_step(title="Expiration time")
    def select_expiration_time(self):
        self.expiration = self.datetime_picker(
            "Please enter solution expiration time.",
            required=True,
            min_time=[3600, "Date/time should be at least 1 hour from now"],
            default=j.data.time.get().timestamp + 3900,
        )

    @chatflow_step(title="Domain")
    def domain(self):
        pass


    @chatflow_step(title="Confirmation")
    def overview(self):
        info = {
            "Solution name": self.solution_name,
            "Threebot version": self.branch,
            "Number of cpu cores": self.container_cpu,
            "Memory": self.container_memory,
            "Root filesystem type": DiskType.SSD.name,
            "Root filesystem size": self.container_rootfs_size,
            "IP address": self.ip_address,
            "Expiration time": j.data.time.get(self.expiration).humanize()
        }
        self.md_show_confirm(info)

    @chatflow_step(title="Payment", disable_previous=True)
    def deploy(self):
        self.network = self.network_copy
        self.network.update(j.core.identity.me.tid, currency=self.query["currency"], bot=self)
        
        flist = "https://hub.grid.tf/ahmedelsayed.3bot/threefoldtech-js-sdk-dev.flist"
        entry_point = "/bin/bash /sandbox/code/github/threefoldtech/js-sdk/jumpscale/packages/tfgrid_solutions/scripts/threebot/entrypoint.sh"
        environment_vars = {
            "SDK_VERSION": self.branch,
            "THREEBOT_NAME": self.user_info.get("username"),
            "SSHKEY": self.public_key
        }

        j.sals.zos.container.create(
            reservation=self.reservation,
            node_id=self.node_selected.node_id,
            network_name=self.network.name,
            ip_address=self.ip_address,
            flist=flist,
            disk_type=DiskType.SSD.value,
            env=environment_vars,
            interactive=False,
            entrypoint=entry_point,
            cpu=self.container_cpu,
            memory=self.container_memory,
            disk_size=self.container_rootfs_size,
        )

        metadata = {
            "Solution name": self.solution_name, "Version": self.branch, "chatflow": "threebot"
        }

        res = j.sals.reservation_chatflow.get_solution_metadata(
            self.solution_name, SolutionType.Threebot, metadata
        )
        reservation = j.sals.reservation_chatflow.add_reservation_metadata(self.reservation, res)

        self.reservation_id = j.sals.reservation_chatflow.register_and_pay_reservation(
            reservation, self.expiration, customer_tid=j.core.identity.me.tid, currency=self.query["currency"], bot=self
        )

        j.sals.reservation_chatflow.save_reservation(
            self.reservation_id, self.solution_name, SolutionType.Threebot, metadata
        )


    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def success(self):
        message = f"""
        Your Threebot has been deployed successfully.
        Reservation ID  : {self.reservation_id}
        IP Address      : {self.ip_address}
        """        
        self.md_show(dedent(message), md=True)


chat = ThreebotDeploy
