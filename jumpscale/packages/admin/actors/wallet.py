from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.clients.stellar.stellar import _NETWORK_KNOWN_TRUSTS


class Wallet(BaseActor):
    @actor_method
    def create_wallet(self, name: str) -> str:
        explorer = j.core.identity.me.explorer
        wallettype = "STD"
        if "testnet" in explorer.url or "devnet" in explorer.url:
            wallettype = "TEST"

        # Why while not if?
        while j.clients.stellar.find(name):
            raise j.exceptions.Value("Name already exists")
        wallet = j.clients.stellar.new(name=name, network=wallettype)

        try:
            if wallettype == "TEST":
                wallet.activate_through_friendbot()
            else:
                wallet.activate_through_threefold_service()
        except Exception:
            j.clients.stellar.delete(name=name)
            raise j.exceptions.JSException("Error on wallet activation")

        trustlines = _NETWORK_KNOWN_TRUSTS[str(wallet.network.name)].copy()
        for asset_code in trustlines.keys():
            wallet.add_known_trustline(asset_code)

        wallet.save()
        return j.data.serializers.json.dumps({"data": wallet.address})

    @actor_method
    def get_wallet_info(self, name: str) -> str:
        if not j.clients.stellar.find(name):
            raise j.exceptions.Value("Wallet does not exist")

        wallet = j.clients.stellar.get(name=name)
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
        return j.data.serializers.json.dumps({"data": ret})

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
        for asset_code in trustlines.keys():
            wallet.add_known_trustline(asset_code)

        wallet.save()
        return j.data.serializers.json.dumps({"data": trustlines})

    @actor_method
    def import_wallet(self, name: str, secret: str, network: str) -> str:
        if name in j.clients.stellar.list_all():
            return j.data.serializers.json.dumps({"error": "Wallet name already exists"})
        network = network or "TEST"
        try:
            wallet = j.clients.stellar.new(name=name, secret=secret, network=network)
        except Exception as e:
            j.clients.stellar.delete(name)
            return j.data.serializers.json.dumps({"error": str(e)})
        try:
            wallet.get_balance()
        except:
            j.clients.stellar.delete(name)
            return j.data.serializers.json.dumps(
                {"error": "Import failed.Make sure wallet is activated and network matches the wallet's network."}
            )
        wallet.save()
        return j.data.serializers.json.dumps({"data": wallet.address})

    @actor_method
    def delete_wallet(self, name: str) -> str:
        j.clients.stellar.delete(name=name)
        return j.data.serializers.json.dumps({"data": True})

    @actor_method
    def create_testnet_funded(self, name: str) -> str:
        j.clients.stellar.create_testnet_funded_wallet(name=name)
        return j.data.serializers.json.dumps({"data": True})


Actor = Wallet
