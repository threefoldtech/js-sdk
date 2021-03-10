from textwrap import dedent

from jumpscale.packages.threebot_deployer.chats.threebot import ThreebotDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch, read_file


class ThreebotDeployAutomated(GedisChatBotPatch, ThreebotDeploy):
    TYPE = "Would you like to create a new 3Bot instance,*?"
    NAME = "Just like humans, each 3Bot needs its own unique identity. Please enter a name for your new 3Bot. This name can only consist of lower case letters and no special characters."
    RECOVER_NAME = "Please enter the 3Bot name you want to recover"
    SECRET = "Please create a secure password for your new 3Bot. This password is used to recover your hosted 3Bot."
    SSH = "Please upload your public ssh key, this will allow you to access your threebot container using ssh"
    RECOVER_PASSWORD = "Please enter the recovery password"
    EXPIRATION = "Please enter the solution's expiration time"
    DOMAIN_TYPE = "Do you want to manage the domain for the container or automatically get a domain of ours?"
    DOMAIN_NAME = "Please specify the domain name you wish to bind to"
    EMAIL_HOST_USER = "E-mail address for your solution"
    EMAIL_HOST = "SMTP host example: `smtp.gmail.com`"
    EMAIL_HOST_PASSWORD = "Host e-mail password"
    NODE_POLICY = "Please select the deployment location policy."
    ESCALATION_MAIL_ADDRESS = "Email address to receive email notifications on"
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
        EMAIL_HOST_USER: "email_host_user",
        EMAIL_HOST: "email_host",
        EMAIL_HOST_PASSWORD: "email_host_password",
        ESCALATION_MAIL_ADDRESS: "escalation_mail_address",
        NODE_POLICY: "node_policy",
    }

    def ask(self, msg, *args, **kwargs):
        return self.fetch_param(msg["msg"], *args, **kwargs)

    def upload_file(self, msg, *args, **kwargs):
        val = self.string_ask(msg, *args, **kwargs)
        if not val:
            return ""
        return read_file(val)
