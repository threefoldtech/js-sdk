def export_module_as():
    from jumpscale.core.base import StoredFactory

    from .name import NameClient

    return StoredFactory(NameClient)
