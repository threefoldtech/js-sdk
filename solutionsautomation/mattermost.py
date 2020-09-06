from marketplacepatch import MarketPlaceAppsChatflowPatch
from jumpscale.packages.marketplace.chats.mattermost import MattermostDeploy
from time import time


class MattermostAutomated(MarketPlaceAppsChatflowPatch, MattermostDeploy):
    pass


test = MattermostAutomated(solution_name="test_automated1", currency="TFT", expiration=time() + 5 * 60, flavor="Silver")
