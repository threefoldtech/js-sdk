from .pagination import get_all, get_page
from .models import TfgridDirectoryGateway1
from .base import BaseResource


class Gateway(BaseResource):
    _resource = "gateways"

    def _query(self, farm_id=None, country=None, city=None, cru=None, sru=None, mru=None, hru=None):
        query = {}
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

    def list(self, farm_id=None, country=None, city=None, cru=None, sru=None, mru=None, hru=None, page=None):

        query = self._query(farm_id, country, city, cru, sru, mru, hru)
        if page:
            nodes, _ = get_page(self._session, page, TfgridDirectoryGateway1, self._url, query)
        else:
            nodes = list(self.iter(farm_id, country, city, cru, sru, mru, hru))

        return nodes

    def iter(self, farm_id=None, country=None, city=None, cru=None, sru=None, mru=None, hru=None):
        query = self._query(farm_id, country, city, cru, sru, mru, hru)
        yield from get_all(self._session, TfgridDirectoryGateway1, self._url, query)

    def get(self, node_id):
        params = {}
        resp = self._session.get(f"{self._url}/{node_id}", params=params)
        return TfgridDirectoryGateway1.from_dict(resp.json())
