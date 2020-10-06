from jumpscale.packages.threebot_deployer.chats.threebot import ThreebotDeploy
from utils.gedispatch import GedisChatBotPatch


class ThreebotDeployAutomated(GedisChatBotPatch, ThreebotDeploy):
    TYPE = "Would you like to create a new 3Bot instance, or recover an existing one?"
    NAME = "Just like humans, each 3Bot needs their own unique identity to exist on top of the Threefold Grid. Please enter a name for your new 3Bot. This name will be used as the web address that could give you access to your 3Bot anytime."
    RECOVER_NAME = "Please enter the 3Bot name you want to recover"
    SECRET = "Please create a secure password for your new 3Bot. This password is used to recover your hosted 3Bot."
    SSH = "Please upload your public ssh key, this will allow you to access your threebot container using ssh"
    RECOVER_PASSWORD = "Please enter the recovery password"
    EXPIRATION = "Please enter the solution's expiration time"
    QS = {
        TYPE: "type",
        NAME: "get_name",
        RECOVER_NAME: "get_name",
        RECOVER_PASSWORD: "recover_password",
        SECRET: "secret",
        SSH: "ssh",
        EXPIRATION: "expiration",
    }

    def ask(self, msg, *args, **kwargs):
        return self.fetch_param(msg["msg"], *args, **kwargs)
