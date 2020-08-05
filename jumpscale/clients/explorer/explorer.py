from urllib.parse import urlparse

import requests
from nacl.encoding import Base64Encoder

from jumpscale.clients.base import Client
from jumpscale.core import identity
from jumpscale.core.base import fields

from .auth import HTTPSignatureAuth
from .conversion import Conversion
from .errors import raise_for_status
from .farms import Farms
from .gateways import Gateways
from .nodes import Nodes
from .pools import Pools
from .reservations import Reservations
from .users import Users
from .workloads import Workoads


class Explorer(Client):
    url = fields.String()

    def __init__(self, url=None, **kwargs):
        super().__init__(url=url, **kwargs)

        me = identity.get_identity()
        secret = me.nacl.signing_key.encode(Base64Encoder)

        auth = HTTPSignatureAuth(key_id=str(me.tid), secret=secret, headers=["(created)", "date", "threebot-id"],)
        headers = {"threebot-id": str(me.tid)}

        self._session = requests.Session()
        self._session.auth = auth
        self._session.headers.update(headers)
        self._session.hooks = dict(response=raise_for_status)

        self.nodes = Nodes(self)
        self.users = Users(self)
        self.farms = Farms(self)
        self.reservations = Reservations(self)
        self.gateway = Gateways(self)
        self.pools = Pools(self)
        self.workloads = Workoads(self)
        self.conversion = Conversion(self)
