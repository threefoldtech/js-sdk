import requests

from jumpscale.loader import j
from jumpscale.core.base import StoredFactory
from stellar_sdk import Keypair
from .exceptions import *
from requests.exceptions import RequestException

TRANSACTION_FEES = 0.01

THREEFOLDFOUNDATION_TFTSTELLAR_SERVICES = {
    "TEST": "https://testnet.threefold.io/threefoldfoundation/transactionfunding_service/fund_transaction",
    "STD": "https://tokenservices.threefold.io/threefoldfoundation/transactionfunding_service/fund_transaction",
}

HORIZON_NETWORKS = {
    "TEST": "https://horizon-testnet.stellar.org",
    "STD": "https://horizon.stellar.org",
}

NETWORKS = HORIZON_NETWORKS.keys()


class StellarFactory(StoredFactory):
    def new(self, name, secret=None, *args, **kwargs):
        instance = super().new(name, *args, **kwargs)

        if not secret:
            key_pair = Keypair.random()
            instance.secret = key_pair.secret
        else:
            instance.secret = secret

        return instance

    def check_stellar_service(self, networks=NETWORKS):
        """This method will check if stellar and token service is up or not"""
        for newtwork in networks:
            stellar_url = HORIZON_NETWORKS[newtwork]
            tokenservices_url = THREEFOLDFOUNDATION_TFTSTELLAR_SERVICES[newtwork]

            # check stellar service
            try:
                j.tools.http.get(stellar_url)
            except RequestException:
                return False

            # check token services
            try:
                j.tools.http.options(tokenservices_url)
            except RequestException:
                return False

        return True

    def create_testnet_funded_wallet(self, name: str) -> bool:
        """This method will create a testnet wallet and fund it from the facuet

        Args:
            name (str): name of the wallet

        """
        wallet = self.new(name)
        try:
            wallet.network = "TEST"
            wallet.activate_through_friendbot()
            wallet.add_known_trustline("TFT")
            wallet.save()
        except Exception as e:
            self.delete(name)
            raise j.exceptions.Runtime(f"Failed to create the wallet due to token service")

        headers = {"Content-Type": "application/json"}
        url = "https://gettft.testnet.grid.tf/tft_faucet/api/transfer"
        data = {"destination": wallet.address}

        try:
            response = requests.post(url, json=data, headers=headers)
        except requests.exceptions.HTTPError:
            self.delete(name)
            raise j.exceptions.Runtime(
                f"Failed to fund wallet can't reach {url} due to connection error. Changes will be reverted."
            )

        if response.status_code != 200:
            self.delete(name)
            raise j.exceptions.Runtime(
                f"Failed to fund the wallet due to to facuet server error. Changes will be reverted."
            )

        j.logger.info("Wallet created successfully")
        return True


def export_module_as():

    from .stellar import Stellar

    return StellarFactory(Stellar)
