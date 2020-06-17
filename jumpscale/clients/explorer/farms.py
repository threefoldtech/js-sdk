from jumpscale.core.exceptions import Input, NotFound
from jumpscale.core import identity
from .pagination import get_page, get_all
from .models import TfgridDirectoryFarm1
from nacl.encoding import Base64Encoder
from .auth import HTTPSignatureAuth
from .base import BaseResource


class Farms(BaseResource):
    _resource = "farms"

    def list(self, threebot_id=None, name=None, page=None):
        query = {}
        if threebot_id:
            query["owner"] = threebot_id
        if name:
            query["name"] = name

        if page:
            farms, _ = get_page(self._session, page, TfgridDirectoryFarm1, self._url, query)
        else:
            farms = list(self.iter(threebot_id, name))

        return farms

    def iter(self, threebot_id=None, name=None):
        query = {}
        if threebot_id:
            query["owner"] = threebot_id
        if name:
            query["name"] = name
        yield from get_all(self._session, TfgridDirectoryFarm1, self._url, query)

    def new(self):
        return TfgridDirectoryFarm1()

    def register(self, farm):
        resp = self._session.post(self._url, json=farm._get_dict())
        return resp.json()["id"]

    def get(self, farm_id=None, farm_name=None):
        if farm_name:
            for farm in self.iter():
                if farm.name == farm_name:
                    return farm
            else:
                raise NotFound(f"Could not find farm with name {farm_name}")
        elif not farm_id:
            raise Input("farms.get requires atleast farm_id or farm_name")
        resp = self._session.get(f"{self._url}/{farm_id}")
        return TfgridDirectoryFarm1.from_dict(resp.json())

    def update(self, farm):
        me = identity.get_identity()
        secret = me.nacl.signing_key.encode(Base64Encoder)

        auth = HTTPSignatureAuth(key_id=str(me.tid), secret=secret, headers=["(created)", "date", "threebot-id"])
        headers = {"threebot-id": str(me.tid)}

        self._session.put(f"{self._url}/{farm.id}", auth=auth, headers=headers, json=farm._ddict)
        return True
