def export_module_as():

    from jumpscale.core.base import StoredFactory

    from .racktivity import RackSal

    return StoredFactory(RackSal)
