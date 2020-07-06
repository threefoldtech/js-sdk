from .balance import Balance
import decimal, base64, binascii


class TransactionSummary:
    def __init__(self, hash, memo_text=None, memo_hash=None, created_at=None):
        self.hash = hash
        self.memo_text = memo_text
        self.memo_hash = memo_hash
        self.created_at = created_at

    @property
    def memo_hash_as_hex(self):
        if not self.memo_hash:
            return None
        return binascii.hexlify(base64.b64decode(self.memo_hash)).decode("utf-8")

    @staticmethod
    def from_horizon_response(response_transaction):
        hash = response_transaction["hash"]
        created_at = response_transaction["created_at"]
        memo_text = None
        memo_hash = None
        if "memo" in response_transaction:
            if response_transaction["memo_type"] == "text":
                memo_text = response_transaction["memo"]
            if response_transaction["memo_type"] == "hash":
                memo_hash = response_transaction["memo"]
        return TransactionSummary(hash, memo_text, memo_hash, created_at)

    def __str__(self):
        representation = f"{self.hash} created at {self.created_at}"
        if self.memo_text is not None:
            representation += f" with memo text '{self.memo_text}'"
        if self.memo_hash is not None:
            representation += f" with memo hash '{self.memo_hash}'"
        return representation

    def __repr__(self):
        return str(self)


class Effect:
    def __init__(self, amount=0.0, asset_code="XLM", asset_issuer=None):
        self.amount = amount
        self.asset_code = asset_code
        self.asset_issuer = asset_issuer

    @staticmethod
    def from_horizon_response(response_effect):
        amount = decimal.Decimal(response_effect["amount"])
        if response_effect["asset_type"] == "native":
            asset_code = "XLM"
            asset_issuer = None
        else:
            asset_code = response_effect["asset_code"]
            asset_issuer = response_effect["asset_issuer"]
        if "type" in response_effect and response_effect["type"] == "account_debited":
            amount = -amount
        return Effect(amount, asset_code, asset_issuer)

    def __str__(self):
        balance = Balance(self.amount, self.asset_code, self.asset_issuer)
        representation = str(balance)
        return representation

    def __repr__(self):
        return str(self)


class PaymentSummary(object):
    def __init__(
        self,
        transaction_hash,
        balance: Balance,
        payment_type: str,
        created_at,
        from_address: str,
        to_address: str,
        my_address: str,
    ):
        self.balance = balance
        self.created_at = created_at
        self.from_address = from_address
        self.to_address = to_address
        self.payment_type = payment_type
        self.transaction_hash = transaction_hash
        self.my_address = my_address

    @staticmethod
    def from_horizon_response(response_payment, my_address: str):
        transaction_hash = response_payment["transaction_hash"]
        created_at = response_payment["created_at"]
        payment_type = response_payment["type"]

        if payment_type == "create_account":
            return PaymentSummary(
                transaction_hash,
                Balance(response_payment["starting_balance"]),
                payment_type,
                created_at,
                response_payment["funder"],
                response_payment["account"],
                my_address,
            )

        if payment_type == "account_merge":
            return PaymentSummary(
                transaction_hash,
                None,
                payment_type,
                created_at,
                response_payment["account"],
                response_payment["into"],
                my_address,
            )

        balance = Balance(response_payment["amount"])
        if response_payment["asset_type"] != "native":
            balance.asset_code = response_payment["asset_code"]
            balance.asset_issuer = response_payment["asset_issuer"]
        return PaymentSummary(
            transaction_hash,
            balance,
            payment_type,
            created_at,
            response_payment["from"],
            response_payment["to"],
            my_address,
        )

    def __str__(self):
        if self.payment_type == "create_account":
            if self.to_address == self.my_address:
                representation = f"Account created with {self.balance} by {self.from_address}"
            else:
                representation = f"Created account {self.to_address} with {self.balance}"
        elif self.payment_type == "account_merge":
            representation = f"Account {self.from_address} merged"
        else:
            if self.to_address == self.my_address:
                representation = f"{self.balance} received from {self.from_address}"
            else:
                representation = f"{self.balance} sent to {self.to_address}"

        representation += f" at {self.created_at} tx: {self.transaction_hash}"
        return representation

    def __repr__(self):
        return str(self)
