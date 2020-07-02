def export_module_as():
    from jumpscale.core.base import StoredFactory

    from .kraken import KrakenClient

    return StoredFactory(KrakenClient)
