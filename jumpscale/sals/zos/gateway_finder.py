from jumpscale.data.time import now
from jumpscale.clients.explorer.models import Gateway
from typing import List


class GatewayFinder:
    def __init__(self, explorer):
        self._gateway = explorer.gateway

    def filter_is_up(self, gw):
        """
        filter out gateways that have not received update for more then 10 minutes
        """
        ago = now().timestamp - (60 * 10)
        return gw.updated > ago

    def gateways_search(self, country: str = None, city: str = None) -> List[Gateway]:
        """
        search gateways by country and or city

        :param country: filter by country, defaults to None
        :type country: str, optional
        :param city: filter by city, defaults to None
        :type city: str, optional
        :return: List of Gateway
        :rtype: List[Gateway]
        """
        return self._gateway.list(country=country, city=city)
