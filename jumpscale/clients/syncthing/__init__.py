def export_module_as():
    from jumpscale.core.base import StoredFactory

    from .syncthing import SyncthingClient

    return StoredFactory(SyncthingClient)
