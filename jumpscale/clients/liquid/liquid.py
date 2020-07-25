"""Liquid client is a growing client support liquid.com API

## Getting liquid client

Liquid client is available from `j.clients.liquid` ```
JS-NG> 1 = j.clients.liquid.get("l1")
```                                                                                

## Getting a pair price

Here we try to get the value of `TFTBTC` (it's the default as well.)
```
JS-NG> p1 = k1.get_pair_price()                                                                                       
JS-NG> p1.last_trade                                                                                                  
'0.06943500'

JS-NG> p1.bid                                                                                                         
'0.06930000'

JS-NG> p1.ask                                                                                                         
'0.06943500'
```


"""

import requests
from jumpscale.loader import j
from jumpscale.clients.base import Client, Base
from jumpscale.core.base import fields


class Price(Base):
    pair = fields.String()
    ask = fields.Float()
    bid = fields.Float()


class LiquidClient(Client):
    _url = fields.String(default="https://api.liquid.com/")
    _price = fields.Object(Price)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session = requests.Session()

    def _do_request(self, url, ex):
        res = self._session.get(url).json()
        return res

    def get_pair_price(self, pair="TFTBTC"):
        """Gets price of specified pair

        Args:
            pair (str): pair name. Defaults to TFTBTC

        Raises:
            j.exceptions.Input: If incorrect pair is provided

        Returns:
            Price: Object containing ask, bid and last trade price
        """
        res = self._do_request(f"{self._url}/products", j.exceptions.Input)
        result = [p for p in res if p["product_type"] == "CurrencyPair" and p["currency_pair_code"] == pair]
        if not result:
            raise j.exceptions.Input()
        result = result[0]
        data = {
            "pair": pair,
            "ask": result["market_ask"],
            "bid": result["market_bid"],
        }
        s = Price(**data)
        return s
