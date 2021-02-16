from .base import BaseResource


class Prices(BaseResource):
    _resource = "prices"

    def calculate(self, cus=0, sus=0, ipv4us=0, farm_prices=None, tft_mill=100):
        explorer_prices = self.get_explorer_prices()
        farm_prices = farm_prices or explorer_prices
        tft_mill = explorer_prices["tft_mill"]

        price = cus * farm_prices["cu"] + sus * farm_prices["su"] + ipv4us * farm_prices["ipv4u"]
        return price / (30 * 24 * 60 * 60) * 1000 / tft_mill

    def get_explorer_prices(self):
        prices = self._session.get(self._url).json()
        return {
            "cu": prices["CuPriceDollarMonth"],
            "su": prices["SuPriceDollarMonth"],
            "ipv4u": prices["IP4uPriceDollarMonth"],
            "tft_mill": prices["TftPriceMill"],
        }
