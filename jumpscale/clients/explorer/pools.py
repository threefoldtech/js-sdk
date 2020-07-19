from .pagination import get_page, get_all
from .models import TfgridWorkloadsPool1, TfgridWorkloadsPoolCreate1, TfgridWorkloadsPoolCreated1
from jumpscale.loader import j


class Pools:
    def __init__(self, client):
        self._session = client._session
        self._client = client
        self._model = TfgridWorkloadsPool1
        self._model_create = TfgridWorkloadsPoolCreate1
        self._model_created = TfgridWorkloadsPoolCreated1

    @property
    def _base_url(self):
        return self._client.url + "/reservations/pools"

    def new(self):
        return self._model_create()

    def create(self, pool):
        resp = self._session.post(self._base_url, json=pool.to_dict())
        return self._model_created.from_dict(resp.json())

    def list(self, customer_tid=None, page=None):
        if page:
            tid = customer_tid if customer_tid else j.core.identity.me.tid
            url = self._base_url + f"/owner/{tid}"
            reservations, _ = get_page(self._session, page, self._model, url)
        else:
            reservations = list(self.iter(customer_tid))
        return reservations

    def iter(self, customer_tid=None):
        tid = customer_tid if customer_tid else j.core.identity.me.tid
        url = self._base_url + f"/owner/{tid}"
        yield from get_all(self._session, self._model, url)

    def get(self, pool_id):
        url = self._base_url + f"/{pool_id}"
        resp = self._session.get(url)
        return self._model.from_dict(resp.json())
