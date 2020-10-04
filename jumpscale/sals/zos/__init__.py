__all__ = ["get", "clear_cache"]

INSTANCES = {}  # Dict[identityName, Zosv2Instance]


def get(identity_name=None):
    """Gets a Zosv2 instance for identity `identity_name`

    Args:
        identity_name ([str], optional): [identity name]. Defaults to None, if None then it returns a Zosv2 instance relative to the me identity

    Returns:
        (Zosv2) instance: Zosv2 instance based on indentity retrieved from `identity_name`
    """
    global INSTANCES, ME_INSTANCE
    from jumpscale.loader import j
    from .zos import Zosv2

    if not identity_name:
        if not j.core.identity.me:
            raise RuntimeError(
                "you need to configure j.core.identity.me if you don't pass identity_name using `j.core.identity.set_default`"
            )
        identity_name = j.core.identity.me.instance_name

    if identity_name not in INSTANCES:
        if identity_name not in j.core.identity.list_all():
            raise ValueError(f"Invalid identity_name {identity_name}")
        identity = j.core.identity.get(identity_name)
        res = Zosv2(identity)
        INSTANCES[identity_name] = res
        return res
    else:
        return INSTANCES[identity_name]


def clear_cache():
    """Clears cached instances of Zosv2"""
    global INSTANCES
    INSTANCES = {}
