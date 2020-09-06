from jumpscale.sals.marketplace import MarketPlaceAppsChatflow
from jumpscale.sals.chatflows.chatflows import StopChatFlow
from decimal import Decimal
from jumpscale.loader import j


class MarketPlaceAppsChatflowPatch(MarketPlaceAppsChatflow):
    NAME_MESSAGE = "Please enter a name for your solution (will be used in listing and deletions in the future and in having a unique url)"
    CURRENCY_MESSAGE = "Please select the currency you want to pay with."
    FLAVOR_MESSAGE = (
        "Please choose the flavor you want ot use (flavors define how much resources the deployed solution will use)"
    )

    QS_STR = {
        NAME_MESSAGE: "get_name",
    }

    QS_CHOICE = {CURRENCY_MESSAGE: "get_currency", FLAVOR_MESSAGE: "get_flavor"}

    EXPECT = [
        "solution_name",
        "currency",
        "expiration",
    ]

    def __init__(self, **kwargs):
        for k in self.EXPECT:
            if k not in kwargs:
                raise Exception(f"{k} not provided.")

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.name_qs = 0
        super().__init__(spawn=True, **kwargs)

    def user_info(self):
        return {"email": j.core.identity.me.tname, "username": "omar0.3bot"}

    def go(self):
        for step in self.steps:
            getattr(self, step)()

    def md_show_update(self, msg, *args, **kwargs):
        pass

    def md_show(self, msg, *args, **kwargs):
        pass

    def qrcode_show(self, pool, **kwargs):
        escrow_info = pool.escrow_information
        resv_id = pool.reservation_id
        escrow_address = escrow_info.address
        escrow_asset = escrow_info.asset
        total_amount = escrow_info.amount
        total_amount_dec = Decimal(total_amount) / Decimal(1e7)
        thecurrency = escrow_asset.split(":")[0]
        total_amount = "{0:f}".format(total_amount_dec)
        j.clients.stellar.wallet.transfer(
            escrow_address,
            f"{total_amount_dec}",
            asset=thecurrency + ":" + j.clients.stellar.wallet.get_asset(thecurrency).issuer,
            memo_text=f"p-{resv_id}",
        )

    def get_name(self, **kwargs):
        if self.name_qs == 0:
            self.name_qs = 1
            return self.solution_name
        else:
            raise StopChatFlow("Name already exists")

    def get_currency(self, **kwargs):
        return self.currency

    def get_flavor(self, *args, **kwargs):
        return self.flavor

    def string_ask(self, msg, **kwargs):
        for k, v in self.QS_STR.items():
            if k == msg:
                return getattr(self, v)(**kwargs)

    def single_choice(self, msg, *args, **kwargs):
        for k, v in self.QS_CHOICE.items():
            if k == msg:
                return getattr(self, v)(**kwargs)

    def datetime_picker(self, *args, **kwargs):
        return self.expiration
