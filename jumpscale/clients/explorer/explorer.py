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
from .users import Users
from .workloads import Workloads
from .prices import Prices

from jumpscale.loader import j


def log_request(r, *args, **kwargs):
    if j.config.get("EXPLORER_LOGS"):
        j.logger.debug(
            f"Request {r.request.url} method: {r.request.method} body: {r.request.body} headers: {r.request.headers}"
        )


class Explorer(Client):
    url = fields.String()
    identity_name = fields.String()

    def __init__(self, url=None, identity_name=None, **kwargs):
        super().__init__(url=url, identity_name=identity_name, **kwargs)
        if identity_name:
            self._loaded_identity = identity.export_module_as().get(identity_name)
        else:
            self._loaded_identity = identity.get_identity()
        self._session = requests.Session()
        self._session.hooks = dict(response=[log_request, raise_for_status])

        secret = self._loaded_identity.nacl.signing_key.encode(Base64Encoder)
        auth = HTTPSignatureAuth(
            key_id=str(self._loaded_identity.tid), secret=secret, headers=["(created)", "date", "threebot-id"],
        )
        headers = {"threebot-id": str(self._loaded_identity.tid)}
        self._session.auth = auth
        self._session.headers.update(headers)

        self.nodes = Nodes(self)
        self.users = Users(self)
        self.farms = Farms(self)
        self.gateway = Gateways(self)
        self.pools = Pools(self)
        self.workloads = Workloads(self)
        self.conversion = Conversion(self)
        self.prices = Prices(self)
