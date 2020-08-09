import uuid

from nacl.encoding import Base64Encoder
from nacl.public import PrivateKey

from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow import deployer, solutions


class TaigaDeploy(GedisChatBot):
    """
    taiga container deploy
    """

    steps = [
        "taiga_start",
        "taiga_name",
        "select_pool",
        "taiga_network",
        "public_key_get",
        "taiga_credentials",
        "container_logs",
        "container_node_id",
        "container_ip",
        "overview",
        "reservation",
        "container_acess",
    ]
    title = "Taiga"

    @chatflow_step()
    def taiga_start(self):
        self.solution_id = uuid.uuid4().hex
        self.user_form_data = dict()
        self.HUB_URL = "https://hub.grid.tf/bishoy.3bot/threefolddev-taiga_all_in_one-latest.flist"
        self.md_show("# This wizard wil help you deploy an taiga solution", md=True)
        self.query = {"mru": 1, "cru": 2, "sru": 6}
        self.solution_metadata = {}

    @chatflow_step(title="Solution name")
    def taiga_name(self):
        valid = False
        while not valid:
            self.solution_name = deployer.ask_name(self)
            taiga_solutions = solutions.list_taiga_solutions(sync=False)
            valid = True
            for sol in taiga_solutions:
                if sol["Name"] == self.solution_name:
                    valid = False
                    self.md_show("The specified solution name already exists. please choose another.")
                    break
                valid = True

    @chatflow_step(title="Pool")
    def select_pool(self):
        cu, su = deployer.calculate_capacity_units(**self.query)
        self.pool_id = deployer.select_pool(self, cu=cu, su=su, **self.query)

    @chatflow_step(title="Network")
    def taiga_network(self):
        self.network_view = deployer.select_network(self)

    @chatflow_step(title="Access keys")
    def public_key_get(self):
        self.public_key = self.upload_file(
            """Please add your public ssh key, this will allow you to access the deployed container using ssh.
                    Just upload the file with the key""",
            required=True,
        ).split("\n")[0]

    @chatflow_step(title="Taiga Setup")
    def taiga_credentials(self):
        form = self.new_form()
        EMAIL_HOST_USER = form.string_ask("Please add the host email name for your solution.", required=True)
        EMAIL_HOST = form.string_ask(
            "Please add the smtp host example: `smtp.gmail.com`", default="smtp.gmail.com", required=True, md=True
        )
        EMAIL_HOST_PASSWORD = form.secret_ask("Please add the host email password", required=True)

        SECRET_KEY = form.secret_ask("Please add the secret for your solution", required=True)
        form.ask()
        self.EMAIL_HOST_USER = EMAIL_HOST_USER.value
        self.EMAIL_HOST = EMAIL_HOST.value
        self.EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD.value
        self.SECRET_KEY = SECRET_KEY.value

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
            self.network_view.name,
            self.selected_node,
            self.pool_id,
            self.network_view_copy,
            bot=self,
            owner=self.solution_metadata.get("owner"),
        )
        if result:
            for wid in result["ids"]:
                success = deployer.wait_workload(wid, self)
                if not success:
                    raise StopChatFlow(f"Failed to add node {self.selected_node.node_id} to network {wid}")
            self.network_view_copy = self.network_view_copy.copy()
        free_ips = self.network_view_copy.get_node_free_ips(self.selected_node)
        self.ip_address = self.drop_down_choice(
            "Please choose IP Address for your solution", free_ips, default=free_ips[0], required=True
        )

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
        private_key = PrivateKey.generate().encode(Base64Encoder).decode()
        var_dict = {
            "EMAIL_HOST_USER": self.EMAIL_HOST_USER,
            "EMAIL_HOST": self.EMAIL_HOST,
            "TAIGA_HOSTNAME": self.ip_address,
            "HTTP_PORT": "80",
            "FLASK_SECRET_KEY": "flask",
            "THREEBOT_URL": "https://login.threefold.me",
            "OPEN_KYC_URL": "https://openkyc.live/verification/verify-sei",
        }
        metadata = {
            "name": self.solution_name,
            "form_info": {"Solution name": self.solution_name, "chatflow": "taiga",},
        }
        self.solution_metadata.update(metadata)

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
            entrypoint="/.start_taiga.sh",
            log_config=self.log_config,
            public_ipv6=True,
            disk_size=2 * 1024,
            secret_env={
                "EMAIL_HOST_PASSWORD": "codescalers_2010",
                "PRIVATE_KEY": private_key,
                "SECRET_KEY": self.SECRET_KEY,
            },
            **self.solution_metadata,
            solution_uuid=self.solution_id,
        )
        success = deployer.wait_workload(self.resv_id, self)
        if not success:
            solutions.cancel_solution([self.resv_id])
            raise StopChatFlow(f"Failed to deploy workload {self.resv_id}")

    @chatflow_step(title="Success", disable_previous=True)
    def container_acess(self):
        res = f"""\
# Taiga has been deployed successfully:
\n<br />\n
your reservation id is: {self.resv_id}
\n<br />\n
To connect ```ssh {self.ip_address}``` .It may take a few minutes.
\n<br />\n
open Taiga from browser at ```https://{self.ip_address}```
                """
        self.md_show(res, md=True)


chat = TaigaDeploy
