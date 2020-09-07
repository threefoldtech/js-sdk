from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.mattermost import MattermostDeploy
from time import time


class MattermostAutomated(GedisChatBotPatch, MattermostDeploy):
    pass


test = MattermostAutomated(
    solution_name="mattermostautomated",
    currency="TFT",
    expiration=time() + 60 * 15,
    flavor="Silver",
    wg_config="NO",
    debug=True,
)
