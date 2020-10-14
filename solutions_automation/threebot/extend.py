from jumpscale.packages.threebot_deployer.chats.extend import ExtendThreebot
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class ThreebotExtendAutomated(GedisChatBotPatch, ExtendThreebot):
    NAME = "Choose the 3Bot you would like to extend"
    EXPIRATION = "Please enter the solution's expiration time"
    QS = {
        NAME: "name",
        EXPIRATION: "expiration",
    }
