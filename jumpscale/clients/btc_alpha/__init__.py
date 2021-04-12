def export_module_as():
    from jumpscale.core.base import StoredFactory

    from .btc_alpha import BTCAlpha

    return StoredFactory(BTCAlpha)
