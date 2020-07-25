# some wrapped stellar_sdk objects to modify the behavior  

from stellar_sdk import Account as stellarAccount
import time

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
