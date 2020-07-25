import time

from jumpscale.loader import j
from jumpscale.clients.explorer.models import DiskType
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.marketplace import deployer, MarketPlaceChatflow
import requests


class FlistDeploy(MarketPlaceChatflow):
    SOLUTION_TYPE = SolutionType.Flist

    steps = [
        "welcome",
        "solution_name",
        "choose_network",
        "flist_url",
        "container_resources",
        "container_interactive",
        "container_env",
        "container_farm",
        "container_volume",
        "container_volume_details",
        "container_logs",
        "expiration_time",
        "container_ip",
        "overview",
        "set_metadata",
        "container_pay",
        "container_access",
    ]
    title = "Generic Container"

    @chatflow_step(title="Flist url")
    def flist_url(self):
        self.user_form_data["Flist link"] = self.string_ask(
            "Please add the link to your flist to be deployed. For example: https://hub.grid.tf/usr/example.flist",
            required=True,
        )
        self.user_form_data["Flist link"] = self.user_form_data["Flist link"].strip()

        if "hub.grid.tf" not in self.user_form_data["Flist link"] or ".md" in self.user_form_data["Flist link"][-3:]:
            raise StopChatFlow(
                "This flist is not correct. Please make sure you enter a valid link to an existing flist For example: https://hub.grid.tf/usr/example.flist"
            )

        response = requests.head(self.user_form_data["Flist link"])
        response_md5 = requests.head(f"{self.user_form_data['Flist link']}.md5")
        if response.status_code != 200 or response_md5.status_code != 200:
            raise StopChatFlow("This flist doesn't exist. Please make sure you enter a valid link to an existing flist")
        self.flist_url = self.user_form_data["Flist link"]

    @chatflow_step()
    def set_metadata(self):
        self.metadata["Solution expiration"] = self.user_form_data["Solution expiration"]
        self.metadata["Flist"] = self.flist_url

    @chatflow_step(title="Success", disable_previous=True)
    def container_access(self):
        if self.interactive:
            res = f"""\
# Container has been deployed successfully: your reservation id is: {self.resv_id}
Open your browser at [http://{self.ip_address}:7681](http://{self.ip_address}:7681)
                """
            self.md_show(res, md=True)
        else:
            res = f"""\
# Container has been deployed successfully: your reservation id is: {self.resv_id}
Your IP is  ```{self.ip_address}```
                """
            self.md_show(res, md=True)


chat = FlistDeploy
