from jumpscale.packages.marketplace.chats.taiga import TaigaDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class TaigaAutomated(GedisChatBotPatch, TaigaDeploy):
    HOST_EMAIL = "Please add the host e-mail address for your solution"
    SMTP_HOST = r"^Please add the smtp host example: .*"
    HOST_EMAIL_PASSWORD = "Please add the host e-mail password"
    SECRET_KEY = "Please add a secret key for your solution"

    QS = {
        HOST_EMAIL: "host_email",
        SMTP_HOST: "smtp_host",
        HOST_EMAIL_PASSWORD: "host_email_password",
        SECRET_KEY: "secret",
    }
