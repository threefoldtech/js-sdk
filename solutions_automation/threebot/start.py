from textwrap import dedent

from jumpscale.packages.threebot_deployer.chats.restart_threebot import ThreebotRedeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class ThreebotStart(GedisChatBotPatch, ThreebotRedeploy):
    PASSWORD = "Please enter the 3Bot password."
    QS = {
        PASSWORD: "password",
    }

    def ask(self, msg, *args, **kwargs):
        return self.fetch_param(msg["msg"], *args, **kwargs)
