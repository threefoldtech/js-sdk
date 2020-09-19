from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.discourse import Discourse


class DiscourseAutomated(GedisChatBotPatch, Discourse):
    HOST_EMAIL = "Please add the host e-mail address for your solution"
    SMTP_EMIAL = r"^Please add the smtp host .*"
    SMTP_USERNAME = "SMTP Server Username"
    STMP_PASSWORD = "Please add the host e-mail password"

    QS = {
        HOST_EMAIL: "host_email",
        SMTP_EMIAL: "smtp_email",
        SMTP_USERNAME: "stmp_username",
        STMP_PASSWORD: "stmp_password",
    }
