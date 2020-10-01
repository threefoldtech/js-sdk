__all__ = ["get_zos_for"]

INSTANCES = {}
ME_INSTANCE = None


def get_zos_for(identity_name=None):
    global INSTANCES, ME_INSTANCE
    from jumpscale.loader import j
    from .zos import Zosv2

    if identity_name:
        if identity_name not in INSTANCES:
            identity = j.core.identity.get(identity_name)
            res = Zosv2(identity)
            INSTANCES[identity_name] = res
            return res
        else:
            return INSTANCES[identity_name]
    else:
        if ME_INSTANCE:
            return ME_INSTANCE
        else:
            identity = j.core.identity.me
            ME_INSTANCE = Zosv2(identity)
            return ME_INSTANCE
