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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url = kwargs['url']

        self._session = requests.Session()
        self._session.hooks = dict(response=raise_for_status)

        self.nodes = Nodes(self._session, self.url)
        self.users = Users(self._session, self.url)
        self.farms = Farms(self._session, self.url)
        self.reservations = Reservations(self._session, self.url)
        self.gateway = Gateway(self._session, self.url)
