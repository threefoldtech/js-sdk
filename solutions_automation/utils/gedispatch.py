import os
import random
from decimal import Decimal

from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot

from .errors import DuplicateSolutionNameException, MissingMessageException, MissingValueException
from .form import Form
from .utils import is_message_matched, read_file, write_file


class GedisChatBotPatch(GedisChatBot):
    NAME_MESSAGE = "Please enter a name for your solution (will be used in listing and deletions in the future and in having a unique url)"
    CURRENCY_MESSAGE = "Please select the currency you want to pay with."
    FLAVOR_MESSAGE = (
        "Please choose the flavor you want to use (flavors define how much resources the deployed solution will use)"
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
        self.QS = {**self.QS_BASE, **self.QS}
        self.debug = kwargs.get("debug", False)

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.name_qs = 0
        super().__init__(spawn=False, **kwargs)

    def get_name(self, msg, *args, **kwargs):
        if self.name_qs == 0:
            self.name_qs = 1
            return self.solution_name
        else:
            raise DuplicateSolutionNameException("Solution name already exists")

    def get_wallet(self):
        wallet = j.clients.stellar.find("demos_wallet")
        if not wallet:
            raise ValueError(f"Couldn't find wallet with name 'demos_wallet'")
        return wallet

    def user_info(self):
        return {"email": j.core.identity.me.email, "username": j.core.identity.me.tname}

    def md_show_update(self, msg, *args, **kwargs):
        if self.debug:
            j.logger.info(msg)

    def md_show(self, msg, *args, **kwargs):
        if self.debug:
            j.logger.info(msg)

    def choose_random(self, msg, options, *args, **kwargs):
        return random.choice(options)

    def multi_choice(self, msg, options, *args, **kwargs):
        values = []
        values.append(random.choice(options))
        options.remove(values[0])
        if options:
            values.append(random.choice(options))
        return values

    def qrcode_show(self, pool, **kwargs):
        escrow_info = pool.escrow_information
        resv_id = pool.reservation_id
        escrow_address = escrow_info.address
        escrow_asset = escrow_info.asset
        total_amount = escrow_info.amount
        total_amount_dec = Decimal(total_amount) / Decimal(1e7)
        total_amount = "{0:f}".format(total_amount_dec)
        wallet = self.get_wallet()
        wallet.transfer(
            escrow_address, f"{total_amount_dec}", asset=escrow_asset, memo_text=f"p-{resv_id}",
        )

    def fetch_param(self, msg, *args, **kwargs):
        for k, v in self.QS.items():
            if is_message_matched(msg, k):
                try:
                    attr = getattr(self, v)
                    if attr is None:
                        raise AttributeError
                except AttributeError:
                    raise MissingValueException(f"{v} was not provided.")
                try:
                    attr = getattr(self, attr)
                except:
                    pass
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

    def multi_list_choice(self, msg, *args, **kwargs):
        return self.fetch_param(msg, *args, **kwargs)

    def multi_values_ask(self, msg, *args, **kwargs):
        return self.fetch_param(msg, *args, **kwargs)

    def download_file(self, msg, data, filename, **kwargs):
        return write_file(filename, data)

    def send_error(self, message, **kwargs):
        pass
