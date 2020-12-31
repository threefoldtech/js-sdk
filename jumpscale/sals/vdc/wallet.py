from jumpscale.clients.stellar.stellar import Network as StellarNetwork
from jumpscale.core.base import Base, StoredFactory, fields
from jumpscale.loader import j

INIT_WALLET_NAME = j.core.config.get("VDC_INIT", "vdc_init")


class VDCWallet(Base):
    vdc_uuid = fields.String()
    wallet_secret = fields.String()
    wallet_network = fields.Enum(StellarNetwork)

    def _init_wallet(self, secret=None):
        wallet = j.clients.stellar.find(INIT_WALLET_NAME)
        if not wallet:
            wallet = j.clients.stellar.new(self.instance_name, secret=secret)
            if not secret:
                wallet.activate_through_threefold_service()
                wallet.add_known_trustline("TFT")
            wallet.save()
        self.wallet_secret = wallet.secret

    @property
    def stellar_wallet(self):
        wallet = j.clients.stellar.find(INIT_WALLET_NAME)
        if not wallet:
            if not j.clients.stellar.find(self.instance_name) and self.wallet_secret:
                self._init_wallet(self.wallet_secret)
            return j.clients.stellar.get(self.instance_name)
        return wallet


class VDCWalletStoredFactory(StoredFactory):
    def new(self, *args, **kwargs):
        instance = super().new(*args, **kwargs)
        instance._init_wallet()
        instance.save()
        return instance


VDC_WALLET_FACTORY = VDCWalletStoredFactory(VDCWallet)
VDC_WALLET_FACTORY.always_reload = True
