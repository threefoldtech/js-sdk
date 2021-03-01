from jumpscale.packages.tfgrid_solutions.chats.pools import PoolReservation
from solutions_automation.utils.gedispatch import GedisChatBotPatch


class PoolAutomated(GedisChatBotPatch, PoolReservation):
    CAPACITY_POOL_NAME = "Please choose a name for your new capacity pool. This name will only be used by you to identify the pool for later usage and management."
    CU = "Required Amount of Compute Unit (CU)"
    SU = "Required Amount of Storage Unit (SU)"
    IPV4U = "Required Amount of Public IP Unit (IPv4U)"
    TIME_UNIT = "Please choose the duration unit"
    TIME_TO_LIVE = "Please specify the pools time-to-live"
    FARM = r"^Please choose a farm to reserve capacity from. By reserving IT Capacity, you are purchasing .*"
    PAYMENT = r"[\s\S]* .*Choose a wallet name to use for payment or proceed with payment through External wallet.*"

    QS = {
        CAPACITY_POOL_NAME: "get_name",
        CU: "cu",
        SU: "su",
        IPV4U: "ipv4u",
        TIME_UNIT: "time_unit",
        TIME_TO_LIVE: "time_to_live",
        FARM: "farm",
        PAYMENT: "wallet_name",
    }

    def single_choice(self, msg, *args, **kwargs):
        selected = self.fetch_param(msg, *args, **kwargs)
        for m in args[0]:
            if selected in m:
                return m
        return selected
