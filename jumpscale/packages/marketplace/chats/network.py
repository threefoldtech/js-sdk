import time

from jumpscale.loader import j

from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.marketplace import deployer, MarketPlaceChatflow


class NetworkDeploy(MarketPlaceChatflow):
    SOLUTION_TYPE = SolutionType.Network

    steps = ["welcome", "solution_name", "expiration_time", "choose_currency", "network_info"]
    title = "Network"

    @chatflow_step(title="Network Information")
    def network_info(self):
        deployer.deploy_network(
            self.user_info()["username"], self.name, self.expiration, self.currency, self, self.user_form_data
        )


chat = NetworkDeploy
