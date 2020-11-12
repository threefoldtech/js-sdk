from jumpscale.packages.threebot_deployer.chats.change_size import ThreebotRedeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class ThreebotChangeSizeAutomated(GedisChatBotPatch, ThreebotRedeploy):
    PASSWORD = "Please enter the 3Bot password."

    QS = {
        PASSWORD: "password",
    }

    def ask(self, msg, *args, **kwargs):
        return self.fetch_param(msg["msg"], *args, **kwargs)
