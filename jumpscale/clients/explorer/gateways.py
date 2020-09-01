from .base import BaseResource
from .models import Gateway
from .pagination import get_all, get_page
from typing import List, Iterator


def _build_query(
    farm_id: int = None,
    country: str = None,
    city: str = None,
    cru: int = None,
    sru: int = None,
    mru: int = None,
    hru: int = None,
) -> dict:
    query = {}
    args = {
        "farm_id": farm_id,
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


class Gateways(BaseResource):
    _resource = "gateways"

    def list(
        self, farm_id=None, country=None, city=None, cru=None, sru=None, mru=None, hru=None, page=None
    ) -> List[Gateway]:
        """
        List all network gateways

        :param farm_id: filter by farm_id,
        :type farm_id: int, optional
        :param country: filter by country,
        :type country: str, optional
        :param city: filter by city,
        :type city: str, optional
        :param cru: filter by cru,
        :type cru: int, optional
        :param sru: filter by sru,
        :type sru: int, optional
        :param mru: filter by mru,
        :type mru: int, optional
        :param hru: filter by hru,
        :type hru: int, optional
        :return: list of Gateway
        :rtype: list
        """
        query = _build_query(farm_id=farm_id, country=country, city=city, cru=cru, sru=sru, mru=mru, hru=hru)
        if page:
            nodes, _ = get_page(self._session, page, Gateway, self._url, query)
        else:
            nodes = list(self.iter(farm_id, country, city, cru, sru, mru, hru))

        return nodes

    def iter(self, farm_id=None, country=None, city=None, cru=None, sru=None, mru=None, hru=None) -> Iterator[Gateway]:
        """
        returns an Iterator that yields gateways

         :param farm_id: filter by farm_id,
        :type farm_id: int, optional
        :param country: filter by country,
        :type country: str, optional
        :param city: filter by city,
        :type city: str, optional
        :param cru: filter by cru,
        :type cru: int, optional
        :param sru: filter by sru,
        :type sru: int, optional
        :param mru: filter by mru,
        :type mru: int, optional
        :param hru: filter by hru,
        :type hru: int, optional
        :yield: Iterator yielding Gateway
        :rtype: Iterator[Gateway]
        """
        query = _build_query(farm_id=farm_id, country=country, city=city, cru=cru, sru=sru, mru=mru, hru=hru)
        yield from get_all(self._session, Gateway, self._url, query)

    def get(self, node_id) -> Gateway:
        """
        get a specify gateway

        :param node_id: gateway ID
        :type node_id: str
        :return: Gateway
        :rtype: Gateway
        """
        params = {}
        resp = self._session.get(f"{self._url}/{node_id}", params=params)
        return Gateway.from_dict(resp.json())
