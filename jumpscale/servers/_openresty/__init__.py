def export_module_as():
    from jumpscale.core.base import StoredFactory
    from .server import OpenRestyServer

    return StoredFactory(OpenRestyServer)
