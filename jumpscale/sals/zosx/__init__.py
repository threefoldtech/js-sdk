def get_zos_for(identity_name):
    from jumpscale.loader import j
    from .zos import Zosv2

    return Zosv2(j.core.identity.get(identity_name))
