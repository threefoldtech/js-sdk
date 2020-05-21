from jumpscale.core.base import StoredFactory

def export_module_as():
    from .threebot import ThreebotServer
    return StoredFactory(ThreebotServer)
    
