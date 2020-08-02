# some wrapped stellar_sdk objects to modify the behavior

import stellar_sdk
from stellar_sdk import Account as stellarAccount
from stellar_sdk import Server as stellarServer
import time
from .exceptions import NoTrustLine, TooLate, UnAuthorized


class Account(stellarAccount):
    def __init__(self, account_id: str, sequence: int, wallet) -> None:
        stellarAccount.__init__(self, account_id, sequence)
        self.wallet = wallet

    def increment_sequence_number(self):
        """
        Increments sequence number in this object by one.
        """
        stellarAccount.increment_sequence_number(self)
        self.wallet.sequence = self.sequence
        self.wallet.sequencedate = int(time.time())

    @property
    def last_created_sequence_is_used(self):
        return self.wallet.sequence <= self.sequence


class Server(stellarServer):
    def __init__(self, horizon_url):
        super().__init__(horizon_url)

    def submit_transaction(self, transaction_envelope):
        try:
            return super().submit_transaction(transaction_envelope)
        except stellar_sdk.exceptions.BadRequestError as e:
            if e.status == 400:
                resultcodes = e.extras["result_codes"]
                if resultcodes["transaction"] == "tx_too_late":
                    raise TooLate()
                if resultcodes["transaction"] == "tx_bad_auth":
                    raise UnAuthorized(e.extras["envelope_xdr"])
                if resultcodes["transaction"] == "tx_failed":
                    if "op_no_trust" in resultcodes["operations"]:
                        raise NoTrustLine()
                    if "op_bad_auth" in resultcodes["operations"]:
                        raise UnAuthorized(e.extras["envelope_xdr"])
            raise e
