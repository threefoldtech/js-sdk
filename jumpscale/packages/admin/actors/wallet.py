import os
from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.clients.stellar.stellar import _NETWORK_KNOWN_TRUSTS


class Wallet(BaseActor):
    @actor_method
    def create_wallet(self, name: str) -> str:
        if j.clients.stellar.find(name):
            raise j.exceptions.Value(f"Wallet {name} already exists")

        wallet = j.clients.stellar.get(name=name)
        if os.environ.get("THREEBOT_WALLET_SECRET"):
            wallet.secret = os.environ.get("THREEBOT_WALLET_SECRET")
        wallet.save()
        return j.data.serializers.json.dumps({"data": wallet.address})

    @actor_method
    def get_wallet_info(self, name: str) -> str:
        if not j.clients.stellar.find(name):
            raise j.exceptions.Value("Wallet does not exist")

        wallet = j.clients.stellar.get(name=name)
        error = ""
        ret = {}
        try:
            balances = wallet.get_balance()
            balances_data = []
            for item in balances.balances:
                balances_data.append(
                    {"balance": item.balance, "asset_code": item.asset_code, "asset_issuer": item.asset_issuer}
                )

            ret = {
                "address": wallet.address,
                "network": wallet.network.value,
                "secret": wallet.secret,
                "balances": balances_data,
            }
        except Exception as e:
            error = str(e)
            j.logger.error(error)

        return j.data.serializers.json.dumps({"data": ret, "error": error})

    @actor_method
    def get_wallets(self) -> str:
        wallets = j.clients.stellar.list_all()
        ret = []
        for name in wallets:
            wallet = j.clients.stellar.get(name=name)
            ret.append({"name": wallet.instance_name, "address": wallet.address, "network": wallet.network.name})

        return j.data.serializers.json.dumps({"data": ret})

    @actor_method
    def update_trustlines(self, name: str) -> str:
        if not j.clients.stellar.find(name):
            raise j.exceptions.Value("Wallet does not exist")

        wallet = j.clients.stellar.get(name=name)
        trustlines = _NETWORK_KNOWN_TRUSTS[str(wallet.network.name)].copy()
        for balance in wallet.get_balance().balances:
            if balance.asset_code in trustlines:
                trustlines.pop(balance.asset_code)
        if "TFT" in trustlines.keys():
            wallet.add_known_trustline("TFT")

        wallet.save()
        return j.data.serializers.json.dumps({"data": trustlines})

    @actor_method
    def import_wallet(self, name: str, secret: str) -> str:
        if name in j.clients.stellar.list_all():
            return j.data.serializers.json.dumps({"error": "Wallet name already exists"})
        try:
            wallet = j.clients.stellar.new(name=name, secret=secret)
        except Exception as e:
            j.clients.stellar.delete(name)
            return j.data.serializers.json.dumps({"error": str(e)})
        try:
            wallet.get_balance()
        except:
            j.clients.stellar.delete(name)
            return j.data.serializers.json.dumps(
                {"error": "Import failed. Make sure wallet is activated on STD network."}
            )
        wallet.save()
        return j.data.serializers.json.dumps({"data": wallet.address})

    @actor_method
    def delete_wallet(self, name: str) -> str:
        j.clients.stellar.delete(name=name)
        return j.data.serializers.json.dumps({"data": True})


Actor = Wallet
