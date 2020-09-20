from jumpscale.packages.marketplace.chats.gitea import GiteaDeploy
from utils.gedispatch import GedisChatBotPatch


class GiteaAutomated(GedisChatBotPatch, GiteaDeploy):
    pass
