from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.gitea import GiteaDeploy
from time import time


class GiteaAutomated(GedisChatBotPatch, GiteaDeploy):
    pass


test = GiteaAutomated(solution_name="are", currency="TFT", expiration=time() + 60 * 15)
