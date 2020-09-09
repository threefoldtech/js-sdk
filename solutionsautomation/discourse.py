from gedispatch import GedisChatBotPatch
from jumpscale.packages.marketplace.chats.discourse import Discourse


class DiscourseAutomated(GedisChatBotPatch, Discourse):
    SMTP_EMIAL = "SMTP Server Address"
    SMTP_USERNAME = "SMTP Server Username"
    STMP_PASSWORD = "SMTP Server Password"

    QS = {
        SMTP_EMIAL: "smtp_email",
        SMTP_USERNAME: "stmp_username",
        STMP_PASSWORD: "stmp_password",
    }
