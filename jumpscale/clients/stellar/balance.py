from stellar_sdk import TransactionEnvelope
import datetime
import time


class Balance:
    def __init__(self, balance=0.0, asset_code="XLM", asset_issuer=None):
        self.balance = balance
        self.asset_code = asset_code
        self.asset_issuer = asset_issuer

    @staticmethod
    def from_horizon_response(response_balance):
        balance = response_balance["balance"]
        if response_balance["asset_type"] == "native":
            asset_code = "XLM"
            asset_issuer = None
        else:
            asset_code = response_balance["asset_code"]
            asset_issuer = response_balance["asset_issuer"]
        return Balance(balance, asset_code, asset_issuer)

    def is_native(self):
        return self.asset_code == "XLM" and self.asset_issuer is None

    def __str__(self):
        representation = f"{self.balance} {self.asset_code}"
        if self.asset_issuer is not None:
            representation += f":{self.asset_issuer}"
        return representation

    def __repr__(self):
        return str(self)


class EscrowAccount:
    def __init__(self, address, unlockhashes, balances, network_passphrase, _get_unlockhash_transaction):
        self.address = address
        self.unlockhashes = unlockhashes
        self.balances = balances
        self.network_passphrase = network_passphrase
        self._get_unlockhash_transaction = _get_unlockhash_transaction
        self.unlock_time = None
        self._set_unlock_conditions()

    def _set_unlock_conditions(self):
        for unlockhash in self.unlockhashes:
            unlockhash_tx = self._get_unlockhash_transaction(unlockhash=unlockhash)
            if unlockhash_tx is None:
                return

            txe = TransactionEnvelope.from_xdr(unlockhash_tx["transaction_xdr"], self.network_passphrase)
            tx = txe.transaction
            if tx.time_bounds is not None:
                self.unlock_time = tx.time_bounds.min_time

    def can_be_unlocked(self):
        if len(self.unlockhashes) == 0:
            return True
        if self.unlock_time is not None:
            return time.time() > self.unlock_time
        return False

    def __str__(self):
        if self.unlock_time is not None:
            representation = "Locked until {unlock_time:%B %d %Y %H:%M:%S} on escrow account {account_id} ".format(
                account_id=self.address, unlock_time=datetime.datetime.fromtimestamp(self.unlock_time)
            )
        else:
            if len(self.unlockhashes) == 0:
                representation = f"Free to be claimed on escrow account {self.address}"
            else:
                representation = f"Escrow account {self.address} with unknown unlockhashes {self.unlockhashes}"
        for balance in self.balances:
            representation += f"\n- {balance.balance} {balance.asset_code}"
            if balance.asset_issuer is not None:
                representation += f":{balance.asset_issuer}"
        return representation

    def __repr__(self):
        return str(self)


class VestingAccount:
    def __init__(self, address, balances, scheme):
        self.address = address
        self.balances = balances
        self.scheme = scheme

    def __str__(self):
        representation = f"Vesting Account {self.address}"
        for balance in self.balances:
            representation += f"\n- {balance.balance} {balance.asset_code}"
            if balance.asset_issuer is not None:
                representation += f":{balance.asset_issuer}"
        return representation

    def __repr__(self):
        return str(self)


class AccountBalances:
    def __init__(self, address):
        self.address = address
        self.balances = []
        self.escrow_accounts = []
        self.vesting_accounts = []

    def add_balance(self, balance):
        self.balances.append(balance)

    def add_escrow_account(self, account):
        if type(account) is VestingAccount:
            self.vesting_accounts.append(account)
        else:
            self.escrow_accounts.append(account)

    def __str__(self):
        representation = "Balances"
        for balance in self.balances:
            representation += "\n  " + str(balance)
        for vesting_account in self.vesting_accounts:
            representation += f"\n{str(vesting_account)}"

        if self.escrow_accounts:
            representation += "\nLocked balances:"
            for escrow_account in self.escrow_accounts:
                representation += f"\n - {str(escrow_account)}"
        return representation

    def __repr__(self):
        return str(self)
