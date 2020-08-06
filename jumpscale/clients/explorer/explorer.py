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
from .workloads import Workloads


class Explorer(Client):
    url = fields.String()

    def __init__(self, url=None, **kwargs):
        super().__init__(url=url, **kwargs)
        self._loaded_identity = identity.get_identity()
        self.__session = requests.Session()
        self.__session.hooks = dict(response=raise_for_status)

        secret = self._loaded_identity.nacl.signing_key.encode(Base64Encoder)
        auth = HTTPSignatureAuth(
            key_id=str(self._loaded_identity.tid), secret=secret, headers=["(created)", "date", "threebot-id"],
        )
        headers = {"threebot-id": str(self._loaded_identity.tid)}
        self.__session.auth = auth
        self.__session.headers.update(headers)

        self.nodes = Nodes(self)
        self.users = Users(self)
        self.farms = Farms(self)
        self.reservations = Reservations(self)
        self.gateway = Gateways(self)
        self.pools = Pools(self)
        self.workloads = Workloads(self)
        self.conversion = Conversion(self)

    @property
    def _session(self):
        me = identity.get_identity()
        if me.tid != self._loaded_identity.tid or me.explorer_url != self._loaded_identity.explorer_url:
            self._loaded_identity = me
            secret = self._loaded_identity.nacl.signing_key.encode(Base64Encoder)
            auth = HTTPSignatureAuth(
                key_id=str(self._loaded_identity.tid), secret=secret, headers=["(created)", "date", "threebot-id"],
            )
            headers = {"threebot-id": str(self._loaded_identity.tid)}
            self.__session.auth = auth
            self.__session.headers.update(headers)

        return self.__session
