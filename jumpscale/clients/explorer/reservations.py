from jumpscale.data.time import now
from jumpscale.data.serializers.json import dumps
from .pagination import get_page, get_all
from .base import BaseResource
from .models import TfgridWorkloadsReservation1, TfgridWorkloadsReservationCreate1
from jumpscale.core.exceptions import Input


class Reservations(BaseResource):
    _resource = "reservations"

    def new(self):
        return TfgridWorkloadsReservation1()

    def create(self, reservation):
        resp = self._session.post(self._url, json=reservation.to_dict())
        return TfgridWorkloadsReservationCreate1.from_dict(resp.json())

    def list(self, customer_tid=None, next_action=None, page=None):
        if page:
            query = {}
            if customer_tid:
                query["customer_tid"] = customer_tid
            if next_action:
                query["next_action"] = self._next_action(next_action)
            reservations, _ = get_page(self._session, page, TfgridWorkloadsReservation1, self._url, query)
        else:
            reservations = list(self.iter(customer_tid, next_action))
        return reservations

    def _next_action(self, next_action):
        if next_action:
            if isinstance(next_action, str):
                next_action = getattr(self.new().next_action, next_action.upper()).value
            if not isinstance(next_action, int):
                raise Input("next_action should be of type int")
        return next_action

    def iter(
        self, customer_tid=None, next_action=None,
    ):
        query = {}
        if customer_tid:
            query["customer_tid"] = customer_tid
        if next_action:
            query["next_action"] = self._next_action(next_action)
        yield from get_all(self._session, TfgridWorkloadsReservation1, self._url, query)

    def get(self, reservation_id):
        url = f"{self._url}/{reservation_id}"
        resp = self._session.get(url)
        return TfgridWorkloadsReservation1.from_dict(resp.json())

    def sign_provision(self, reservation_id, tid, signature):
        url = f"{self._url}/{reservation_id}/sign/provision"
        data = dumps({"signature": signature, "tid": tid, "epoch": now().timestamp})
        self._session.post(url, data=data)
        return True

    def sign_delete(self, reservation_id, tid, signature):
        url = f"{self._url}/{reservation_id}/sign/delete"
        data = dumps({"signature": signature, "tid": tid, "epoch": now().timestamp})
        self._session.post(url, data=data)
        return True
