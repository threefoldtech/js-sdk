from jumpscale.packages.tfgrid_solutions.chats.extend_pools import PoolExtend
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class PoolExtendAutomated(GedisChatBotPatch, PoolExtend):
    CU = "Required Amount of Compute Unit (CU)"
    SU = "Required Amount of Storage Unit (SU)"
    IPV4U = "Required Amount of Public IP Unit (IPv4U)"
    TIME_UNIT = "Please choose the duration unit"
    TIME_TO_LIVE = "Please specify the pools time-to-live"
    PAYMENT = r"[\s\S]* .*Choose a wallet name to use for payment or proceed with payment through External wallet.*"

    QS = {
        CU: "cu",
        SU: "su",
        IPV4U: "ipv4u",
        TIME_UNIT: "time_unit",
        TIME_TO_LIVE: "time_to_live",
        PAYMENT: "wallet_name",
    }

    def single_choice(self, msg, *args, **kwargs):
        selected = self.fetch_param(msg, *args, **kwargs)
        for m in args[0]:
            if selected in m:
                return m
        return selected
