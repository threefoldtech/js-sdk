def export_module_as():
    from jumpscale.core.base import StoredFactory
    from .restic import ResticRepo

    return StoredFactory(ResticRepo)
