import requests
from jumpscale.loader import j
from jumpscale.clients.base import Client, Base
from jumpscale.core.base import fields


class Price(Base):
    pair = fields.String()
    ask = fields.String()
    bid = fields.String()
    last_trade = fields.String()
    stored_date = fields.DateTime()


class KrakenClient(Client):
    url = fields.String(default="https://api.kraken.com/")
    _price = fields.Object(Price)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        if self._price.pair != pair or (j.data.time.utcnow().datetime - self._price.stored_date).days > 0:
            res = self._do_request(f"https://api.kraken.com/0/public/Ticker?pair={pair}", j.exceptions.Input)
            result = res["result"]
            key = list(result.keys())[0]
            data = {
                "pair": pair,
                "ask": result[key]["a"][0],
                "bid": result[key]["b"][0],
                "last_trade": result[key]["c"][0],
                "stored_date": j.data.time.utcnow().datetime,
            }
            self._price = Price(**data)
        return self._price
