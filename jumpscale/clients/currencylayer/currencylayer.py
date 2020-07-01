from pprint import pprint as print
import cryptocompare as cc
from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.loader import j
from .currencies import CURRENCIES, CURRNECIES_IDS
from pprint import pprint


def get_currency_data(api_key, fake=False, fakeonerror=False):
    if fake:
        return CURRENCIES
    else:
        url = "http://apilayer.net/api/live?access_key={}".format(api_key)
        r = j.tools.http.get(url)
        try:
            json_res = r.json()
            data = json_res["quotes"]

            data["USDETH"] = 1 / cc.get_price("ETH", "USD")["ETH"]["USD"]
            data["USDXRP"] = cc.get_price("USD", "XRP")["USD"]["XRP"]
            data["USDBTC"] = 1 / cc.get_price("BTC", "USD")["BTC"]["USD"]

            normalized_data = {k.lower().lstrip("usd"): v for k, v in data.items()}
            return normalized_data

        except Exception as e:
            print("error happened")
            if not fakeonerror:
                raise e
            else:
                return CURRENCIES


class CurrencyLayerClient(Client):

    name = fields.String()
    api_key = fields.String()
    fake = fields.Boolean(default=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = None

        self._data_cur = {}
        self._id2cur = {}
        self._cur2id = {}

    def load(self):
        # data = self._cache.get("currency_data", get, expire=3600 * 24)
        data = get_currency_data(self.api_key, fake=self.fake)
        self._data_cur = data

    @property
    def cur2usd(self):
        """
        e.g. AED = 3,672 means 3,6... times AED=1 USD
        """
        if not self._data_cur:
            self.load()
        return self._data_cur

    def cur2usd_print(self):
        print(self.cur2usd)

    @property
    def id2cur(self):
        if not self._id2cur:
            self._id2cur = CURRNECIES_IDS
        return self._id2cur

    @property
    def cur2id(self):
        if not self._cur2id:
            self._cur2id = dict(zip(self.id2cur.values(), self.id2cur.keys()))
        return self._cur2id

    def id2cur_print(self):
        pprint(self.id2cur)

    def cur2id_print(self):
        pprint(self.cur2id)

    def test(self):
        self._log_info(self.cur2usd)
        assert "aed" in self.cur2usd
