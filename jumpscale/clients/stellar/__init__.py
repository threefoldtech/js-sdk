from jumpscale.core.base import StoredFactory
from stellar_sdk import Keypair


class StellarFactory(StoredFactory):
    def new(self, name, *args, **kwargs):
        instance = super().new(name, *args, **kwargs)
        key_pair = Keypair.random()
        instance.address = key_pair.public_key
        instance.secret = key_pair.secret
        instance.save()
        return instance


def export_module_as():

    from .stellar import Stellar

    return StellarFactory(Stellar)
