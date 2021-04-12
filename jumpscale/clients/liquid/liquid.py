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

## Orders
Here we handle orders on liquid network. The token_id and token_secret should be passed in the client creation
```
client = j.clients.liquid.get("test_client",token_id=TOKEN_ID,token_secret=TOKEN_SECRET)
client.save()

JS-NG> client.create_order(order_type="limit",product_id=637,side="sell",quantity=12,price=50)
{'id': 4238991143, 'order_type': 'limit', 'quantity': '12.0', 'disc_quantity': '0.0', 'iceberg_total_quantity': '0.0', 'side': 'sell', 'filled_quantity': '0.0', 'price': 50.0, 'created_at': 1617896032, 'updated_at': 1617896032, 'status': 'live', 'leverage_level': 1, 'source_exchange': 'QUOINE', 'product_id': 637, 'margin_type': None, 'take_profit': None, 'stop_loss': None, 'trading_type': 'spot', 'product_code': 'CASH', 'funding_currency': 'BTC', 'crypto_account_id': None, 'currency_pair_code': 'TFTBTC', 'average_price': 0.0, 'target': 'spot', 'order_fee': 0.0, 'source_action': 'manual', 'unwound_trade_id': None, 'trade_id': None, 'client_order_id': None}

JS-NG> client.get_order(4238991143)
{'id': 4238991143, 'order_type': 'limit', 'quantity': '12.0', 'disc_quantity': '0.0', 'iceberg_total_quantity': '0.0', 'side': 'sell', 'filled_quantity': '0.0', 'price': 50.0, 'created_at': 1617896032, 'updated_at': 1617896032, 'status': 'live', 'leverage_level': 1, 'source_exchange': 'QUOINE', 'product_id': 637, 'margin_type': None, 'take_profit': None, 'stop_loss': None, 'trading_type': 'spot', 'product_code': 'CASH', 'funding_currency': 'BTC', 'crypto_account_id': None, 'currency_pair_code': 'TFTBTC', 'average_price': 0.0, 'target': 'spot', 'order_fee': '0.0', 'source_action': 'manual', 'unwound_trade_id': None, 'trade_id': None, 'client_order_id': None, 'settings': None, 'trailing_stop_type': None, 'trailing_stop_value': None, 'executions': [], 'stop_triggered_time': None}

JS-NG> client.get_orders()
{'models': [{'id': 4238991143, 'order_type': 'limit', 'quantity': '12.0', 'disc_quantity': '0.0', 'iceberg_total_quantity': '0.0', 'side': 'sell', 'filled_quantity': '0.0', 'price': '50.0', 'created_at': 1617896032, 'updated_at': 1617896032, 'status': 'live', 'leverage_level': 1, 'source_exchange': 0, 'product_id': 637, 'margin_type': None, 'take_profit': None, 'stop_loss': None, 'trading_type': 'spot', 'product_code': 'CASH', 'funding_currency': 'BTC', 'crypto_account_id': None, 'currency_pair_code': 'TFTBTC', 'average_price': '0.0', 'target': 'spot', 'order_fee': '0.0', 'source_action': 'manual', 'unwound_trade_id': None, 'trade_id': None, 'client_order_id': None}], 'total_pages': 1, 'current_page': 1}

JS-NG> client.get_balance()
[{'currency': 'USD', 'balance': '0.0'}, {'currency': 'TFT', 'balance': '13.0'}, {'currency': 'XLM', 'balance': '0.0'}, {'currency': 'ETH', 'balance': '0.0'}, {'currency': 'BTC', 'balance': '0.0'}]

JS-NG> client.edit_order(order_id=4238991143,price=40)
{'id': 4238991143, 'order_type': 'limit', 'quantity': '12.0', 'disc_quantity': '0.0', 'iceberg_total_quantity': '0.0', 'side': 'sell', 'filled_quantity': '0.0', 'price': 40.0, 'created_at': 1617896032, 'updated_at': 1617896342, 'status': 'live', 'leverage_level': 1, 'source_exchange': 'QUOINE', 'product_id': 637, 'margin_type': None, 'take_profit': None, 'stop_loss': None, 'trading_type': 'spot', 'product_code': 'CASH', 'funding_currency': 'BTC', 'crypto_account_id': None, 'currency_pair_code': 'TFTBTC', 'average_price': 0.0, 'target': 'spot', 'order_fee': 0.0, 'source_action': 'manual', 'unwound_trade_id': None, 'trade_id': None, 'client_order_id': None}

JS-NG> client.cancel_order(4238991143)
{'id': 4238991143, 'order_type': 'limit', 'quantity': '12.0', 'disc_quantity': '0.0', 'iceberg_total_quantity': '0.0', 'side': 'sell', 'filled_quantity': '0.0', 'price': 40.0, 'created_at': 1617896032, 'updated_at': 1617897424, 'status': 'cancelled', 'leverage_level': 1, 'source_exchange': 'QUOINE', 'product_id': 637, 'margin_type': None, 'take_profit': None, 'stop_loss': None, 'trading_type': 'spot', 'product_code': 'CASH', 'funding_currency': 'BTC', 'crypto_account_id': None, 'currency_pair_code': 'TFTBTC', 'average_price': 0.0, 'target': 'spot', 'order_fee': 0.0, 'source_action': 'manual', 'unwound_trade_id': None, 'trade_id': None, 'client_order_id': None}
```

"""

import requests
import jwt
from jumpscale.loader import j
from jumpscale.clients.base import Client, Base
from jumpscale.core.base import fields
from urllib.parse import urlencode


class Price(Base):
    pair = fields.String()
    ask = fields.Float()
    bid = fields.Float()


class LiquidClient(Client):
    _url = fields.String(default="https://api.liquid.com/")
    _price = fields.Object(Price)
    token_id = fields.String(default=None)
    token_secret = fields.Secret(default=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session = requests.Session()

    def _do_request(self, url, ex, headers=None, params=None, data=None, request_method="GET"):
        res = {}
        if headers:
            self._session.headers.update(headers)
        if request_method == "GET":
            res = self._session.get(url, headers=headers, params=params).json()
        elif request_method == "POST":
            res = self._session.post(url, headers=headers, json=data).json()
        elif request_method == "PUT":
            res = self._session.put(url, headers=headers, json=data).json()

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
            raise j.exceptions.Input("no result")
        result = result[0]
        data = {"pair": pair, "ask": result["market_ask"], "bid": result["market_bid"]}
        s = Price(**data)
        return s

    def do_authenticated_request(self, endpoint, data=None, params=None, request_method="GET"):

        path = f"{self._url}{endpoint}"
        if params:
            encoded_query = urlencode(params)
        payload = {
            "path": f"{path}?{encoded_query}" if params else path,
            "nonce": j.data.time.get().timestamp * 1000,  # time in milliseconds
            "token_id": self.token_id,
        }
        signature = jwt.encode(payload, self.token_secret, "HS256")
        request_headers = {"X-Quoine-API-Version": "2", "X-Quoine-Auth": signature, "Content-Type": "application/json"}
        return self._do_request(
            path, j.exceptions.Input, headers=request_headers, params=params, data=data, request_method=request_method
        )

    def create_order(
        self,
        order_type,
        side,
        quantity,
        product_id=637,
        price=None,
        trailing_stop_type=None,
        trailing_stop_value=None,
        trading_type=None,
        margin_type="cross",
        price_range=None,
        client_order_id=None,
        take_profit=None,
        stop_loss=None,
    ):
        """Create a new order

        Args:
            order_type (str) : type of order [limit, market, market_with_range, trailing_stop, limit_post_only, stop],
            product_id (int) : type of product, e.g 637 (TFTBTC)
            side (str) : supported side of order [buy,sell],
            quantity (str) : quantity to buy or sell,
            price (str) : price per unit of cryptocurrency ,
            trailing_stop_type (str) : Only available if order_type is trailing_stop.  [price, percentage]
            trailing_stop_value (str) : Only available if order_type is trailing_stop.The distance the order should trail the market price.,
            trading_type=None (str) : Only available if leverage_level is greater than 1. [margin, cfd, perpetual]
            margin_type=None (str) : Only available if leverage_level is greater than 1. [cross, isolated],
            price_range=None (str) : Only available if order_type is market_with_range,
            client_order_id=None (str) :Custom unique identifying JSON string ,
            take_profit=None (str) : Only available if leverage_level is greater than 1. Take profit will be executed as a limit order,
            stop_loss=None (str) : Only available if leverage_level is greater than 1. Stop loss will be executed as a market order,

        Raises:
            j.exceptions.Input: If invalid order type or side is provided.

        Returns:
            Order response: dict
        """
        if order_type and order_type not in [
            "limit",
            "market",
            "market_with_range",
            "trailing_stop",
            "limit_post_only",
            "stop",
        ]:
            raise j.exceptions.Input("Invalid order type")
        if side and side not in ["buy", "sell"]:
            raise j.exceptions.Input("Invalid supported side. Value should be buy or sell")

        data = {
            "order": {
                "order_type": order_type,
                "product_id": product_id,
                "side": side,
                "quantity": quantity,
                "price": price,
                "trailing_stop_type": trailing_stop_type,
                "trailing_stop_value": trailing_stop_value,
                "trading_type": trading_type,
                "margin_type": margin_type,
                "price_range": price_range,
                "client_order_id": client_order_id,
                "take_profit": take_profit,
                "stop_loss": stop_loss,
            }
        }
        return self.do_authenticated_request(endpoint="orders", request_method="POST", data=data)

    def get_order(self, order_id):
        """Get an existing order

        Args:
            order_id (str): id of order
        Returns:
            Order response: dict
        """
        endpoint = f"orders/{order_id}"
        return self.do_authenticated_request(endpoint=endpoint, request_method="GET")

    def get_order_trades(self, order_id):
        """Get an existing order's trades

        Args:
            order_id (str): id of order
        Returns:
            Order trades response: dict
        """
        endpoint = f"orders/{order_id}/trades"
        return self.do_authenticated_request(endpoint=endpoint, request_method="GET")

    def get_orders(
        self,
        funding_currency=None,
        product_id=None,
        status=None,
        trading_type=None,
        with_details=None,
        limit=None,
        page=None,
    ):
        params = {
            "funding_currency": funding_currency,
            "product_id": product_id,
            "status": status,
            "trading_type": trading_type,
            "with_details": with_details,
            "limit": limit,
            "page": page,
        }
        # remove None paramas
        for key, item in params.copy().items():
            if not item:
                params.pop(key)
        return self.do_authenticated_request(endpoint="orders", params=params, request_method="GET")

    def edit_order(
        self,
        order_id,
        order_type=None,
        product_id=637,
        side=None,
        quantity=None,
        price=None,
        trailing_stop_type=None,
        trailing_stop_value=None,
        trading_type=None,
        margin_type=None,
        price_range=None,
        client_order_id=None,
        take_profit=None,
        stop_loss=None,
    ):
        endpoint = f"orders/{order_id}"
        data = {
            "order": {
                "order_type": order_type,
                "product_id": product_id,
                "side": side,
                "quantity": quantity,
                "price": price,
                "trailing_stop_type": trailing_stop_type,
                "trailing_stop_value": trailing_stop_value,
                "trading_type": trading_type,
                "margin_type": margin_type,
                "price_range": price_range,
                "client_order_id": client_order_id,
                "take_profit": take_profit,
                "stop_loss": stop_loss,
            }
        }

        return self.do_authenticated_request(endpoint=endpoint, request_method="PUT", data=data)

    def cancel_order(self, order_id):
        endpoint = f"orders/{order_id}/cancel"
        return self.do_authenticated_request(endpoint=endpoint, request_method="PUT")

    def get_balance(self):
        return self.do_authenticated_request(endpoint="accounts/balance", request_method="GET")
