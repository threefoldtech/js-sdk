from decimal import Decimal
from typing import List

from stellar_sdk.exceptions import BadRequestError

from jumpscale.clients.explorer.models import PaymentDetail
from jumpscale.clients.stellar.stellar import Stellar

# TFT_ISSUER on production
TFT_ISSUER_PROD = "GBOVQKJYHXRR3DX6NOX2RRYFRCUMSADGDESTDNBDS6CDVLGVESRTAC47"
# TFT_ISSUER on testnet
TFT_ISSUER_TEST = "GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3"
ASSET_CODE = "TFT"


class InsufficientFunds(Exception):
    pass


class MissingTrustLine(Exception):
    pass


class Billing:
    def payout_farmers(self, wallet: Stellar, reservation_response: PaymentDetail) -> List[str]:
        """payout farmer based on the resources per node used

        Args:
          client(j.clients.stellar): stellar wallet client
          reservation_response(tfgrid.workloads.reservation.create.1): reservation create response

        Returns:
            the list of transaction hash created on stellar
        """
        total_amount = reservation_response.escrow_information.amount
        if total_amount <= 0:
            return []  # nothing to pay,early return

        reservation_id = reservation_response.reservation_id
        asset = reservation_response.escrow_information.asset
        escrow_address = reservation_response.escrow_information.address

        total_amount_dec = Decimal(total_amount) / Decimal(1e7)
        total_amount = "{0:f}".format(total_amount_dec)

        for balance in wallet.get_balance().balances:
            if f"{balance.asset_code}:{balance.asset_issuer}" == asset:
                if total_amount_dec > Decimal(balance.balance):
                    raise InsufficientFunds(
                        f"Wallet {wallet.instance_name} does not have enough funds to pay for {total_amount_dec:0f} {asset}"
                    )
                break
        else:
            raise MissingTrustLine(f"Wallet {wallet.instance_name} does not have a valid trustline to pay for {asset}")

        transaction_hashes = []
        try:
            txhash = wallet.transfer(escrow_address, total_amount, asset=asset, memo_text=f"p-{reservation_id}")
            transaction_hashes.append(txhash)
        except BadRequestError as e:
            raise e

        return transaction_hashes
