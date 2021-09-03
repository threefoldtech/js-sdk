from solutions_automation.vdc.dashboard.common import CommonChatBot
from jumpscale.packages.vdc_dashboard.chats.taiga import TaigaDeploy


class TaigaAutomated(CommonChatBot, TaigaDeploy):
    pass
