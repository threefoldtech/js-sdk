def export_module_as():
    from jumpscale.core.base import StoredFactory
    from .servicemanager import ServiceManager

    return StoredFactory(ServiceManager)
