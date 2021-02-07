from solutions_automation.vdc.dashboard.common import CommonChatBot
from jumpscale.packages.vdc_dashboard.chats.digibyte import DigibyteDeploy


class DigibyteAutomated(CommonChatBot, DigibyteDeploy):
    USERNAME_MESSAGE = "RPC Username"
    PASSWORD_MESSAGE = "RPC Password"

    QS = {
        USERNAME_MESSAGE: "rpc_username",
        PASSWORD_MESSAGE: "rpc_password",
    }
