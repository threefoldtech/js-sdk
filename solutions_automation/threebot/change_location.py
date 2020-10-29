from textwrap import dedent

from jumpscale.packages.threebot_deployer.chats.change_location import ThreebotRedeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class ThreebotChangeLocation(GedisChatBotPatch, ThreebotRedeploy):
    PASSWORD = "Please enter the 3Bot password."
    NODE_POLICY = "Please select the deployment location policy."
    EXPIRATION = "Please enter the solution's expiration time"
    QS = {
        PASSWORD: "password",
        NODE_POLICY: "node_policy",
        EXPIRATION: "expiration",
    }

    def ask(self, msg, *args, **kwargs):
        return self.fetch_param(msg["msg"], *args, **kwargs)
