from .gitlab import Gitlab
from jumpscale.clients.base import ClientFactory


export_module_as = ClientFactory(Gitlab)