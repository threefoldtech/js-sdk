from solutions_automation.vdc.dashboard.common import CommonChatBot
from jumpscale.packages.vdc_dashboard.chats.zeroci import ZeroCIDeploy


class ZeroCIAutomated(CommonChatBot, ZeroCIDeploy):
    pass
