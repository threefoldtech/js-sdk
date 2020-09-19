from gedispatch import GedisChatBotPatch
from jumpscale.packages.threebot_deployer.chats.threebot import ThreebotDeploy
from time import time


class ThreebotDeployAutomated(GedisChatBotPatch, ThreebotDeploy):
    TYPE = "Would you like to create a new 3Bot instance, or recover an existing one?"
    MESSAGE_NAME = "Just like humans, each 3Bot needs their own unique identity to exist on top of the Threefold Grid. Please enter a name for your new 3Bot. This name will be used as the web address that could give you access to your 3Bot anytime."
    SECRET = "Please create a secure password for your new 3Bot. This password is used to recover your hosted 3Bot."
    EXPIRATION = "Please enter the expiration date of your 3Bot. This will be used to calculate the amount of capacity you need to keep your 3Bot alive and build projects on top of the TF Grid. But no worries, you could always extend your 3Bot’s lifetime on 3Bot Deployer's home screen"
    QS = {
        TYPE: "type",
        MESSAGE_NAME: "get_name",
        SECRET: "secret",
    }

    def ask(self, msg, **kwargs):
        pass
