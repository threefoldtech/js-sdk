import requests
from jumpscale.loader import j
from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from collections import namedtuple

Price = namedtuple("Price", "ask bid last_trade")


class KrakenClient(Client):
    url = fields.String(default="https://api.kraken.com/")

    def __init__(self, *args, **kwargs):
        super().__init__(*args,)
        self._session = requests.Session()

    def _do_request(self, url, ex):
        res = self._session.get(url).json()
        if res["error"]:
            raise ex("\n".join(res["error"]))
        return res

    def get_pair_price(self, pair="XLMUSD"):
        """Gets price of specified pair

        Args:
            pair (str): pair name. Defaults to XLMUSD

        Raises:
            j.exceptions.Input: If incorrect pair is provided

        Returns:
            Price: Object containing ask, bid and last trade price
        """
        res = self._do_request(f"https://api.kraken.com/0/public/Ticker?pair={pair}", j.exceptions.Input)
        data = res["result"]
        prices = []
        key = list(data.keys())[0]
        for k in ["a", "b", "c"]:
            prices.append(data[key][k][0])
        return Price(*prices)
