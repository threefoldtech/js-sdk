from gedispatch import GedisChatBotPatch
from jumpscale.packages.tfgrid_solutions.chats.pools import PoolReservation
from decimal import Decimal
import os
import re

re.DOTALL
WALLET_NAME = os.environ.get("WALLET_NAME")


class PoolAutomated(GedisChatBotPatch, PoolReservation):
    CREATE_POOL = "Would you like to create a new capacity pool, or extend an existing one?"
    CAPACITY_POOL_NAME = "Please choose a name for your new capacity pool. This name will only be used by you to identify the pool for later usage and management."
    CU = "Required Amount of Compute Unit (CU)"
    SU = "Required Amount of Storage Unit (SU)"
    TIME_UNIT = "Please choose the duration unit"
    TIME_TO_LIVE = "Please specify the pools time-to-live"
    FARM = r"^Please choose a farm to reserve capacity from. By reserving IT Capacity, you are purchasing .*"
    PAYMENT = r"[\s\S]* .*Choose a wallet name to use for payment or proceed with payment through External wallet.*"
    EXTEND_POOL = "Please select a pool"

    QS = {
        CREATE_POOL: "type",
        CAPACITY_POOL_NAME: "get_name",
        CU: "cu",
        SU: "su",
        TIME_UNIT: "time_unit",
        TIME_TO_LIVE: "time_to_live",
        FARM: "choose_random",
        PAYMENT: "wallet_name",
        EXTEND_POOL: "choose_random",
    }

    def show_payment(self, pool, **kwargs):
        escrow_info = pool.escrow_information
        resv_id = pool.reservation_id
        escrow_address = escrow_info.address
        escrow_asset = escrow_info.asset
        total_amount = escrow_info.amount
        total_amount_dec = Decimal(total_amount) / Decimal(1e7)
        thecurrency = escrow_asset.split(":")[0]
        total_amount = "{0:f}".format(total_amount_dec)
        wallet = self.get_wallet()
        wallet.transfer(
            escrow_address,
            f"{total_amount_dec}",
            asset=thecurrency + ":" + wallet.get_asset(thecurrency).issuer,
            memo_text=f"p-{resv_id}",
        )
