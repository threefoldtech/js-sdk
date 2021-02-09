from jumpscale.data.time import now
from jumpscale.clients.explorer.models import Gateway
from typing import List


class GatewayFinder:
    """ """

    def __init__(self, identity):
        self._identity = identity
        explorer = self._identity.explorer
        self._gateway = explorer.gateway

    def filter_is_up(self, gw):
        """
        filter out gateways that have not received update for more then 10 minutes
        """
        ago = now().timestamp - (60 * 10)
        return gw.updated.timestamp() > ago

    def gateways_search(self, country: str = None, city: str = None) -> List[Gateway]:
        """search gateways by country and or city

        Args:
          country(str, optional): filter by country, defaults to None
          city(str, optional): filter by city, defaults to None
          country: str:  (Default value = None)
          city: str:  (Default value = None)

        Returns:
          List[Gateway]: List of Gateway

        """
        return self._gateway.list(country=country, city=city)
