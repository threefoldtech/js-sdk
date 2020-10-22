from textwrap import dedent

from jumpscale.packages.threebot_deployer.chats.threebot import ThreebotDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch, read_file


class ThreebotDeployAutomated(GedisChatBotPatch, ThreebotDeploy):
    TYPE = "Would you like to create a new 3Bot instance, or recover an existing one?"
    NAME = "Just like humans, each 3Bot needs their own unique identity to exist on top of the Threefold Grid. Please enter a name for your new 3Bot. This name will be used as the web address that could give you access to your 3Bot anytime."
    RECOVER_NAME = "Please enter the 3Bot name you want to recover"
    SECRET = "Please create a secure password for your new 3Bot. This password is used to recover your hosted 3Bot."
    SSH = "Please upload your public ssh key, this will allow you to access your threebot container using ssh"
    RECOVER_PASSWORD = "Please enter the recovery password"
    EXPIRATION = "Please enter the solution's expiration time"
    DOMAIN_TYPE = "Do you want to manage the domain for the container or automatically get a domain of ours?"
    DOMAIN_NAME = "Please specify the domain name you wish to bind to"
    WIREGUARD = dedent(
        """
        <h3> Use the following template to configure your wireguard connection. This will give you access to your network. </h3>
        <h3> Make sure you have <a target="_blank" href="https://www.wireguard.com/install/">wireguard</a> installed </h3>
        <br /><br />*"""
    )
    QS = {
        TYPE: "type",
        NAME: "get_name",
        RECOVER_NAME: "get_name",
        RECOVER_PASSWORD: "recover_password",
        SECRET: "secret",
        SSH: "ssh",
        EXPIRATION: "expiration",
        DOMAIN_TYPE: "domain_type",
        DOMAIN_NAME: "domain_name",
    }

    def ask(self, msg, *args, **kwargs):
        return self.fetch_param(msg["msg"], *args, **kwargs)

    def upload_file(self, msg, *args, **kwargs):
        val = self.string_ask(msg, *args, **kwargs)
        if not val:
            return ""
        return read_file(val)
