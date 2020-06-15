from jumpscale.data.time import now


class GatewayFinder:
    def __init__(self, explorer):
        self._gateway = explorer.gateway

    def filter_is_up(self, gw):
        """
        filter out gateways that have not received update for more then 10 minutes
        """
        ago = now().timestamp - (60 * 10)
        return gw.updated > ago

    def gateways_search(self, country=None, city=None):
        return self._gateway.list(country=country, city=city)
