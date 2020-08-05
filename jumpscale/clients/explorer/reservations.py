from urllib.parse import urlparse, urlunparse

from jumpscale.core.exceptions import Input
from jumpscale.data.serializers.json import dumps
from jumpscale.data.time import now

from .base import BaseResource
from .models import NextAction, PaymentDetail, Reservation
from .pagination import get_all, get_page

from typing import List, Iterator


def _next_action(next_action):
    if next_action:
        if isinstance(next_action, str):
            next_action = getattr(NextAction, next_action.upper()).value
        if not isinstance(next_action, int):
            raise Input("next_action should be of type int")
    return next_action


def _build_query(customer_tid: int = None, next_action: NextAction = None,) -> dict:
    query = {}
    if customer_tid:
        query["customer_tid"] = customer_tid
    if next_action:
        query["next_action"] = _next_action(next_action)
    return query


class Reservations(BaseResource):
    _resource = "reservations"

    @property
    def _base_url(self):
        # we fallback on the legacy endpoint of the API
        # cause they are only endpoints for reservation there
        url_parts = list(urlparse(self._client.url))
        url_parts[2] = "/explorer/reservations"
        return urlunparse(url_parts)

    def list(self, customer_tid: int = None, next_action: str = None, page: int = None) -> List[Reservation]:
        """
        List legacy reservations

        :param customer_tid: filter by cutsomter ID, defaults to None
        :type customer_tid: int, optional
        :param next_action: filter by next_action value, defaults to None
        :type next_action: str, optional
        :return: list of Reservation
        :rtype: list
        """
        if page:
            query = _build_query(customer_tid=customer_tid, next_action=next_action)
            reservations, _ = get_page(self._session, page, Reservation, self._base_url, query)
        else:
            reservations = list(self.iter(customer_tid, next_action))
        return reservations

    def iter(self, customer_tid=None, next_action=None,) -> Iterator[Reservation]:
        """
        returns an Iterator that yields legacy reservations

        :param customer_tid: filter by cutsomter ID, defaults to None
        :type customer_tid: int, optional
        :param next_action: filter by next_action value, defaults to None
        :type next_action: str, optional
        :yield: [description]
        :rtype: Iterator[Reservation]
        """
        query = _build_query(customer_tid=customer_tid, next_action=next_action)
        yield from get_all(self._session, Reservation, self._base_url, query)

    def get(self, reservation_id: int) -> Reservation:
        """
        get a reservation

        :param reservation_id: reservation ID
        :type reservation_id: int
        :return: Reservation
        :rtype: Reservation
        """
        url = f"{self._base_url}/{reservation_id}"
        resp = self._session.get(url)
        return Reservation.from_dict(resp.json())
