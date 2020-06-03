def export_module_as():
    from jumpscale.core.base import StoredFactory
    from .nginxserver import NginxServer

    return StoredFactory(NginxServer)
