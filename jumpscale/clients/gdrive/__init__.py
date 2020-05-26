def export_module_as():
    from jumpscale.core.base import StoredFactory

    from .gdrive import GdriveClient

    return StoredFactory(GdriveClient)
