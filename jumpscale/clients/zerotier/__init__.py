def export_module_as():
    from jumpscale.core.base import StoredFactory

    from .zerotier import ZerotierClient

    return StoredFactory(ZerotierClient)
