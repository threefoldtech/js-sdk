import time

from jumpscale.god import j

from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.deployer import deployer, MarketPlaceChatflow


class NetworkDeploy(MarketPlaceChatflow):
    SOLUTION_TYPE = "Network"

    steps = ["solution_name", "expiration_time", "choose_currency", "network_info"]

    @chatflow_step(title="Network Information")
    def network_info(self):
        deployer.deploy_network(self.get_tid(), self.name, self.expiration, self.currency, self, self.user_form_data)


chat = NetworkDeploy
