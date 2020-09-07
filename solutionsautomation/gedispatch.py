from jumpscale.sals.chatflows.chatflows import GedisChatBot
from decimal import Decimal
from jumpscale.loader import j
from form import Form
from utils import is_message_matched, read_file
from errors import MissingValueException, DuplicateSolutionNameException, MissingMessageException
import random


class GedisChatBotPatch(GedisChatBot):
    NAME_MESSAGE = "Please enter a name for your solution (will be used in listing and deletions in the future and in having a unique url)"
    CURRENCY_MESSAGE = "Please select the currency you want to pay with."
    FLAVOR_MESSAGE = (
        "Please choose the flavor you want ot use (flavors define how much resources the deployed solution will use)"
    )
    EXPIRATION_MESSAGE = "Please enter the solution's expiration time"
    WIREGUARD_CONFIG_MESSAGE = "Do you want to save the wireguard configration, it could help you to connect with your workload using ip address ?"
    QS_BASE = {
        NAME_MESSAGE: "get_name",
        CURRENCY_MESSAGE: "currency",
        FLAVOR_MESSAGE: "flavor",
        EXPIRATION_MESSAGE: "expiration",
        WIREGUARD_CONFIG_MESSAGE: "wg_config",
    }

    # To be overridden by child classes

    QS = {}

    def __init__(self, **kwargs):
        self.QS = {**self.QS, **self.QS_BASE}
        self.debug = kwargs.get("debug", False)

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.name_qs = 0
        super().__init__(spawn=False)

    def get_name(self, msg, *args, **kwargs):
        if self.name_qs == 0:
            self.name_qs = 1
            return self.solution_name
        else:
            raise DuplicateSolutionNameException("Solution name already exists")

    def user_info(self):
        return {"email": j.core.identity.me.email, "username": j.core.identity.me.tname}

    def md_show_update(self, msg, *args, **kwargs):
        if self.debug:
            print(msg)

    def md_show(self, msg, *args, **kwargs):
        if self.debug:
            print(msg)

    def choose_random(self, msg, options, *args, **kwargs):
        return random.choice(options)

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

    def fetch_param(self, msg, *args, **kwargs):
        for k, v in self.QS.items():
            if is_message_matched(msg, k):
                try:
                    attr = getattr(self, v)
                except AttributeError:
                    raise MissingValueException(f"{v} was not provided.")
                if callable(attr):
                    return attr(msg, *args, **kwargs)
                else:
                    return attr
        raise MissingMessageException(f"No entry found for the message: {msg}")

    def string_ask(self, msg, *args, **kwargs):
        return self.fetch_param(msg, *args, **kwargs)

    def int_ask(self, msg, *args, **kwargs):
        return self.fetch_param(msg, *args, **kwargs)

    def single_choice(self, msg, *args, **kwargs):
        return self.fetch_param(msg, *args, **kwargs)

    def drop_down_choice(self, msg, *args, **kwargs):
        return self.single_choice(msg, *args, **kwargs)

    def upload_file(self, msg, *args, **kwargs):
        val = self.string_ask(msg, *args, **kwargs)
        return read_file(val)

    def new_form(self):
        return Form(self)

    def datetime_picker(self, msg, *args, **kwargs):
        return self.fetch_param(msg, *args, **kwargs)
