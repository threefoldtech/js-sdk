from jumpscale.loader import j
from jumpscale.core.base import StoredFactory
from stellar_sdk import Keypair
from .exceptions import *


class StellarFactory(StoredFactory):
    def new(self, name, secret=None, *args, **kwargs):
        instance = super().new(name, *args, **kwargs)

        if not secret:
            key_pair = Keypair.random()
            instance.secret = key_pair.secret
        else:
            instance.secret = secret

        return instance

    def check_stellar_service(self):
        """This method will check if stellar and token service is up or not
        """
        _THREEFOLDFOUNDATION_TFTSTELLAR_SERVICES = {
            "TEST": "https://testnet.threefold.io/threefoldfoundation/transactionfunding_service/fund_transaction",
            "STD": "https://tokenservices.threefold.io/threefoldfoundation/transactionfunding_service/fund_transaction",
        }
        _HORIZON_NETWORKS = {"TEST": "https://horizon-testnet.stellar.org", "STD": "https://horizon.stellar.org"}

        services_status = True

        # urls of services according to identity explorer
        if "testnet" in j.core.identity.me.explorer_url:
            stellar_url = _HORIZON_NETWORKS["TEST"]
            tokenservices_url = _THREEFOLDFOUNDATION_TFTSTELLAR_SERVICES["TEST"]
        else:
            stellar_url = _HORIZON_NETWORKS["STD"]
            tokenservices_url = _THREEFOLDFOUNDATION_TFTSTELLAR_SERVICES["STD"]

        # check stellar service
        try:
            j.tools.http.get(stellar_url)
        except:
            services_status = False

        # check token services
        try:
            j.tools.http.get(tokenservices_url)
        except:
            services_status = False

        return services_status

def export_module_as():

    from .stellar import Stellar

    return StellarFactory(Stellar)
