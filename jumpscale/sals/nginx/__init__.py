def export_module_as():
    from jumpscale.core.base import Factory
    from .nginx import NginxConfig

    return Factory(NginxConfig)
