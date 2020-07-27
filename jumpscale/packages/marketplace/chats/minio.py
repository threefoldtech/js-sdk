import time
import uuid
from jumpscale.loader import j
from jumpscale.clients.explorer.models import Category, DiskType, Mode
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.marketplace import deployer, MarketPlaceChatflow
import math


class MinioDeploy(MarketPlaceChatflow):
    SOLUTION_TYPE = SolutionType.Minio

    steps = [
        "welcome",
        "solution_name",
        "choose_network",
        "setup_type",
        "storage_type",
        "access_credentials",
        "container_resources",
        "container_logs",
        "minio_resources",
        "public_key_get",
        "expiration_time",
        "zdb_nodes",
        "minio_node",
        "ip_selection",
        "overview",
        "zdb_reservation",
        "minio_reservation",
        "success",
    ]
    title = "Minio"

    @chatflow_step(title="Setup type")
    def setup_type(self):
        self.user_form_data["Setup type"] = self.drop_down_choice(
            "Please choose the type of setup you need. Single setup is the basic setup while master/slave setup includes TLOG use to be able to reconstruct the metadata",
            ["Single Setup", "Master/Slave Setup"],
            required=True,
            default="Single Setup",
        )

    @chatflow_step(title="Storage")
    def storage_type(self):
        self.user_form_data["Disk type"] = self.drop_down_choice(
            "Please choose a the type of disk for zdb", ["SSD", "HDD"], required=True, default="SSD"
        )
        self.disk_type = getattr(DiskType, self.user_form_data["Disk type"])
        self.vol_type = getattr(DiskType, self.user_form_data["Disk type"])

    @chatflow_step(title="Access credentials")
    def access_credentials(self):
        self.user_information = self.user_info()
        name = self.user_information["username"]
        accesskey_string = f"{name.split('.')[0]}"
        secret_string = "secret12345"
        form = self.new_form()
        accesskey = form.string_ask(
            "Please add the key to be used for minio when logging in. Make sure not to lose it",
            default=accesskey_string,
            min_length=3,
        )
        secret = form.string_ask(
            "Please add the secret to be used for minio when logging in to match the previous key. Make sure not to lose it",
            default=secret_string,
            min_length=8,
        )
        form.ask()

        self.user_form_data["Access key"] = accesskey.value
        self.user_form_data["Secret"] = secret.value

    @chatflow_step(title="Container resources")
    def container_resources(self):
        form = self.new_form()
        cpu = form.int_ask("Please add how many CPU cores are needed", default=1)
        memory = form.int_ask("Please add the amount of memory in MB", default=4096, min=4096)
        form.ask()
        self.user_form_data["CPU"] = cpu.value
        self.user_form_data["Memory"] = memory.value

    @chatflow_step(title="Resources for minio")
    def minio_resources(self):
        form = self.new_form()
        data_number = form.int_ask(
            "Please add the number of locations you need. Take care of the ratio between the locations and locations allowed to fail that you will specify next",
            default=2,
        )
        parity = form.int_ask("Please add the number of locations allowed to fail", default=1)

        form.ask()
        self.user_form_data["Locations"] = int(data_number.value)
        self.user_form_data["Locations allowed to fail"] = int(parity.value)
        self.user_form_data["ZDB number"] = int(data_number.value) + int(parity.value)
        if self.user_form_data["Setup type"] == "Single Setup":
            self.number_of_minio_nodes = 1
        elif self.user_form_data["Setup type"] == "Master/Slave Setup":
            self.user_form_data["ZDB number"] += 1
            self.number_of_minio_nodes = 2

    @chatflow_step(title="Zdb (storage) nodes selection")
    def zdb_nodes(self):
        zdb_nodequery = {}
        zdb_nodequery["currency"] = self.network.currency
        if self.user_form_data["Disk type"] == "SSD":
            zdb_nodequery["sru"] = 10
        if self.user_form_data["Disk type"] == "HDD":
            zdb_nodequery["hru"] = 10

        zdb_farms = j.sals.reservation_chatflow.get_farm_names(
            self.user_form_data["ZDB number"], self, message="zdb", **zdb_nodequery
        )
        self.nodes_selected = j.sals.reservation_chatflow.get_nodes(
            number_of_nodes=self.user_form_data["ZDB number"], farm_names=zdb_farms, **zdb_nodequery
        )

    @chatflow_step(title="Minio container node selection")
    def minio_node(self):
        nodequery = {}
        nodequery["currency"] = self.network.currency
        nodequery["mru"] = math.ceil(self.user_form_data["Memory"] / 1024)
        nodequery["cru"] = self.user_form_data["CPU"]
        nodequery["sru"] = 1
        cont_farms = j.sals.reservation_chatflow.get_farm_names(1, self, message="minio container", **nodequery)
        self.minio_nodes = j.sals.reservation_chatflow.get_nodes(
            number_of_nodes=self.number_of_minio_nodes, farm_names=cont_farms, **nodequery
        )
        self.cont_node = self.minio_nodes[0]
        if self.user_form_data["Setup type"] == "Master/Slave Setup" and len(self.minio_nodes) > 1:
            self.slave_node = self.minio_nodes[1]

    @chatflow_step(title="Minio container IP")
    def ip_selection(self):
        self.network_copy = self.network.copy()
        selected_ids = []
        for node_selected in self.minio_nodes:
            self.network_copy.add_node(node_selected)
            selected_ids.append(node_selected.node_id)

        self.ip_address = self.network_copy.ask_ip_from_node(
            self.cont_node, "Please choose IP Address for your solution"
        )
        self.user_form_data["IP Address"] = self.ip_address
        if self.user_form_data["Setup type"] == "Master/Slave Setup":
            self.slave_ip_address = self.network_copy.ask_ip_from_node(
                self.slave_node, "Please choose IP Address for your backup (slave)"
            )
            self.user_form_data["Slave IP Address"] = self.slave_ip_address

    @chatflow_step(title="Reserve zdb", disable_previous=True)
    def zdb_reservation(self):
        self.md_show_update("Preparing Network on Nodes.....")
        self.network = self.network_copy
        self.network.update(self.user_info()["username"], currency=self.network.currency, bot=self)
        # create new reservation
        self.md_show_update("Preparing ZDB reservation.....")
        self.reservation = j.sals.zos.reservation_create()

        self.password = uuid.uuid4().hex

        for node in self.nodes_selected:
            j.sals.zos.zdb.create(
                reservation=self.reservation,
                node_id=node.node_id,
                size=10,
                mode=Mode.Seq,
                password=self.password,
                disk_type=self.disk_type,
                public=False,
            )
        self.volume = j.sals.zos.volume.create(self.reservation, self.cont_node.node_id, size=10, type=self.vol_type)
        if self.user_form_data["Setup type"] == "Master/Slave Setup":
            self.slave_volume = j.sals.zos.volume.create(
                self.reservation, self.slave_node.node_id, size=10, type=self.vol_type
            )

        # register the reservation for zdb db
        res = deployer.get_solution_metadata(
            self.user_form_data["Solution name"],
            SolutionType.Minio,
            self.user_info()["username"],
            {"AK": self.user_form_data["Access key"]},
            self.solution_uuid,
        )
        self.reservation = j.sals.reservation_chatflow.add_reservation_metadata(self.reservation, res)
        self.zdb_rid = deployer.register_and_pay_reservation(
            self.reservation,
            self.expiration,
            customer_tid=self.user_info()["username"],
            currency=self.network.currency,
            bot=self,
        )
        res = f"# Database has been deployed with reservation id: {self.zdb_rid}. Click next to continue with deployment of the minio container"

        self.reservation_result = j.sals.reservation_chatflow.wait_reservation(self, self.zdb_rid)
        self.md_show(res)

    @chatflow_step(title="Reserve minio container", disable_previous=True)
    def minio_reservation(self):
        self.md_show_update("Preparing Minio reservation.....")
        # read the IP address of the 0-db namespaces after they are deployed to be used in the creation of the minio container
        self.namespace_config = []
        for result in self.reservation_result:
            if result.category == Category.Zdb:
                data = j.data.serializers.json.loads(result.data_json)
                if data.get("IP"):
                    ip = data["IP"]
                else:
                    ip = data["IPs"][0]
                cfg = f"{data['Namespace']}:{self.password}@[{ip}]:{data['Port']}"
                self.namespace_config.append(cfg)
        if self.user_form_data["Setup type"] == "Master/Slave Setup":
            self.tlog_access = self.namespace_config.pop(-1)

        flist_url = "https://hub.grid.tf/tf-official-apps/minio:latest.flist"

        minio_secret_encrypted = j.sals.zos.container.encrypt_secret(
            self.cont_node.node_id, self.user_form_data["Secret"]
        )
        shards_encrypted = j.sals.zos.container.encrypt_secret(self.cont_node.node_id, ",".join(self.namespace_config))
        secret_env = {"SHARDS": shards_encrypted, "SECRET_KEY": minio_secret_encrypted}
        if self.user_form_data["Setup type"] == "Master/Slave Setup":
            tlog_access_encrypted = j.sals.zos.container.encrypt_secret(self.cont_node.node_id, self.tlog_access)
            secret_env["TLOG"] = tlog_access_encrypted

        # create container
        cont = j.sals.zos.container.create(
            reservation=self.reservation,
            node_id=self.cont_node.node_id,
            network_name=self.network.name,
            ip_address=self.ip_address,
            flist=flist_url,
            entrypoint="",
            cpu=self.user_form_data["CPU"],
            memory=self.user_form_data["Memory"],
            env={
                "DATA": str(self.user_form_data["Locations"]),
                "PARITY": str(self.user_form_data["Locations allowed to fail"]),
                "ACCESS_KEY": self.user_form_data["Access key"],
                "SSH_KEY": self.user_form_data["Public key"],
                "MINIO_PROMETHEUS_AUTH_TYPE": "public",
            },
            secret_env=secret_env,
        )
        if self.container_logs_option == "YES":
            j.sals.zos.container.add_logs(
                cont,
                channel_type=self.user_form_data["Logs Channel type"],
                channel_host=self.user_form_data["Logs Channel host"],
                channel_port=self.user_form_data["Logs Channel port"],
                channel_name=self.user_form_data["Logs Channel name"],
            )

        j.sals.zos.volume.attach_existing(
            container=cont, volume_id=f"{self.zdb_rid}-{self.volume.workload_id}", mount_point="/data"
        )

        if self.user_form_data["Setup type"] == "Master/Slave Setup":
            slave_secret_encrypted = j.sals.zos.container.encrypt_secret(
                self.slave_node.node_id, self.user_form_data["Secret"]
            )
            slave_shards_encrypted = j.sals.zos.container.encrypt_secret(
                self.slave_node.node_id, ",".join(self.namespace_config)
            )
            tlog_access_encrypted = j.sals.zos.container.encrypt_secret(self.slave_node.node_id, self.tlog_access)
            secret_env = {
                "SHARDS": slave_shards_encrypted,
                "SECRET_KEY": slave_secret_encrypted,
                "MASTER": tlog_access_encrypted,
            }
            slave_cont = j.sals.zos.container.create(
                reservation=self.reservation,
                node_id=self.slave_node.node_id,
                network_name=self.network.name,
                ip_address=self.slave_ip_address,
                flist=flist_url,
                entrypoint="",
                cpu=self.user_form_data["CPU"],
                memory=self.user_form_data["Memory"],
                env={
                    "DATA": str(self.user_form_data["Locations"]),
                    "PARITY": str(self.user_form_data["Locations allowed to fail"]),
                    "ACCESS_KEY": self.user_form_data["Access key"],
                    "SSH_KEY": self.user_form_data["Public key"],
                    "MINIO_PROMETHEUS_AUTH_TYPE": "public",
                },
                secret_env=secret_env,
            )
            j.sals.zos.volume.attach_existing(
                container=slave_cont, volume_id=f"{self.zdb_rid}-{self.slave_volume.workload_id}", mount_point="/data"
            )
            self.metadata["Slave IP"] = self.slave_ip_address

        self.metadata["AK"] = self.user_form_data["Access key"]
        self.metadata["Solution expiration"] = self.expiration
        self.metadata["Primary IP"] = self.ip_address
        res = deployer.get_solution_metadata(
            self.user_form_data["Solution name"], SolutionType.Minio, self.user_info()["username"], self.metadata
        )
        self.reservation = j.sals.reservation_chatflow.add_reservation_metadata(self.reservation, res)
        try:
            self.resv_id = deployer.register_and_pay_reservation(
                self.reservation,
                self.expiration,
                customer_tid=j.core.identity.me.tid,
                currency=self.network.currency,
                bot=self,
            )
        except Exception as e:
            deployer.cancel_reservation(self.user_info()["username"], self.zdb_rid)
            raise e

    @chatflow_step(title="Success", disable_previous=True)
    def success(self):
        res = f"""\
# Minio cluster has been deployed successfully. Your reservation id is: {self.resv_id}
Open your browser at [http://{self.ip_address}:9000](http://{self.ip_address}:9000). It may take a few minutes.
            """
        if self.user_form_data["Setup type"] == "Master/Slave Setup":
            res += f"""\
You can access the slave machine at [http://{self.slave_ip_address}:9000](http://{self.slave_ip_address}:9000)
            """
        self.md_show(res)


chat = MinioDeploy
