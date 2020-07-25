def export_module_as():
    from jumpscale.core.base import StoredFactory

    from .liquid import LiquidClient

    return StoredFactory(LiquidClient)
