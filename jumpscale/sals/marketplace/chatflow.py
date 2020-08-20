import copy
import math
import time
import datetime
from jumpscale.clients.explorer.models import DiskType
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.packages.marketplace.bottle.models import UserEntry
from jumpscale.core.base import StoredFactory
import uuid

from .deployer import deployer


class MarketPlaceChatflow(GedisChatBot):
    SOLUTION_TYPE = None

    def get_tid(self):
        if not self._tid:
            user = j.sals.reservation_chatflow.validate_user(self.user_info())
            self._tid = user.id
        return self._tid

    def _validate_user(self):
        tname = self.user_info()["username"].lower()
        user_factory = StoredFactory(UserEntry)
        explorer_url = j.core.identity.me.explorer.url

        if "testnet" in explorer_url:
            explorer_name = "testnet"
        elif "devnet" in explorer_url:
            explorer_name = "devnet"
        elif "explorer.grid.tf" in explorer_url:
            explorer_name = "mainnet"
        else:
            raise StopChatFlow(f"Unsupported explorer {explorer_url}")
        instance_name = f"{explorer_name}_{tname.replace('.3bot', '')}"
        if instance_name in user_factory.list_all():
            user_entry = user_factory.get(instance_name)
            if not user_entry.has_agreed:
                raise StopChatFlow(
                    f"You must accept terms and conditions before using this solution. please head towards the main page to read our terms"
                )
        else:
            raise StopChatFlow(
                f"You must accept terms and conditions before using this solution. please head towards the main page to read our terms"
            )

    @chatflow_step(title="Welcome")
    def welcome(self):
        self.solution_uuid = uuid.uuid4().hex
        self._validate_user()
        self._tid = None
        self.user_form_data = dict()
        self.metadata = dict()
        self.query = dict()
        self.env = dict()
        self.secret_env = dict()
        self.md_show(f"### Welcome to {self.SOLUTION_TYPE.value} chatflow. click next to proceed to the deployment")

    @chatflow_step(title="Solution name")
    def solution_name(self):
        self.name = self.string_ask("Please enter a name for your solution", required=True)
        self.user_form_data["Solution name"] = self.name

    @chatflow_step(title="Expiration time")
    def expiration_time(self):
        self.expiration = self.datetime_picker(
            "Please enter solution expiration time.",
            required=True,
            min_time=[3600, "Date/time should be at least 1 hour from now"],
            default=j.data.time.get().timestamp + 3900,
        )
        # DONT REMOVE THIS until capacity pool migration is done on mainnet
        while self.expiration > 1599091200:
            self.md_show(
                "the maximum expiration in marketplace is currently 09/03/2020 @ 12:00am (UTC). please click next to try again"
            )
            self.expiration = self.datetime_picker(
                "Please enter solution expiration time.",
                required=True,
                min_time=[3600, "Date/time should be at least 1 hour from now"],
                default=j.data.time.get().timestamp + 3900,
            )
        self.user_form_data["Solution expiration"] = j.data.time.get(self.expiration).humanize()
        self.metadata["Solution expiration"] = self.user_form_data["Solution expiration"]

    @chatflow_step(title="Currency")
    def choose_currency(self):
        self.currency = self.single_choice(
            "Please choose a currency that will be used for the payment",
            ["FreeTFT", "TFTA", "TFT"],
            default="TFT",
            required=True,
        )
        self.user_form_data["currency"] = self.currency

    @chatflow_step(title="Container Resources")
    def container_resources(self):
        form = self.new_form()
        cpu = form.int_ask("Please add how many CPU cores are needed", default=1, required=True)
        memory = form.int_ask("Please add the amount of memory in MB", default=1024, required=True)

        self.rootfs_size = form.int_ask("Choose the amount of storage for your root filesystem in MiB", default=256)
        form.ask()
        self.user_form_data["CPU"] = cpu.value
        self.user_form_data["Memory"] = memory.value
        self.user_form_data["Root filesystem Type"] = DiskType.SSD.name
        self.user_form_data["Root filesystem Size"] = self.rootfs_size.value
        self.query["mru"] = math.ceil(self.user_form_data["Memory"] / 1024)
        self.query["cru"] = self.user_form_data["CPU"]
        storage_units = math.ceil(self.rootfs_size.value / 1024)
        self.query["sru"] = storage_units
        self.query["currency"] = self.currency

    @chatflow_step(title="Access keys")
    def public_key_get(self):
        self.user_form_data["Public key"] = self.upload_file(
            """Please add your public ssh key, this will allow you to access the deployed container using ssh.
                    Just upload the file with the key""",
            required=True,
        ).split("\n")[0]
        self.env["pub_key"] = self.user_form_data["Public key"]
        self.public_key = self.user_form_data["Public key"]

    @chatflow_step(title="Container node id")
    def container_node_id(self):
        # create new reservation
        self.nodeid = self.string_ask(
            "Please enter the nodeid you would like to deploy on if left empty a node will be chosen for you"
        )
        while self.nodeid:
            try:
                self.node_selected = j.sals.reservation_chatflow.validate_node(
                    self.nodeid, self.query, self.network.currency
                )
                break
            except (j.exceptions.Value, j.exceptions.NotFound) as e:
                message = "<br> Please enter a different nodeid to deploy on or leave it empty"
                self.nodeid = self.string_ask(str(e) + message, html=True, retry=True)
        self.query["currency"] = self.currency

    @chatflow_step(title="Container farm")
    def container_farm(self):
        if not hasattr(self, "nodeid"):
            self.nodeid = None
        if not self.nodeid:
            if not self.query:
                self.query["mru"] = math.ceil(self.user_form_data["Memory"] / 1024)
                self.query["cru"] = self.user_form_data["CPU"]

                storage_units = math.ceil(self.rootfs_size.value / 1024)
                self.query["sru"] = storage_units
            farms = j.sals.reservation_chatflow.get_farm_names(1, self, **self.query)
            self.node_selected = j.sals.reservation_chatflow.get_nodes(1, farm_names=farms, **self.query)[0]

    @chatflow_step(title="Container IP")
    def container_ip(self):
        self.md_show_update("Finding Available IPs.....")
        self.network_copy = self.network.copy()
        self.network_copy.add_node(self.node_selected)
        self.ip_address = self.network_copy.ask_ip_from_node(
            self.node_selected, "Please choose IP Address for your solution"
        )
        self.user_form_data["IP Address"] = self.ip_address

    @chatflow_step(title="Confirmation")
    def overview(self):
        self.md_show_confirm(self.user_form_data)

    @chatflow_step(title="Container logs")
    def container_logs(self):
        self.container_logs_option = self.single_choice(
            "Do you want to push the container logs (stdout and stderr) onto an external redis channel",
            ["YES", "NO"],
            default="NO",
        )
        if self.container_logs_option == "YES":
            form = self.new_form()
            self.channel_type = form.string_ask("Please add the channel type", default="redis", required=True)
            self.channel_host = form.string_ask(
                "Please add the IP address where the logs will be output to", required=True
            )
            self.channel_port = form.int_ask(
                "Please add the port available where the logs will be output to", required=True
            )
            self.channel_name = form.string_ask(
                "Please add the channel name to be used. The channels will be in the form NAME-stdout and NAME-stderr",
                default=self.user_form_data["Solution name"],
                required=True,
            )
            form.ask()
            self.user_form_data["Logs Channel type"] = self.channel_type.value
            self.user_form_data["Logs Channel host"] = self.channel_host.value
            self.user_form_data["Logs Channel port"] = self.channel_port.value
            self.user_form_data["Logs Channel name"] = self.channel_name.value

    @chatflow_step(title="Choose Network")
    def choose_network(self):
        self.md_show_update("Listing User Networks....")
        networks_data = deployer.list_solutions(self.user_info()["username"], SolutionType.Network, reload=True)
        if not networks_data:
            raise StopChatFlow("You don't have any available networks yet. please create a newtork first")
        network_names = []
        networks_dict = {}
        for net in networks_data:
            message = f"{net['name']} Currency: {net['reservation_obj'].data_reservation.currencies[0]}"
            network_names.append(message)
            networks_dict[message] = net
        network_name = self.single_choice(
            "Please choose the network you want to connect your container to\n<br>\n<br>\n`The currency of the network will be used for the solution`",
            network_names,
            required=True,
            md=True,
        )
        self.user_form_data["Network Name"] = network_name
        network_reservation = networks_dict[network_name]
        self.network = deployer.get_network_object(network_reservation["reservation_obj"], self)
        self.currency = self.network.currency

    @chatflow_step(title="Payment", disable_previous=True)
    def container_pay(self):
        self.reservation = j.sals.zos.reservation_create()
        if not hasattr(self, "container_volume_attach"):
            self.container_volume_attach = False
        if not hasattr(self, "interactive"):
            self.interactive = False
        if not hasattr(self, "entry_point"):
            self.entry_point = None
        self.md_show_update("Preparing Network on Node.....")
        self.network = self.network_copy
        self.network.update(self.user_info()["username"], currency=self.currency, bot=self)
        storage_url = "zdb://hub.grid.tf:9900"

        # create container
        cont = j.sals.zos.container.create(
            reservation=self.reservation,
            node_id=self.node_selected.node_id,
            network_name=self.network.name,
            ip_address=self.ip_address,
            flist=self.flist_url,
            storage_url=storage_url,
            disk_type=DiskType.SSD.value,
            disk_size=self.rootfs_size.value,
            env=self.env,
            secret_env=self.secret_env,
            interactive=self.interactive,
            entrypoint=self.entry_point,
            cpu=self.user_form_data["CPU"],
            memory=self.user_form_data["Memory"],
        )
        if self.container_logs_option == "YES":
            j.sals.zos.container.add_logs(
                cont,
                channel_type=self.user_form_data["Logs Channel type"],
                channel_host=self.user_form_data["Logs Channel host"],
                channel_port=self.user_form_data["Logs Channel port"],
                channel_name=self.user_form_data["Logs Channel name"],
            )
        if self.container_volume_attach:
            self.volume = j.sals.zos.volume.create(
                self.reservation,
                self.node_selected.node_id,
                size=self.user_form_data["Volume Size"],
                type=self.vol_disk_type.value,
            )
            j.sals.zos.volume.attach(
                container=cont, volume=self.volume, mount_point=self.user_form_data["Volume mount point"]
            )

        res = deployer.get_solution_metadata(
            self.user_form_data["Solution name"],
            self.SOLUTION_TYPE,
            self.user_info()["username"],
            self.metadata,
            self.solution_uuid,
        )
        reservation = j.sals.reservation_chatflow.add_reservation_metadata(self.reservation, res)
        self.resv_id = deployer.register_and_pay_reservation(
            reservation, self.expiration, customer_tid=j.core.identity.me.tid, currency=self.currency, bot=self
        )

    @chatflow_step(title="Attach Volume")
    def container_volume(self):
        volume_attach = self.drop_down_choice(
            "Would you like to attach an extra volume to the container", ["YES", "NO"], required=True, default="NO"
        )
        self.container_volume_attach = volume_attach == "YES" or False

    @chatflow_step(title="Volume details")
    def container_volume_details(self):
        if self.container_volume_attach:
            form = self.new_form()
            vol_disk_size = form.int_ask("Please specify the volume size", required=True, default=10)
            vol_mount_point = form.string_ask("Please enter the mount point", required=True, default="/data")
            form.ask()
            self.vol_disk_size = vol_disk_size
            self.vol_disk_type = DiskType.SSD
            self.user_form_data["Volume Disk type"] = DiskType.SSD.name
            self.user_form_data["Volume Size"] = vol_disk_size.value
            self.user_form_data["Volume mount point"] = vol_mount_point.value

    @chatflow_step(title="Environment variables")
    def container_env(self):
        self.user_form_data["Env variables"] = self.multi_values_ask("Set Environment Variables")
        self.env.update(self.user_form_data["Env variables"])

    @chatflow_step(title="Container ineractive & EntryPoint")
    def container_interactive(self):
        self.user_form_data["Interactive"] = self.single_choice(
            "Would you like access to your container through the web browser (coreX)?", ["YES", "NO"], required=True
        )
        if self.user_form_data["Interactive"] == "NO":
            self.interactive = False
            self.user_form_data["Entry point"] = self.string_ask("Please add your entrypoint for your flist") or ""
        else:
            self.interactive = True
            self.user_form_data["Port"] = "7681"
            self.user_form_data["Entry point"] = ""

        self.entry_point = self.user_form_data["Entry point"]
