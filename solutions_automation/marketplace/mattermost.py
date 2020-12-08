from jumpscale.packages.marketplace.chats.mattermost import MattermostDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class MattermostAutomated(GedisChatBotPatch, MattermostDeploy):
    pass
