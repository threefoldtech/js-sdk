from jumpscale.packages.marketplace.chats.mattermost import MattermostDeploy
from utils.gedispatch import GedisChatBotPatch


class MattermostAutomated(GedisChatBotPatch, MattermostDeploy):
    pass
