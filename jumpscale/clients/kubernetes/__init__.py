def export_module_as():
    from jumpscale.core.base import StoredFactory
    from .manager import Manager

    return StoredFactory(Manager)
