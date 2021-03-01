from solutions_automation.vdc.dashboard.common import CommonChatBot
from jumpscale.packages.vdc_dashboard.chats.cryptpad import CryptpadDeploy


class CryptpadAutomated(CommonChatBot, CryptpadDeploy):
    STORAGE_SIZE_MESSAGE = "Please select your storage size (in GBs)"

    QS = {
        STORAGE_SIZE_MESSAGE: "storage_size",
    }
