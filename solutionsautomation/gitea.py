from marketplacepatch import MarketPlaceAppsChatflowPatch
from jumpscale.packages.marketplace.chats.gitea import GiteaDeploy
from time import time


class GiteaAutomated(MarketPlaceAppsChatflowPatch, GiteaDeploy):
    pass


test = GiteaAutomated(solution_name="test_automated", currency="TFT", expiration=time() + 5 * 60)
