from jumpscale.clients.explorer.models import DiskType
from jumpscale.god import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.reservation_chatflow.reservation_chatflow import Network
from jumpscale.clients.explorer.models import NextAction
import math, time


class SDKOnlineDeployer:
    def __init__(self, tname, bot, network_name):
        self.tname = tname
        self.bot = bot
        self.network_name = network_name
        self.network = None
        self.sdk_containers = []
        self.get_user_reservations()

    def get_user_reservations(self):
        reservations = j.sals.reservation_chatflow.get_solutions_explorer()
        for res in reservations:
            if res["form_info"].get("tname") != self.tname:
                continue
            if res["solution_type"] == "network" and res["name"] == self.network_name:
                self.network = res
            elif res["solution_type"] == "sdk_online":
                self.sdk_containers.append(res)

    def deploy_network(self, expiration, currency):
        ips = ["IPv6", "IPv4"]
        ipversion = self.bot.single_choice(
            "How would you like to connect to your network? IPv4 or IPv6? If unsure, choose IPv4", ips, required=True
        )
        farms = j.sals.reservation_chatflow.get_farm_names(1, self.bot)
        access_node = j.sals.reservation_chatflow.get_nodes(
            1, farm_names=farms, currency=currency, ip_version=ipversion
        )[0]

        ip_range = j.sals.reservation_chatflow.get_ip_range(self.bot)
        reservation = j.sals.zos.reservation_create()
        res = j.sals.reservation_chatflow.get_solution_metadata(
            self.network_name, SolutionType.Network, {"tname": self.tname, "chatflow": "network"}
        )
        reservation = j.sals.reservation_chatflow.add_reservation_metadata(reservation, res)

        while True:
            config = j.sals.reservation_chatflow.create_network(
                self.network_name,
                reservation,
                ip_range,
                j.core.identity.me.tid,
                ipversion,
                access_node,
                expiration=expiration,
                currency=currency,
                bot=self.bot,
            )
            try:
                j.sals.reservation_chatflow.register_and_pay_reservation(config["reservation_create"], bot=self.bot)
                break
            except StopChatFlow as e:
                if "wireguard listen port already in use" in e.msg:
                    j.sals.zos.reservation_cancel(config["rid"])
                    time.sleep(5)
                    continue
                raise

        message = """
### Use the following template to configure your wireguard connection. This will give you access to your network.
#### Make sure you have <a target="_blank" href="https://www.wireguard.com/install/">wireguard</a> installed
Click next
to download your configuration
        """

        self.bot.md_show(message, md=True, html=True)

        filename = "wg-{}.conf".format(config["rid"])
        self.bot.download_file(msg=f'<pre>{config["wg"]}</pre>', data=config["wg"], filename=filename, html=True)

        message = f"""
### In order to have the network active and accessible from your local/container machine. To do this, execute this command:
#### ```wg-quick up /etc/wireguard/{filename}```
# Click next
        """

        self.bot.md_show(message, md=True)

    def list_networks(self):
        reservations = j.sals.zos.reservation_list(tid=j.core.identity.me.tid, next_action="DEPLOY")
        networks = dict()
        names = set()
        for reservation in sorted(reservations, key=lambda r: r.id, reverse=True):
            if reservation.next_action != NextAction.DEPLOY:
                continue
            rnetworks = reservation.data_reservation.networks
            expiration = reservation.data_reservation.expiration_reservation
            currency = j.sals.reservation_chatflow.get_currency(reservation)
            for network in rnetworks:
                if network.name in names:
                    continue
                names.add(network.name)
                networks[network.name] = (network, expiration, currency, reservation.id)

        return networks


class SDKDeploy(GedisChatBot):
    HUB_URL = "https://playground.hub.grid.tf/guest"
    VERSIONS = ["latest"]  # name should be js-sdk-{version}.flist

    steps = [
        "sdk_identity",
        "deployed_sdks",
        "container_name",
        "expiration_time",
        "sdk_network",
        "sdk_resources",
        "public_key_get",
        "container_node_id",
        "container_farm",
        "container_ip",
        "overview",
        "version",
        "container_pay",
        "ssh_access",
    ]

    @chatflow_step(title="Identity")
    def sdk_identity(self):
        # get from login
        user_info = self.user_info()
        j.sals.reservation_chatflow.validate_user(user_info)
        form = self.new_form()
        tname = form.string_ask("What is your threebot name?", required=True)
        email = form.string_ask("What is your configured email?", required=True)
        words = form.string_ask("What are you identity words?", required=True)
        form.ask()
        self.tname = tname.value
        self.email = email.value
        self.words = words.value
        self.user_form_data = {"solution_type": "sdk_online", "tname": self.tname, "chatflow": "sdk_online"}

    @chatflow_step(title="Your Deployed SDKs")
    def deployed_sdks(self):
        # TODO: better formatting
        self.network_name = f"sdk_online_net_{self.tname}"
        self.deployer = SDKOnlineDeployer(self.tname, self, self.network_name)
        self.deployer.get_user_reservations()
        if self.deployer.sdk_containers:
            self.md_show(
                f"You already have deployed sdks\n{j.data.serializers.json.dumps(self.deployer.sdk_containers)}\n click next to deploy another"
            )

    @chatflow_step(title="Solution name")
    def container_name(self):
        self.user_form_data["Solution name"] = self.string_ask(
            "Please enter a name for your sdk container", required=True, field="name"
        )

    @chatflow_step(title="Expiration time")
    def expiration_time(self):
        self.expiration = self.datetime_picker(
            "Please enter solution expiration time.",
            required=True,
            min_time=[3600, "Date/time should be at least 1 hour from now"],
            default=j.data.time.get().timestamp + 3900,
        )
        self.user_form_data["Solution expiration"] = j.data.time.get(self.expiration).humanize()

    @chatflow_step(title="Container Network")
    def sdk_network(self):
        if not self.deployer.network:
            currency = self.single_choice(
                "Please choose a currency that will be used for the payment",
                ["FreeTFT", "TFTA", "TFT"],
                default="TFT",
                required=True,
            )
            self.deployer.deploy_network(self.expiration, currency)
        reservations = j.sals.zos.reservation_list(tid=j.core.identity.me.tid, next_action="DEPLOY")
        networks = self.deployer.list_networks()
        network, expiration, self.currency, resv_id = networks[self.network_name]
        self.network = Network(network, expiration, self, reservations, self.currency, resv_id)
        self.user_form_data["Currency"] = self.currency

    @chatflow_step(title="Container Resources")
    def sdk_resources(self):
        form = self.new_form()
        cpu = form.int_ask("Please add how many CPU cores are needed", default=1, required=True)
        memory = form.int_ask("Please add the amount of memory in MB", default=1024, required=True)

        self.rootfs_size = form.int_ask("Choose the amount of storage for your root filesystem in MiB", default=256)
        form.ask()
        self.user_form_data["CPU"] = cpu.value
        self.user_form_data["Memory"] = memory.value
        self.user_form_data["Root filesystem Type"] = DiskType.SSD.name
        self.user_form_data["Root filesystem Size"] = self.rootfs_size.value

    @chatflow_step(title="Access keys")
    def public_key_get(self):
        # TODO: will access over ssh?
        self.user_form_data["Public key"] = self.upload_file(
            """Please add your public ssh key, this will allow you to access the deployed container using ssh.
                    Just upload the file with the key""",
            required=True,
        ).split("\n")[0]

    @chatflow_step(title="Container node id")
    def container_node_id(self):
        self.query = dict()
        self.var_dict = {"pub_key": self.user_form_data["Public key"]}
        self.query["mru"] = math.ceil(self.user_form_data["Memory"] / 1024)
        self.query["cru"] = self.user_form_data["CPU"]
        storage_units = math.ceil(self.rootfs_size.value / 1024)
        self.query["sru"] = storage_units
        # create new reservation
        self.reservation = j.sals.zos.reservation_create()
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
        self.query["currency"] = self.network.currency

    @chatflow_step(title="Container farm")
    def container_farm(self):
        if not self.nodeid:
            farms = j.sals.reservation_chatflow.get_farm_names(1, self, **self.query)
            self.node_selected = j.sals.reservation_chatflow.get_nodes(1, farm_names=farms, **self.query)[0]

    @chatflow_step(title="Container IP")
    def container_ip(self):
        self.network_copy = self.network.copy(j.core.identity.me.tid)
        self.network_copy.add_node(self.node_selected)
        self.ip_address = self.network_copy.ask_ip_from_node(
            self.node_selected, "Please choose IP Address for your solution"
        )
        self.user_form_data["IP Address"] = self.ip_address

    @chatflow_step(title="Confirmation")
    def overview(self):
        self.md_show_confirm(self.user_form_data)

    @chatflow_step(title="SDK Version")
    def version(self):
        self.user_form_data["Version"] = self.single_choice("Please choose the SDK version", self.VERSIONS)

    @chatflow_step(title="Payment", disable_previous=True)
    def container_pay(self):
        self.network = self.network_copy
        self.network.update(j.core.identity.me.tid, currency=self.query["currency"], bot=self)
        # container_flist = f"{self.HUB_URL}/js-sdk-{self.user_form_data['Version']}.flist"  # TODO: set js-sdk flsit
        container_flist = f"{self.HUB_URL}/js-ng-{self.user_form_data['Version']}.flist"
        storage_url = "zdb://hub.grid.tf:9900"

        # create container
        cont = j.sals.zos.container.create(
            reservation=self.reservation,
            node_id=self.node_selected.node_id,
            network_name=self.network.name,
            ip_address=self.ip_address,
            flist=container_flist,
            storage_url=storage_url,
            disk_type=DiskType.SSD.value,
            disk_size=self.rootfs_size.value,
            env=self.var_dict,
            interactive=True,  # TODO: change to False
            # entrypoint=entry_point, # TODO: set entry point
            cpu=self.user_form_data["CPU"],
            memory=self.user_form_data["Memory"],
        )

        metadata = dict()
        metadata["chatflow"] = self.user_form_data["chatflow"]
        metadata["Solution name"] = self.user_form_data["Solution name"]
        metadata["Version"] = self.user_form_data["Version"]
        metadata["Solution expiration"] = self.user_form_data["Solution expiration"]

        res = j.sals.reservation_chatflow.get_solution_metadata(
            self.user_form_data["Solution name"], SolutionType.SDKOnline, metadata
        )
        reservation = j.sals.reservation_chatflow.add_reservation_metadata(self.reservation, res)
        self.resv_id = j.sals.reservation_chatflow.register_and_pay_reservation(
            reservation, self.expiration, customer_tid=j.core.identity.me.tid, currency=self.query["currency"], bot=self
        )

        j.sals.reservation_chatflow.save_reservation(
            self.resv_id, self.user_form_data["Solution name"], SolutionType.Ubuntu, self.user_form_data
        )

    @chatflow_step(title="Success", disable_previous=True)
    def ssh_acess(self):
        res = f"""\
# Ubuntu has been deployed successfully: your reservation id is: {self.resv_id}
To connect ```ssh root@{self.ip_address}``` .It may take a few minutes.
"""
        self.md_show(res, md=True)


## Optional Expose

chat = SDKDeploy
