from solutions_automation.vdc.dashboard.common import CommonChatBot
from jumpscale.packages.vdc_dashboard.chats.cryptpad import CryptpadDeploy


class CryptpadAutomated(CommonChatBot, CryptpadDeploy):
    pass
