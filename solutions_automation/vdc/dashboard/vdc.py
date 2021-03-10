from jumpscale.packages.vdc.chats.new_vdc import VDCDeploy
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class VDCAutomated(GedisChatBotPatch, VDCDeploy):
    NAME_MESSAGE = "Please enter a name for your VDC (will be used in listing and deletions in the future and in having a unique url)"
    VDC_SECERT = "VDC Secret (Secret for controlling the vdc)"
    VDC_PLAN = "Choose the VDC plan"
    PAYMENT = r"^Please scan the QR Code below for the payment details .*"
    ZDB_FARMS = "Do you wish to select farms for storage automatically?"

    QS = {
        NAME_MESSAGE: "get_name",
        VDC_SECERT: "vdc_secert",
        VDC_PLAN: "vdc_plan",
        PAYMENT: "md_show_update",
        ZDB_FARMS: "zdb_Farms",
    }
