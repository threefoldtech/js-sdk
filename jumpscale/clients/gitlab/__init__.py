from .gitlab import Gitlab
from jumpscale.clients.base import ClientFactory


factory = ClientFactory(Gitlab)