from .balance import Balance
import decimal


class TransactionSummary:
    def __init__(self, hash, memo_text=None, memo_hash=None, created_at=None):
        self.hash = hash
        self.memo_text = memo_text
        self.memo_hash = memo_hash
        self.created_at = created_at

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
