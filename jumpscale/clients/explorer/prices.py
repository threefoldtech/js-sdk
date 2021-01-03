from .base import BaseResource


class Prices(BaseResource):
    _resource = "prices"

    def _get(self, cus=0, sus=0, ipv4us=0):
        response = self._session.get(self._url)
        prices_dict = response.json()
        price = (
            cus * prices_dict["CuPriceDollarMonth"]
            + sus * prices_dict["SuPriceDollarMonth"]
            + ipv4us * prices_dict["IP4uPriceDollarMonth"]
        )
        return price / (30 * 24 * 60 * 60), prices_dict["TftPriceMill"]

    def calculate(self, cus=0, sus=0, ipv4us=0):
        price, tft_mill = self._get(cus, sus, ipv4us)
        return price * 1000 / tft_mill
