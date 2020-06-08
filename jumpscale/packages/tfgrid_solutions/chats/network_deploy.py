from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step, StopChatFlow
import time


class NetworkDeploy(GedisChatBot):
    steps = ["network_reservation", "network_info"]
    
    @chatflow_step(title="Deploy Network")
    def network_reservation(self):
        user_form_data = {}
        user_info = self.user_info()
        # j.sals.reservation_chatflow.validate_user(user_info)
        user_form_data["chatflow"] = "network"
        network_name = self.string_ask("Please enter a network name", required=True, field="name")
        user_form_data["Currency"] = self.single_choice(
            "Please choose a currency that will be used for the payment", ["FreeTFT", "TFT"], default="TFT", required=True
        )
        expiration = self.datetime_picker(
            "Please enter network expiration time.",
            required=True,
            # min_time=[3600, "Date/time should be at least 1 hour from now"],
            # default=j.data.time.utcnow().timestamp + 3900,
        )

        ips = ["IPv6", "IPv4"]
        ipversion = self.single_choice(
            "How would you like to connect to your network? IPv4 or IPv6? If unsure, choose IPv4",
            ips, required=True
        )
        user_form_data["Solution expiration"] = j.data.time.get(expiration).humanize()


chat = NetworkDeploy
