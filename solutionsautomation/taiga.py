from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.taiga import TaigaDeploy


class TaigaAutomated(GedisChatBotPatch, TaigaDeploy):
    HOST_EMAIL = "Please add the host e-mail address for your solution"
    SMTP_EMAIL = r"^Please add the smtp host example: .*"
    SMTP_PASSWORD = "Please add the host e-mail password"
    SECRET_KEY = "Please add a secret key for your solution"

    QS = {
        HOST_EMAIL: "host_email",
        SMTP_EMAIL: "smtp_email",
        SMTP_PASSWORD: "stmp_password",
        SECRET_KEY: "secret",
    }
