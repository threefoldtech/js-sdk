from jumpscale.packages.marketplace.chats.cryptpad import CryptpadDeploy
from utils.gedispatch import GedisChatBotPatch


class CryptpadAutomated(GedisChatBotPatch, CryptpadDeploy):
    pass
