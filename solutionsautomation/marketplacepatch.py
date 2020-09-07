from jumpscale.sals.chatflows.chatflows import GedisChatBot
from decimal import Decimal
from jumpscale.loader import j
from form import Form
from utils import is_message_matched, read_file


class MarketPlaceAppsChatflowPatch(GedisChatBot):
    NAME_MESSAGE = "Please enter a name for your solution (will be used in listing and deletions in the future and in having a unique url)"
    CURRENCY_MESSAGE = "Please select the currency you want to pay with."
    FLAVOR_MESSAGE = (
        "Please choose the flavor you want ot use (flavors define how much resources the deployed solution will use)"
    )

    QS_STR_BASE = {
        NAME_MESSAGE: "solution_name",
    }

    QS_INT_BASE = {}

    QS_CHOICE_BASE = {CURRENCY_MESSAGE: "currency", FLAVOR_MESSAGE: "flavor"}

    EXPECT_BASE = set(["solution_name", "currency", "expiration",])

    # To be overridden by child classes

    QS_STR = {}

    QS_INT = {}

    QS_CHOICE = {}

    EXPECT = set([])

    def __init__(self, **kwargs):
        self.EXPECT = self.EXPECT | self.EXPECT_BASE
        self.QS_CHOICE = {**self.QS_CHOICE, **self.QS_CHOICE_BASE}
        self.QS_STR = {**self.QS_STR, **self.QS_STR_BASE}
        self.QS_INT = {**self.QS_INT, **self.QS_INT_BASE}
        for k in self.EXPECT:
            if k not in kwargs:
                raise Exception(f"{k} not provided.")

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.name_qs = 0
        super().__init__(spawn=False)

    def user_info(self):
        return {"email": j.core.identity.me.email, "username": j.core.identity.me.tname}

    def md_show_update(self, msg, *args, **kwargs):
        print(msg)

    def md_show(self, msg, *args, **kwargs):
        print(msg)

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

    def string_ask(self, msg, **kwargs):
        for k, v in self.QS_STR.items():
            if is_message_matched(msg, k):
                return getattr(self, v)

    def int_ask(self, msg, **kwargs):
        for k, v in self.QS_INT.items():
            if is_message_matched(msg, k):
                return getattr(self, v)

    def single_choice(self, msg, *args, **kwargs):
        print(msg, args)
        for k, v in self.QS_CHOICE.items():
            if is_message_matched(msg, k):
                attr = getattr(self, v)
                if callable(attr):
                    return attr(msg, *args, **kwargs)
                else:
                    return attr

    def drop_down_choice(self, msg, *args, **kwargs):
        return self.single_choice(msg, *args, **kwargs)

    def upload_file(self, msg, *args, **kwargs):
        val = self.string_ask(msg, *args, **kwargs)
        return read_file(val)

    def new_form(self):
        return Form(self)

    def datetime_picker(self, *args, **kwargs):
        return self.expiration
