import time

from jumpscale.loader import j
from jumpscale.clients.explorer.models import DiskType
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.marketplace import deployer, MarketPlaceChatflow
import math


class GiteaDeploy(MarketPlaceChatflow):
    SOLUTION_TYPE = SolutionType.Gitea

    steps = [
        "welcome",
        "solution_name",
        "choose_network",
        "public_key_get",
        "expiration_time",
        "gitea_credentials",
        "container_logs",
        "container_resources",
        "container_node_id",
        "container_farm",
        "container_ip",
        "overview",
        "set_env",
        "set_metadata",
        "container_pay",
        "container_access",
    ]
    title = "Gitea"

    flist_url = "https://hub.grid.tf/tf-official-apps/gitea-latest.flist"

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

    @chatflow_step()
    def set_env(self):
        self.env.update(
            {
                "pub_key": self.user_form_data["Public key"],
                "POSTGRES_DB": self.user_form_data["Database Name"],
                "DB_TYPE": "postgres",
                "DB_HOST": f"{self.ip_address}:5432",
                "POSTGRES_USER": self.user_form_data["Database User"],
                "APP_NAME": self.user_form_data["Repository"],
                "ROOT_URL": f"http://{self.ip_address}:3000",
            }
        )
        database_password_encrypted = j.sals.zos.container.encrypt_secret(
            self.node_selected.node_id, self.user_form_data["Database Password"]
        )
        self.secret_env.update({"POSTGRES_PASSWORD": database_password_encrypted})

    @chatflow_step()
    def set_metadata(self):
        self.metadata["Solution expiration"] = self.user_form_data["Solution expiration"]
        self.metadata["Database name"] = self.user_form_data["Database Name"]
        self.metadata["Database user"] = self.user_form_data["Database User"]
        self.metadata["Database password"] = self.user_form_data["Database Password"]
        self.metadata["Repository"] = self.user_form_data["Repository"]

    @chatflow_step(title="Success", disable_previous=True)
    def container_access(self):
        res = f"""\
# gitea has been deployed successfully: your reservation id is: {self.resv_id}
To connect ```ssh git@{self.ip_address}``` .It may take a few minutes.
open gitea from browser at ```{self.ip_address}:3000```
            """
        self.md_show(res, md=True)


chat = GiteaDeploy
