from jumpscale.packages.marketplace.chats.discourse import Discourse
from utils.gedispatch import GedisChatBotPatch


class DiscourseAutomated(GedisChatBotPatch, Discourse):
    SMTP_EMIAL = "Please add the host e-mail address for your solution"
    SMTP_HOST = r"^Please add the smtp host .*"
    STMP_PASSWORD = "Please add the host e-mail password"

    QS = {
        SMTP_EMIAL: "smtp_email",
        SMTP_HOST: "stmp_host",
        STMP_PASSWORD: "stmp_password",
    }
