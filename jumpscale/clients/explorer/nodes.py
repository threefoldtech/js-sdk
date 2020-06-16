from .pagination import get_page, get_all
from .models import TfgridDirectoryNode2
from .base import BaseResource
from nacl.encoding import Base64Encoder
from .auth import HTTPSignatureAuth
from jumpscale.core.exceptions import Input
from jumpscale.core import identity


class Nodes(BaseResource):
    _resource = "nodes"

    def _query(self, farm_id=None, country=None, city=None, cru=None, sru=None, mru=None, hru=None, proofs=False):
        query = {}
        if proofs:
            query["proofs"] = "true"
        args = {
            "farm": farm_id,
            "city": city,
            "cru": cru,
            "sru": sru,
            "mru": mru,
            "hru": hru,
        }
        for k, v in args.items():
            if v is not None:
                query[k] = v
        return query

    def list(
        self, farm_id=None, country=None, city=None, cru=None, sru=None, mru=None, hru=None, proofs=False, page=None
    ):

        query = self._query(farm_id, country, city, cru, sru, mru, hru, proofs)
        if page:
            nodes, _ = get_page(self._session, page, TfgridDirectoryNode2, self._url, query)
        else:
            nodes = list(self.iter(farm_id, country, city, cru, sru, mru, hru, proofs))
        return nodes

    def iter(self, farm_id=None, country=None, city=None, cru=None, sru=None, mru=None, hru=None, proofs=False):
        query = self._query(farm_id, country, city, cru, sru, mru, hru, proofs)
        yield from get_all(self._session, TfgridDirectoryNode2, self._url, query)

    def get(self, node_id, proofs=False):
        params = {}
        if proofs:
            params["proofs"] = "true"
        resp = self._session.get(f"{self._url}/{node_id}", params=params)
        return TfgridDirectoryNode2.from_dict(resp.json())

    def configure_free_to_use(self, node_id, free):
        if not isinstance(free, bool):
            raise Input("free must be a boolean")

        me = identity.get_identity()
        secret = me.nacl.signing_key.encode(Base64Encoder)

        auth = HTTPSignatureAuth(key_id=str(me.tid), secret=secret, headers=["(created)", "date", "threebot-id"])
        headers = {"threebot-id": str(me.tid)}

        data = {"free_to_use": free}
        self._session.post(f"{self._url}/{node_id}/configure_free", auth=auth, headers=headers, json=data)
        return True

    def configure_public_config(self, node_id, master_iface, ipv4, gw4, ipv6, gw6):
        node = self.get(node_id)

        public_config = node.public_config
        public_config.master = master_iface
        public_config.ipv4 = ipv4
        public_config.gw4 = gw4
        public_config.ipv6 = ipv6
        public_config.gw6 = gw6
        public_config.type = "MACVLAN"
        public_config.version += 1

        me = identity.get_identity()
        secret = me.nacl.signing_key.encode(Base64Encoder)

        auth = HTTPSignatureAuth(key_id=str(me.tid), secret=secret, headers=["(created)", "date", "threebot-id"])
        headers = {"threebot-id": str(me.tid)}

        data = public_config.to_dict()
        self._session.post(f"{self._url}/{node_id}/configure_public", auth=auth, headers=headers, json=data)
        return True
