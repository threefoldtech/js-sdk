from solutions_automation.vdc.dashboard.common import CommonChatBot
from jumpscale.packages.vdc_dashboard.chats.mattermost import MattermostDeploy


class MattermostAutomated(CommonChatBot, MattermostDeploy):

    MYSQL_USER_NAME_MESSAGE = "Enter mysql user name"
    MYSQL_USER_PASSWORD_MESSAGE = "Enter mysql password"
    MYSQL_ROOT_PASSWORD_MESSAGE = "Enter mysql password for root user"

    QS = {
        MYSQL_USER_NAME_MESSAGE: "mysql_username",
        MYSQL_USER_PASSWORD_MESSAGE: "mysql_password",
        MYSQL_ROOT_PASSWORD_MESSAGE: "mysql_root_password",
    }
