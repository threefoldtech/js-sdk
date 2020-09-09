from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.taiga import TaigaDeploy


class TaigaAutomated(GedisChatBotPatch, TaigaDeploy):
    SMTP_EMAIL = "Please add the host e-mail address for your solution."
    SMTP_USERNAME = "Please add the smtp host example: `smtp.gmail.com`"
    SMTP_PASSWORD = "Please add the host e-mail password"
    SECRET_KEY = "Please add a secret key for your solution"

    QS = {
        SMTP_EMAIL: "smtp_email",
        SMTP_USERNAME: "stmp_username",
        SMTP_PASSWORD: "stmp_password",
        SECRET_KEY: "secret",
    }
