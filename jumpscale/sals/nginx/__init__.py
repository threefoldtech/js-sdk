def export_module_as():
    from jumpscale.core.base import StoredFactory
    from .nginx import NginxConfig

    return StoredFactory(NginxConfig)
