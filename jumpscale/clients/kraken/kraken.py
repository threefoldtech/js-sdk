"""Kraken client is a growing client support kraken.com API

## Getting kraken clientn

Kraken client is available from `j.clients.kraken`
```
JS-NG> k1 = j.clients.kraken.get("k1")
```                                                                                

## Getting a pair price

Here we try to get the value of `XLMUSD` (it's the default as well.)
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
    ask = fields.String()
    bid = fields.String()
    last_trade = fields.String()
    stored_date = fields.DateTime()


class KrakenClient(Client):

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
        return Price(**data)
