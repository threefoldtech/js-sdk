from marketplacepatch import MarketPlaceAppsChatflowPatch
from jumpscale.packages.marketplace.chats.gitea import GiteaDeploy
from time import time


class GiteaAutomated(MarketPlaceAppsChatflowPatch, GiteaDeploy):
    pass


test = GiteaAutomated(solution_name="are", currency="TFT", expiration=time() + 60 * 15)
