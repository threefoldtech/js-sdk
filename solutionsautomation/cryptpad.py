from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.cryptpad import CryptpadDeploy


class CryptpadAutomated(GedisChatBotPatch, CryptpadDeploy):
    pass
