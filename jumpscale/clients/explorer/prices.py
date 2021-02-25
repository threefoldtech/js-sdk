from .base import BaseResource


class Prices(BaseResource):
    _resource = "prices"

    def calculate(self, cus=0, sus=0, ipv4us=0, farm_prices=None, tft_mill=100):
        explorer_prices = self.get_explorer_prices()
        farm_prices = farm_prices or explorer_prices
        farm_prices = farm_prices.copy()
        tft_mill = explorer_prices["tft_mill"]
        # remove any discounts
        farm_prices["cu"] *= 100
        farm_prices["su"] *= 100
        farm_prices["ipv4u"] *= 100
        cu_stropes = int(farm_prices["cu"] * 10_000_000_000 / tft_mill / (30 * 24 * 60 * 60))
        su_stropes = int(farm_prices["su"] * 10_000_000_000 / tft_mill / (30 * 24 * 60 * 60))
        ipv4u_stropes = int(farm_prices["ipv4u"] * 10_000_000_000 / tft_mill / (30 * 24 * 60 * 60))
        price = cus * cu_stropes + sus * su_stropes + ipv4us * ipv4u_stropes
        # reapply the discount
        return (price / 100) / 1e7

    def get_explorer_prices(self):
        prices = self._session.get(self._url).json()
        return {
            "cu": prices["CuPriceDollarMonth"],
            "su": prices["SuPriceDollarMonth"],
            "ipv4u": prices["IP4uPriceDollarMonth"],
            "tft_mill": prices["TftPriceMill"],
        }
