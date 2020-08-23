from jumpscale.core.base import StoredFactory
from .client import HTTPClient

def export_module_as():

    return StoredFactory(HTTPClient)
