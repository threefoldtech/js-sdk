def export_module_as():
    from jumpscale.core.base import StoredFactory
    from .redis import RedisServer

    return StoredFactory(RedisServer)
