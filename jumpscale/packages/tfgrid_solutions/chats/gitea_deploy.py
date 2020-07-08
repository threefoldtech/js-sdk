import math

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType


class GiteaDeploy(GedisChatBot):
    """
    gitea container deploy
    """

    steps = [
        "gitea_start",
        "gitea_network",
        "gitea_solution_name",
        "public_key_get",
        "expiration_time",
        "gitea_credentials",
        "container_logs",
        "container_node_id",
        "container_farm",
        "container_ip",
        "overview",
        "container_pay",
        "container_acess",
    ]
    title = "Gitea"

    @chatflow_step()
    def gitea_start(self):
        self.user_form_data = dict()
        self.HUB_URL = "https://hub.grid.tf/tf-official-apps/gitea-latest.flist"
        user_info = self.user_info()
        self.user_form_data["chatflow"] = "gitea"
        j.sals.reservation_chatflow.validate_user(user_info)
        self.md_show("# This wizard wil help you deploy an gitea container", md=True)

    @chatflow_step(title="Network")
    def gitea_network(self):
        self.network = j.sals.reservation_chatflow.select_network(self, j.core.identity.me.tid)
        self.currency = self.network.currency

    @chatflow_step(title="Solution name")
    def gitea_solution_name(self):
        self.user_form_data["Solution name"] = self.string_ask(
            "Please enter a name for your gitea solution", required=True, field="name"
        )

    @chatflow_step(title="Access keys")
    def public_key_get(self):
        self.user_form_data["Public key"] = self.upload_file(
            """Please add your public ssh key, this will allow you to access the deployed container using ssh.
                    Just upload the file with the key""",
            required=True,
        ).split("\n")[0]

    @chatflow_step(title="Expiration time")
    def expiration_time(self):
        self.expiration = self.datetime_picker(
            "Please enter solution expiration time.",
            required=True,
            min_time=[3600, "Date/time should be at least 1 hour from now"],
            default=j.data.time.get().timestamp + 3900,
        )
        self.user_form_data["Solution expiration"] = j.data.time.get(self.expiration).humanize()

    @chatflow_step(title="Database credentials & Repository name")
    def gitea_credentials(self):
        form = self.new_form()
        database_name = form.string_ask("Please add the database name of your gitea", default="postgres", required=True)
        database_user = form.string_ask(
            "Please add the username for your gitea database. Make sure not to lose it",
            default="postgres",
            required=True,
        )
        database_password = form.string_ask(
            "Please add the secret for your gitea database. Make sure not to lose it", default="postgres", required=True
        )
        repository_name = form.string_ask(
            "Please add the name of repository in your gitea", default="myrepo", required=True
        )
        form.ask()
        self.user_form_data["Database Name"] = database_name.value
        self.user_form_data["Database User"] = database_user.value
        self.user_form_data["Database Password"] = database_password.value
        self.user_form_data["Repository"] = repository_name.value

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

    @chatflow_step(title="Container node id")
    def container_node_id(self):
        self.query = {"mru": math.ceil(1024 / 1024), "cru": 2, "sru": 6}
        # create new reservation
        self.reservation = j.sals.zos.reservation_create()
        self.nodeid = self.string_ask(
            "Please enter the node id you would like to deploy on if left empty a node will be chosen for you"
        )
        while self.nodeid:
            try:
                self.node_selected = j.sals.reservation_chatflow.validate_node(self.nodeid, self.query, self.currency)
                break
            except (j.exceptions.Value, j.exceptions.NotFound) as e:
                message = "<br> Please enter a different node id to deploy on or leave it empty"
                self.nodeid = self.string_ask(str(e) + message, html=True, retry=True)
        self.query["currency"] = self.currency

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

    @chatflow_step(title="Payment", disable_previous=True)
    def container_pay(self):
        self.network = self.network_copy
        var_dict = {
            "pub_key": self.user_form_data["Public key"],
            "POSTGRES_DB": self.user_form_data["Database Name"],
            "DB_TYPE": "postgres",
            "DB_HOST": f"{self.ip_address}:5432",
            "POSTGRES_USER": self.user_form_data["Database User"],
            "APP_NAME": self.user_form_data["Repository"],
            "ROOT_URL": f"http://{self.ip_address}:3000",
        }
        database_password_encrypted = j.sals.zos.container.encrypt_secret(
            self.node_selected.node_id, self.user_form_data["Database Password"]
        )
        secret_env = {"POSTGRES_PASSWORD": database_password_encrypted}
        self.network.update(j.core.identity.me.tid, currency=self.currency, bot=self)
        storage_url = "zdb://hub.grid.tf:9900"
        entry_point = "/start_gitea.sh"

        # create container
        cont = j.sals.zos.container.create(
            reservation=self.reservation,
            node_id=self.node_selected.node_id,
            network_name=self.network.name,
            ip_address=self.ip_address,
            flist=self.HUB_URL,
            storage_url=storage_url,
            env=var_dict,
            interactive=False,
            entrypoint=entry_point,
            cpu=2,
            public_ipv6=True,
            memory=1024,
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
        metadata = dict()
        metadata["chatflow"] = self.user_form_data["chatflow"]
        metadata["Solution name"] = self.user_form_data["Solution name"]
        metadata["Solution expiration"] = self.user_form_data["Solution expiration"]
        metadata["Database name"] = self.user_form_data["Database Name"]
        metadata["Database user"] = self.user_form_data["Database User"]
        metadata["Database password"] = self.user_form_data["Database Password"]
        metadata["Repository"] = self.user_form_data["Repository"]

        res = j.sals.reservation_chatflow.get_solution_metadata(
            self.user_form_data["Solution name"], SolutionType.Gitea, metadata
        )
        self.reservation = j.sals.reservation_chatflow.add_reservation_metadata(self.reservation, res)
        self.resv_id = j.sals.reservation_chatflow.register_and_pay_reservation(
            self.reservation, self.expiration, customer_tid=j.core.identity.me.tid, currency=self.currency, bot=self
        )

        j.sals.reservation_chatflow.save_reservation(
            self.resv_id, self.user_form_data["Solution name"], SolutionType.Gitea, self.user_form_data
        )

    @chatflow_step(title="Success", disable_previous=True, final_step=True)
    def container_acess(self):
        res = f"""\
# gitea has been deployed successfully: your reservation id is: {self.resv_id}
To connect ```ssh git@{self.ip_address}``` .It may take a few minutes.
open gitea from browser at ```{self.ip_address}:3000```
            """
        self.md_show(res, md=True)


chat = GiteaDeploy
