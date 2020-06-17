import requests
from urllib.parse import urlparse

from .nodes import Nodes
from .users import Users
from .farms import Farms
from .reservations import Reservations
from .gateway import Gateway
from .errors import raise_for_status

from jumpscale.clients.base import Client
from jumpscale.core.base import fields


class Explorer(Client):
    url = fields.String()

    def __init__(self, url=None, **kwargs):
        super().__init__(url=url, **kwargs)
        self._session = requests.Session()
        self._session.hooks = dict(response=raise_for_status)

        self.nodes = Nodes(self)
        self.users = Users(self)
        self.farms = Farms(self)
        self.reservations = Reservations(self)
        self.gateway = Gateway(self)
