from solutions_automation.vdc.dashboard.common import CommonChatBot
from jumpscale.packages.vdc_dashboard.chats.discourse import DiscourseDeploy


class DiscourseAutomated(CommonChatBot, DiscourseDeploy):
    ADMIN_USER_MESSAGE = "Admin username"
    ADMIN_PASSWORD_MESSAGE = "Admin Password (should be at least 10 characters long, Shouldn't include username)"
    SMTP_HOST_MESSAGE = "SMTP Host"
    SMTP_PORT_MESSAGE = "SMTP Port"
    SMTP_USERNAME_MESSAGE = "Email (SMTP username)"
    SMTP_PASSWORD_MESSAGE = "Email Password"

    QS = {
        ADMIN_USER_MESSAGE: "admin_username",
        ADMIN_PASSWORD_MESSAGE: "admin_password",
        SMTP_HOST_MESSAGE: "smtp_host",
        SMTP_PORT_MESSAGE: "smtp_port",
        SMTP_USERNAME_MESSAGE: "smtp_username",
        SMTP_PASSWORD_MESSAGE: "smtp_password",
    }
