from jumpscale.packages.marketplace.chats.discourse import Discourse
from utils.gedispatch import GedisChatBotPatch


class DiscourseAutomated(GedisChatBotPatch, Discourse):
    HOST_EMAIL = "Please add the host e-mail address for your solution"
    SMTP_HOST = r"^Please add the smtp host .*"
    HOST_EMAIL_PASSWORD = "Please add the host e-mail password"

    QS = {
        HOST_EMAIL: "host_email",
        SMTP_HOST: "stmp_host",
        HOST_EMAIL_PASSWORD: "host_email_password",
    }
