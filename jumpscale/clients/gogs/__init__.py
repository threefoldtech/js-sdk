def export_module_as():
    from jumpscale.core.base import StoredFactory
    from .gogs import Gogs

    return StoredFactory(Gogs)
