from marketplacepatch import MarketPlaceAppsChatflowPatch
from jumpscale.packages.marketplace.chats.cryptpad import CryptpadDeploy
from time import time


class CryptpadAutomated(MarketPlaceAppsChatflowPatch, CryptpadDeploy):
    pass


test = CryptpadAutomated(solution_name="cryptautomation", currency="TFT", expiration=time() + 60 * 15, flavor="Silver")
