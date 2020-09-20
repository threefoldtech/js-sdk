from jumpscale.packages.marketplace.chats.taiga import TaigaDeploy
from utils.gedispatch import GedisChatBotPatch


class TaigaAutomated(GedisChatBotPatch, TaigaDeploy):
    SMTP_HOST = "Please add the host e-mail address for your solution"
    SMTP_EMAIL = r"^Please add the smtp host example: .*"
    SMTP_PASSWORD = "Please add the host e-mail password"
    SECRET_KEY = "Please add a secret key for your solution"

    QS = {
        SMTP_HOST: "smtp_host",
        SMTP_EMAIL: "smtp_email",
        SMTP_PASSWORD: "stmp_password",
        SECRET_KEY: "secret",
    }
