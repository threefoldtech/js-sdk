from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.mattermost import MattermostDeploy


class MattermostAutomated(GedisChatBotPatch, MattermostDeploy):
    pass
