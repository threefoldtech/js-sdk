from solutions_automation.vdc.dashboard.common import CommonChatBot
from jumpscale.packages.vdc_dashboard.chats.gitea import GiteaDeploy


class GiteaAutomated(CommonChatBot, GiteaDeploy):
    pass
