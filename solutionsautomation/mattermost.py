from marketplacepatch import MarketPlaceAppsChatflowPatch
from jumpscale.packages.marketplace.chats.mattermost import MattermostDeploy
from time import time


class MattermostAutomated(MarketPlaceAppsChatflowPatch, MattermostDeploy):
    pass


test = MattermostAutomated(
    solution_name="mattermostautomated", currency="TFT", expiration=time() + 60 * 15, flavor="Silver"
)
