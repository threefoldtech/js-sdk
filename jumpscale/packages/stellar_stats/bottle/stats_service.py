#!/usr/bin/env python
# pylint: disable=no-value-for-parameter

from jumpscale.loader import j
import click
import stellar_sdk
import datetime

from urllib import parse


_ASSET_ISUERS = {
    "test": {
        "TFT": "GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3",
        "FreeTFT": "GBLDUINEFYTF7XEE7YNWA3JQS4K2VD37YU7I2YAE7R5AHZDKQXSS2J6R",
        "TFTA": "GB55A4RR4G2MIORJTQA4L6FENZU7K4W7ATGY6YOT2CW47M5SZYGYKSCT",
    },
    "public": {
        "TFT": "GBOVQKJYHXRR3DX6NOX2RRYFRCUMSADGDESTDNBDS6CDVLGVESRTAC47",
        "FreeTFT": "GCBGS5TFE2BPPUVY55ZPEMWWGR6CLQ7T6P46SOFGHXEBJ34MSP6HVEUT",
        "TFTA": "GBUT4GP5GJ6B3XW5PXENHQA7TXJI5GOPW3NF4W3ZIW6OOO4ISY6WNLN2",
    },
}
_HORIZON_NETWORKS = {"test": "https://horizon-testnet.stellar.org", "public": "https://horizon.stellar.org"}
_THREEFOLDFOUNDATION_TFTSTELLAR_SERVICES = {"test": "testnet.threefold.io", "public": "tokenservices.threefold.io"}

_NETWORK_PASSPHRASES = {
    "test": stellar_sdk.Network.TESTNET_NETWORK_PASSPHRASE,
    "public": stellar_sdk.Network.PUBLIC_NETWORK_PASSPHRASE,
}


class StatisticsCollector(object):
    """
    Gathers statistics on TFT, TFTA and FreeTFT.
    Reuse an instance of this class to cache the locktimes of escrow accounts and speed up the detailed statistics gathering
    """

    def __init__(self, network: str):
        self._network = network
        self.locked_accounts = {}

    @property
    def _horizon_server(self):
        server_url = _HORIZON_NETWORKS[self._network]
        return stellar_sdk.Server(horizon_url=server_url)

    @property
    def _network_passphrase(self):
        return _NETWORK_PASSPHRASES[self._network]

    def get_accounts(self, tokencode: str, issuer: str):
        locked_accounts = []
        horizon_server = self._horizon_server
        asset = stellar_sdk.Asset(tokencode, issuer)
        accounts_endpoint = horizon_server.accounts().for_asset(asset).limit(50)
        old_cursor = "old"
        new_cursor = ""
        while new_cursor != old_cursor:
            old_cursor = new_cursor
            accounts_endpoint.cursor(new_cursor)
            response = accounts_endpoint.call()
            next_link = response["_links"]["next"]["href"]
            next_link_query = parse.urlsplit(next_link).query
            new_cursor = parse.parse_qs(next_link_query)["cursor"][0]
            accounts = response["_embedded"]["records"]
            for account in accounts:
                account_id = account["account_id"]
                preauth_signers = [signer["key"] for signer in account["signers"] if signer["type"] == "preauth_tx"]
                tokenbalances = [
                    float(b["balance"])
                    for b in account["balances"]
                    if b["asset_type"] == "credit_alphanum4"
                    and b["asset_code"] == tokencode
                    and b["asset_issuer"] == issuer
                ]
                tokenbalance = tokenbalances[0] if tokenbalances else 0
                if len(preauth_signers) > 0:
                    locked_accounts.append(
                        {"account": account_id, "amount": tokenbalance, "preauth_signers": preauth_signers}
                    )
        return locked_accounts

    def _get_url(self, endpoint):
        url = _THREEFOLDFOUNDATION_TFTSTELLAR_SERVICES[self._network]
        if not j.sals.nettools.wait_connection_test(url, 443, 5):
            raise j.exceptions.Timeout(f"Can not connect to server {url}, connection timeout")
        return f"https://{url}{endpoint}"

    def _get_unlockhash_transaction(self, unlockhash):
        data = {"unlockhash": unlockhash}
        resp = j.tools.http.post(
            self._get_url("/threefoldfoundation/unlock_service/get_unlockhash_transaction"), json={"args": data}
        )
        resp.raise_for_status()
        return resp.json()

    def lookup_lock_time(self, preauth_signer: str):
        unlock_tx = self._get_unlockhash_transaction(unlockhash=preauth_signer)
        if unlock_tx is None:
            return None
        txe = stellar_sdk.TransactionEnvelope.from_xdr(unlock_tx["transaction_xdr"], self._network_passphrase)
        tx = txe.transaction
        if tx.time_bounds is not None:
            return tx.time_bounds.min_time
        return None

    def getstatistics(self, tokencode: str, detailed: bool):
        stats = {"asset": tokencode}
        horizon_server = self._horizon_server
        asset_issuer = _ASSET_ISUERS[self._network][tokencode]
        stats["issuer"] = asset_issuer
        response = horizon_server.assets().for_code(tokencode).for_issuer(asset_issuer).call()
        record = response["_embedded"]["records"][0]
        stats["total"] = float(record["amount"])
        stats["num_accounts"] = record["num_accounts"]
        locked_accounts = self.get_accounts(tokencode, asset_issuer)
        total_locked = 0.0
        for locked_account in locked_accounts:
            total_locked += locked_account["amount"]
        stats["total_locked"] = total_locked
        if not detailed:
            return stats
        amounts_per_locktime = {}
        for locked_account in locked_accounts:
            if locked_account["account"] in self.locked_accounts:
                locked_account["until"] = self.locked_accounts[locked_account["account"]]["until"]
            else:
                locked_account["until"] = self.lookup_lock_time(locked_account["preauth_signers"][0])
                self.locked_accounts[locked_account["account"]] = locked_account
        for locked_account in locked_accounts:
            amount = amounts_per_locktime.get(locked_account["until"], 0.0)
            amount += locked_account["amount"]
            amounts_per_locktime[locked_account["until"]] = amount
        locked_amounts = []
        for until, amount in amounts_per_locktime.items():
            locked_amounts.append({"until": until, "amount": amount})

        def sort_key(a):
            return a["until"]

        locked_amounts.sort(key=sort_key)
        stats["locked"] = locked_amounts
        return stats


@click.command(help="Statistics about TFT, TFTA and FreeTFT")
@click.argument("tokencode", type=click.Choice(["TFT", "TFTA", "FreeTFT"]), default="TFT")
@click.option("--network", type=click.Choice(["test", "public"], case_sensitive=False), default="public")
@click.option("--detailed/--not-detailed", default=False)
def show_stats(tokencode, network, detailed):
    print(f"Statistics for {tokencode} on the {network} network")
    collector = StatisticsCollector(network)
    stats = collector.getstatistics(tokencode, detailed)
    print(f"Total amount of tokens: {stats['total']:,.7f}")
    print(f"Number of accounts: {stats['num_accounts']}")
    print(f"Amount of locked tokens: {stats['total_locked']:,.7f}")
    if detailed:
        for locked_amount in stats["locked"]:
            print(
                f"{locked_amount['amount']:,.7f} locked until {datetime.datetime.fromtimestamp(locked_amount['until'])}"
            )


if __name__ == "__main__":
    show_stats()
