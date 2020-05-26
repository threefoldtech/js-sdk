def export_module_as():
    from jumpscale.core.base import StoredFactory

    from .taiga import TaigaClient

    return StoredFactory(TaigaClient)
