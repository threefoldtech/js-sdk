from jumpscale.packages.threebot_deployer.chats.threebot import ThreebotDeploy
from utils.gedispatch import GedisChatBotPatch, read_file


class ThreebotDeployAutomated(GedisChatBotPatch, ThreebotDeploy):
    TYPE = "Would you like to create a new 3Bot instance, or recover an existing one?"
    NAME = "Just like humans, each 3Bot needs their own unique identity to exist on top of the Threefold Grid. Please enter a name for your new 3Bot. This name will be used as the web address that could give you access to your 3Bot anytime."
    RECOVER_NAME = "Please enter the 3Bot name you want to recover"
    SECRET = "Please create a secure password for your new 3Bot. This password is used to recover your hosted 3Bot."
    RECOVER_PASSWORD = "Please enter the recovery password"
    EXPIRATION = "Please enter the solution's expiration time"
    DOMAIN_TYPE = "Do you want to manage the domain for the container or automatically get a domain of ours?"
    DOMAIN_NAME = "Please specify the domain name you wish to bind to"
    PUBLIC_KEY = "Please upload your public ssh key, this will allow you to access your threebot container using ssh"
    QS = {
        TYPE: "type",
        NAME: "get_name",
        RECOVER_NAME: "get_name",
        RECOVER_PASSWORD: "recover_password",
        SECRET: "secret",
        EXPIRATION: "expiration",
        DOMAIN_TYPE: "domain_type",
        DOMAIN_NAME: "domain_name",
        PUBLIC_KEY: "public_key",
    }

    def ask(self, msg, *args, **kwargs):
        return self.fetch_param(msg["msg"], *args, **kwargs)

    def upload_file(self, msg, *args, **kwargs):
        val = self.string_ask(msg, *args, **kwargs)
        if not val:
            return ""
        return read_file(val)
