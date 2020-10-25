from jumpscale.packages.marketplace.chats.gitea import GiteaDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class GiteaAutomated(GedisChatBotPatch, GiteaDeploy):
    pass
