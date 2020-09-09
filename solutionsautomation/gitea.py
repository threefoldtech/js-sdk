from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.gitea import GiteaDeploy


class GiteaAutomated(GedisChatBotPatch, GiteaDeploy):
    pass
