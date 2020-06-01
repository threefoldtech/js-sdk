from jumpscale.core.base import StoredFactory
from stellar_sdk import Keypair


class StellarFactory(StoredFactory):
    def new(self, name, secret=None, *args, **kwargs):
        instance = super().new(name, *args, **kwargs)

        if not secret:
            key_pair = Keypair.random()
            instance.secret = key_pair.secret
        else:
            instance.secret = secret

        return instance


def export_module_as():

    from .stellar import Stellar

    return StellarFactory(Stellar)
