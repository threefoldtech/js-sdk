from jumpscale.packages.marketplace.chats.cryptpad import CryptpadDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class CryptpadAutomated(GedisChatBotPatch, CryptpadDeploy):
    pass
