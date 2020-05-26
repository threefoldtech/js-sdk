def export_module_as():

    from jumpscale.core.base import StoredFactory

    from .digitalocean import DigitalOcean

    return StoredFactory(DigitalOcean)
