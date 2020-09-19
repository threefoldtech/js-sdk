import math
import base64
import time
from enum import Enum
import decimal
from urllib import parse
from urllib.parse import urlparse
from typing import Union

import stellar_sdk
from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.loader import j
from stellar_sdk import Asset, TransactionBuilder

from .wrapped import Account, Server
from .balance import AccountBalances, Balance, EscrowAccount
from .transaction import Effect, PaymentSummary, TransactionSummary
from .exceptions import UnAuthorized


_THREEFOLDFOUNDATION_TFTSTELLAR_SERVICES = {"TEST": "testnet.threefold.io", "STD": "tokenservices.threefold.io"}
_HORIZON_NETWORKS = {"TEST": "https://horizon-testnet.stellar.org", "STD": "https://horizon.stellar.org"}
_NETWORK_PASSPHRASES = {
    "TEST": stellar_sdk.Network.TESTNET_NETWORK_PASSPHRASE,
    "STD": stellar_sdk.Network.PUBLIC_NETWORK_PASSPHRASE,
}
_NETWORK_KNOWN_TRUSTS = {
    "TEST": {
        "TFT": "GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3",
        "FreeTFT": "GBLDUINEFYTF7XEE7YNWA3JQS4K2VD37YU7I2YAE7R5AHZDKQXSS2J6R",
        "TFTA": "GB55A4RR4G2MIORJTQA4L6FENZU7K4W7ATGY6YOT2CW47M5SZYGYKSCT",
    },
    "STD": {
        "TFT": "GBOVQKJYHXRR3DX6NOX2RRYFRCUMSADGDESTDNBDS6CDVLGVESRTAC47",
        "FreeTFT": "GCBGS5TFE2BPPUVY55ZPEMWWGR6CLQ7T6P46SOFGHXEBJ34MSP6HVEUT",
        "TFTA": "GBUT4GP5GJ6B3XW5PXENHQA7TXJI5GOPW3NF4W3ZIW6OOO4ISY6WNLN2",
    },
}
_THREEFOLDFOUNDATION_TFTSTELLAR_ENDPOINT = {
    "FUND": "/threefoldfoundation/transactionfunding_service/fund_transaction",
    "CREATE_UNLOCK": "/threefoldfoundation/unlock_service/create_unlockhash_transaction",
    "GET_UNLOCK": "/threefoldfoundation/unlock_service/get_unlockhash_transaction",
    "CREATE_ACTIVATION_CODE": "/threefoldfoundation/activation_service/create_activation_code",
    "ACTIVATE_ACCOUNT": "/threefoldfoundation/activation_service/activate_account",
}


class Network(Enum):
    STD = "STD"
    TEST = "TEST"


class Stellar(Client):
    network = fields.Enum(Network)
    address = fields.String()

    def secret_updated(self, value):
        self.address = stellar_sdk.Keypair.from_secret(value).public_key

    secret = fields.String(on_update=secret_updated)

    def _get_horizon_server(self):
        server_url = _HORIZON_NETWORKS[self.network.value]
        server = Server(horizon_url=server_url)
        return server

    def _get_free_balances(self, address=None):
        address = address or self.address
        balances = AccountBalances(address)
        response = self._get_horizon_server().accounts().account_id(address).call()
        for response_balance in response["balances"]:
            balances.add_balance(Balance.from_horizon_response(response_balance))
        return balances

    def load_account(self):
        horizonServer = self._get_horizon_server()
        saccount = horizonServer.load_account(self.address)
        account = Account(saccount.account_id, saccount.sequence, self)
        return account

    def _get_url(self, endpoint):
        url = _THREEFOLDFOUNDATION_TFTSTELLAR_SERVICES[self.network.value]
        if not j.sals.nettools.wait_connection_test(url, 443, 5):
            raise j.exceptions.Timeout(f"Can not connect to server {url}, connection timeout")
        endpoint = _THREEFOLDFOUNDATION_TFTSTELLAR_ENDPOINT[endpoint]
        return f"https://{url}{endpoint}"

    def _fund_transaction(self, transaction):
        data = {"transaction": transaction}
        resp = j.tools.http.post(self._get_url("FUND"), json={"args": data})
        resp.raise_for_status()
        return resp.json()

    def _create_unlockhash_transaction(self, unlock_hash, transaction_xdr):
        data = {"unlockhash": unlock_hash, "transaction_xdr": transaction_xdr}
        resp = j.tools.http.post(self._get_url("CREATE_UNLOCK"), json={"args": data})
        resp.raise_for_status()
        return resp.json()

    def _get_unlockhash_transaction(self, unlockhash):
        data = {"unlockhash": unlockhash}
        resp = j.tools.http.post(self._get_url("GET_UNLOCK"), json={"args": data})
        resp.raise_for_status()
        return resp.json()

    def _create_activation_code(self):
        data = {"address": self.address}
        resp = j.tools.http.post(self._get_url("CREATE_ACTIVATION_CODE"), json={"args": data})
        resp.raise_for_status()
        return resp.json()

    def _activation_account(self, activation_code):
        data = {"activation_code": activation_code}
        resp = j.tools.http.post(self._get_url("ACTIVATE_ACCOUNT"), json={"args": data})
        resp.raise_for_status()
        return resp.json()

    def set_unlock_transaction(self, unlock_transaction):
        """
        Adds a xdr encoded unlocktransaction
        :param unlock_transaction: xdr encoded unlocktransactionaddress of the destination.
        :type destination_address: str
        """
        txe = stellar_sdk.TransactionEnvelope.from_xdr(unlock_transaction, _NETWORK_PASSPHRASES[self.network.value])
        tx_hash = txe.hash()
        unlock_hash = stellar_sdk.strkey.StrKey.encode_pre_auth_tx(tx_hash)

        self._create_unlockhash_transaction(unlock_hash=unlock_hash, transaction_xdr=txe.to_xdr())

    def get_balance(self, address=None):
        """Gets balance for a stellar address
        """
        if address is None:
            address = self.address
        all_balances = self._get_free_balances(address)
        for account in self._find_escrow_accounts(address):
            all_balances.add_escrow_account(account)
        return all_balances

    def _find_escrow_accounts(self, address=None):
        if address is None:
            address = self.address
        escrow_accounts = []
        accounts_endpoint = self._get_horizon_server().accounts()
        accounts_endpoint.signer(address)
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
                if account_id == address:
                    continue  # Do not take the receiver's account
                all_signers = account["signers"]
                preauth_signers = [signer["key"] for signer in all_signers if signer["type"] == "preauth_tx"]
                # TODO check the tresholds and signers
                # TODO if we can merge, the amount is unlocked ( if len(preauth_signers))==0
                balances = []
                for response_balance in account["balances"]:
                    balances.append(Balance.from_horizon_response(response_balance))

                escrow_account = EscrowAccount(
                    account_id,
                    preauth_signers,
                    balances,
                    _NETWORK_PASSPHRASES[self.network.value],
                    self._get_unlockhash_transaction,
                )
                escrow_accounts.append(escrow_account)
        return escrow_accounts

    def claim_locked_funds(self):
        balances = self.get_balance()
        for locked_account in balances.escrow_accounts:
            if locked_account.can_be_unlocked():
                self._unlock_account(locked_account)

    def _unlock_account(self, escrow_account):
        submitted_unlock_transactions = 0
        for unlockhash in escrow_account.unlockhashes:
            unlockhash_transation = self._get_unlockhash_transaction(unlockhash=unlockhash)
            if unlockhash_transation is None:
                return
            j.logger.info(unlockhash_transation["transaction_xdr"])
            self._get_horizon_server().submit_transaction(unlockhash_transation["transaction_xdr"])
            submitted_unlock_transactions += 1

        if submitted_unlock_transactions == len(escrow_account.unlockhashes):
            self._merge_account(escrow_account.address)

    def _merge_account(self, address):
        server = self._get_horizon_server()
        account = server.load_account(address)
        # Increment the sequence number in case the unlock transaction was not processed before the load_account call
        # account.increment_sequence_number()
        balances = self._get_free_balances(address)
        base_fee = server.fetch_base_fee()
        transaction_builder = stellar_sdk.TransactionBuilder(
            source_account=account, network_passphrase=_NETWORK_PASSPHRASES[self.network.value], base_fee=base_fee
        )
        for balance in balances.balances:
            if balance.is_native():
                continue
            # Step 1: Transfer custom assets
            transaction_builder.append_payment_op(
                destination=self.address,
                amount=balance.balance,
                asset_code=balance.asset_code,
                asset_issuer=balance.asset_issuer,
            )
            # Step 2: Delete trustlines
            transaction_builder.append_change_trust_op(
                asset_issuer=balance.asset_issuer, asset_code=balance.asset_code, limit="0"
            )
        # Step 3: Merge account
        transaction_builder.append_account_merge_op(self.address)

        transaction_builder.set_timeout(30)
        transaction = transaction_builder.build()
        signer_kp = stellar_sdk.Keypair.from_secret(self.secret)
        transaction.sign(signer_kp)
        server.submit_transaction(transaction)

    def activate_through_friendbot(self):
        """Activates and funds a testnet account using riendbot
        """
        if self.network.value != "TEST":
            raise Exception("Account activation through friendbot is only available on testnet")

        resp = j.tools.http.get("https://friendbot.stellar.org/", params={"addr": self.address})
        resp.raise_for_status()
        j.logger.info(f"account with address {self.address} activated and  funded through friendbot")

    def activate_through_threefold_service(self):
        """
        Activate your weallet through threefold services
        """
        activationdata = self._create_activation_code()
        self._activation_account(activationdata["activation_code"])

    def activate_account(self, destination_address, starting_balance="12.50"):
        """Activates another account

        Args:
            destination_address (str): address of the destination
            starting_balance (str, optional): the balance that the destination address will start with. Must be a positive integer expressed as a string. Defaults to "12.50".
        """
        server = self._get_horizon_server()
        source_keypair = stellar_sdk.Keypair.from_secret(self.secret)

        source_account = self.load_account()

        base_fee = server.fetch_base_fee()
        transaction = (
            stellar_sdk.TransactionBuilder(
                source_account=source_account,
                network_passphrase=_NETWORK_PASSPHRASES[self.network.value],
                base_fee=base_fee,
            )
            .append_create_account_op(destination=destination_address, starting_balance=starting_balance)
            .build()
        )
        transaction.sign(source_keypair)
        try:
            response = server.submit_transaction(transaction)
            j.logger.info("Transaction hash: {}".format(response["hash"]))
        except stellar_sdk.exceptions.BadRequestError as e:
            j.logger.debug(e)

    def add_trustline(self, asset_code, issuer, secret=None):
        """Create a trustline to an asset

        Args:
            asset_code (str): code of the asset. For example: 'BTC', 'TFT', ...
            issuer (str): address of the asset issuer
            secret (str, optional): Secret to use will use instance property if empty. Defaults to None.
        """
        self._change_trustline(asset_code, issuer, secret=secret)

    def add_known_trustline(self, asset_code):
        """Will add a trustline known by threefold for chosen asset_code

        Args:
            asset_code (str): code of the asset. For example: 'BTC', 'TFT', ...
        """
        issuer = _NETWORK_KNOWN_TRUSTS.get(self.network.value, {}).get(asset_code)
        if not issuer:
            raise j.exceptions.NotFound(f"We do not provide a known issuers for {asset_code} on network {self.network}")
        self._change_trustline(asset_code, issuer)

    def delete_trustline(self, asset_code, issuer, secret=None):
        """Deletes a trustline

        Args:
            asset_code (str): code of the asset. For example: 'BTC', 'XRP', ...
            issuer (str): address of the asset issuer
            secret (str, optional): Secret to use will use instance property if empty. Defaults to None.
        """
        self._change_trustline(asset_code, issuer, limit="0", secret=secret)

    def _change_trustline(self, asset_code, issuer, limit=None, secret=None):
        """Create a trustline between you and the issuer of an asset

        Args:
            asset_code (str): code which form the asset. For example: 'BTC', 'TFT', ...
            issuer (str): address of the asset issuer
            limit ([type], optional): The limit for the asset, defaults to max int64(922337203685.4775807). If the limit is set to “0” it deletes the trustline. Defaults to None.
            secret (str, optional): Secret to use will use instance property if empty. Defaults to None.
        """
        # if no secret is provided we assume we change trustlines for this account
        secret = secret or self.secret

        server = self._get_horizon_server()
        source_keypair = stellar_sdk.Keypair.from_secret(secret)
        source_public_key = source_keypair.public_key
        source_account = server.load_account(source_public_key)

        base_fee = server.fetch_base_fee()

        transaction = (
            stellar_sdk.TransactionBuilder(
                source_account=source_account,
                network_passphrase=_NETWORK_PASSPHRASES[self.network.value],
                base_fee=base_fee,
            )
            .append_change_trust_op(asset_issuer=issuer, asset_code=asset_code, limit=limit)
            .set_timeout(30)
            .build()
        )

        transaction.sign(source_keypair)

        try:
            response = server.submit_transaction(transaction)
            j.logger.info("Transaction hash: {}".format(response["hash"]))
        except stellar_sdk.exceptions.BadRequestError as e:
            j.logger.debug(e)
            raise e

    def transfer(
        self,
        destination_address,
        amount,
        asset="XLM",
        locked_until=None,
        memo_text=None,
        memo_hash=None,
        fund_transaction=True,
        from_address=None,
        timeout=30,
        sequence_number: int = None,
        sign: bool = True,
    ):
        """Transfer assets to another address

        Args:
            destination_address (str): address of the destination
            amount (str): can be a floating point number with 7 numbers after the decimal point expressed as a string
            asset (str, optional): asset to transfer. Defaults to "XLM". if you wish to specify an asset it should be in format 'assetcode:issuer'. Where issuer is the address of the
            issuer of the asset.
            locked_until (float, optional): epoch timestamp indicating until when the tokens  should be locked. Defaults to None.
            memo_text (Union[str, bytes], optional): memo text to add to the transaction, a string encoded using either ASCII or UTF-8, up to 28-bytes long. Defaults to None.
            memo_hash (Union[str, bytes], optional): memo hash to add to the transaction, A 32 byte hash. Defaults to None.
            fund_transaction (bool, optional): use the threefoldfoundation transaction funding service. Defautls to True.
            from_address (str, optional): Use a different address to send the tokens from, useful in multisig use cases. Defaults to None.
            timeout (int,optional: Seconds from now on until when the transaction to be submitted to the stellar network
            sequence_number (int,optional): specify a specific sequence number ( will still be increased by one) instead of loading it from the account
            sign (bool,optional) : Do not sign and submit the transaction

        Raises:
            Exception: If asset not in correct format
            stellar_sdk.exceptions.BadRequestError: not enough funds for opertaion
            stellar_sdk.exceptions.BadRequestError: bad transfer authentication

        Returns:
            [type]: [description]
        """
        issuer = None
        j.logger.info(f"Sending {amount} {asset} to {destination_address}")
        if asset != "XLM":
            assetStr = asset.split(":")
            if len(assetStr) != 2:
                raise Exception("Wrong asset format should be in format 'assetcode:issuer'")
            asset = assetStr[0]
            issuer = assetStr[1]

        if locked_until is not None:
            return self._transfer_locked_tokens(
                destination_address,
                amount,
                asset,
                issuer,
                locked_until,
                memo_text=memo_text,
                memo_hash=memo_hash,
                fund_transaction=fund_transaction,
                from_address=from_address,
            )

        horizon_server = self._get_horizon_server()

        base_fee = horizon_server.fetch_base_fee()
        if from_address:
            source_account = horizon_server.load_account(from_address)
        else:
            source_account = self.load_account()

        if sequence_number:
            source_account.sequence = sequence_number

        transaction_builder = stellar_sdk.TransactionBuilder(
            source_account=source_account,
            network_passphrase=_NETWORK_PASSPHRASES[self.network.value],
            base_fee=base_fee,
        )
        transaction_builder.append_payment_op(
            destination=destination_address,
            amount=str(amount),
            asset_code=asset,
            asset_issuer=issuer,
            source=source_account.account_id,
        )
        transaction_builder.set_timeout(timeout)
        if memo_text is not None:
            transaction_builder.add_text_memo(memo_text)
        if memo_hash is not None:
            transaction_builder.add_hash_memo(memo_hash)

        transaction = transaction_builder.build()
        transaction = transaction.to_xdr()

        if asset == "TFT" or asset == "FreeTFT":
            if fund_transaction:
                transaction = self._fund_transaction(transaction=transaction)
                transaction = transaction["transaction_xdr"]

        if not sign:
            return transaction

        transaction = stellar_sdk.TransactionEnvelope.from_xdr(transaction, _NETWORK_PASSPHRASES[self.network.value])

        my_keypair = stellar_sdk.Keypair.from_secret(self.secret)
        transaction.sign(my_keypair)
        response = horizon_server.submit_transaction(transaction)
        tx_hash = response["hash"]
        j.logger.info(f"Transaction hash: {tx_hash}")
        return tx_hash

    def list_payments(self, address: str = None, asset: str = None, cursor: str = None):
        """Get the transactions for an adddress
        :param address: address of the effects.In None, the address of this wallet is taken
        :param asset: stellar asset in the code:issuer form( except for XLM, which does not need an issuer)
        :param cursor:pass a cursor to continue after the last call or an empty str to start receivibg a cursor
         if a cursor is passed, a tuple of the payments and the cursor is returned
        """
        if address is None:
            address = self.address
        tx_endpoint = self._get_horizon_server().payments()
        tx_endpoint.for_account(address)
        tx_endpoint.limit(50)
        payments = []
        old_cursor = "old"
        new_cursor = ""
        if cursor is not None:
            new_cursor = cursor
        while old_cursor != new_cursor:
            old_cursor = new_cursor
            tx_endpoint.cursor(new_cursor)
            response = tx_endpoint.call()
            next_link = response["_links"]["next"]["href"]
            next_link_query = parse.urlsplit(next_link).query
            new_cursor = parse.parse_qs(next_link_query)["cursor"][0]
            response_payments = response["_embedded"]["records"]
            for response_payment in response_payments:
                ps = PaymentSummary.from_horizon_response(response_payment, address)
                if asset:
                    split_asset = asset.split(":")
                    assetcode = split_asset[0]
                    assetissuer = None
                    if len(split_asset) > 1:
                        assetissuer = split_asset[1]
                    if ps.balance and ps.balance.asset_code == assetcode:
                        if assetissuer and assetissuer == ps.balance.asset_issuer:
                            payments.append(ps)
                else:
                    payments.append(ps)
        if cursor is not None:
            return {"payments": payments, "cursor": new_cursor}

        return payments

    def list_transactions(self, address: str = None, cursor: str = None):
        """Get the transactions for an adddres
        :param address (str, optional): address of the effects.If None, the address of this wallet is taken. Defaults to None.
        :param cursor:pass a cursor to continue after the last call or an empty str to start receivibg a cursor
         if a cursor is passed, a tuple of the payments and the cursor is returned

        Returns:
            list: list of TransactionSummary objects
            dictionary: {"transactions":list of TransactionSummary objects, "cursor":cursor}
        """
        address = address or self.address
        tx_endpoint = self._get_horizon_server().transactions()
        tx_endpoint.for_account(address)
        tx_endpoint.include_failed(True)
        transactions = []
        old_cursor = "old"
        new_cursor = ""
        if cursor is not None:
            new_cursor = cursor
        while old_cursor != new_cursor:
            old_cursor = new_cursor
            tx_endpoint.cursor(new_cursor)
            response = tx_endpoint.call()
            next_link = response["_links"]["next"]["href"]
            next_link_query = parse.urlsplit(next_link).query
            new_cursor = parse.parse_qs(next_link_query)["cursor"][0]
            response_transactions = response["_embedded"]["records"]
            for response_transaction in response_transactions:
                if response_transaction["successful"]:
                    transactions.append(TransactionSummary.from_horizon_response(response_transaction))

        if cursor is not None:
            return {"transactions": transactions, "cursor": new_cursor}
        return transactions

    def get_transaction_effects(self, transaction_hash, address=None):
        """Get the effects on an adddressfor a specific transaction

        Args:
            transaction_hash (str): hash of the transaction
            address (str, optional): address of the effects.If None, the address of this wallet is taken. Defaults to None.

        Returns:
            list: list of Effect objects
        """
        address = address or self.address
        effects = []
        endpoint = self._get_horizon_server().effects()
        endpoint.for_transaction(transaction_hash)
        old_cursor = "old"
        new_cursor = ""
        while old_cursor != new_cursor:
            old_cursor = new_cursor
            endpoint.cursor(new_cursor)
            response = endpoint.call()
            next_link = response["_links"]["next"]["href"]
            next_link_query = parse.urlsplit(next_link).query
            new_cursor = parse.parse_qs(next_link_query)["cursor"][0]
            response_effects = response["_embedded"]["records"]
            for response_effect in response_effects:
                if "account" in response_effect and response_effect["account"] == address:
                    effects.append(Effect.from_horizon_response(response_effect))
        return effects

    def _transfer_locked_tokens(
        self,
        destination_address,
        amount,
        asset_code,
        asset_issuer,
        unlock_time,
        memo_text=None,
        memo_hash=None,
        fund_transaction=True,
        from_address=None,
    ):
        """Transfer locked assets to another address

        Args:
            destination_address (str): address of the destination
            amount (str): amount, can be a floating point number with 7 numbers after the decimal point expressed as a string
            asset_code (str): asset to transfer
            asset_issuer (str): if the asset_code is different from 'XlM', the issuer address
            unlock_time (float):  an epoch timestamp indicating when the funds should be unlocked
            memo_text (Union[str, bytes], optional): memo text to add to the transaction, a string encoded using either ASCII or UTF-8, up to 28-bytes long
            memo_hash (Union[str, bytes], optional): memo hash to add to the transaction, A 32 byte hash
            fund_transaction (bool, optional): use the threefoldfoundation transaction funding service.Defaults to True.
            from_address (str, optional): Use a different address to send the tokens from, useful in multisig use cases. Defaults to None.

        Returns:
            [type]: [description]
        """

        unlock_time = math.ceil(unlock_time)

        self._log_info("Creating escrow account")
        escrow_kp = stellar_sdk.Keypair.random()

        # minimum account balance as described at https://www.stellar.org/developers/guides/concepts/fees.html#minimum-account-balance
        horizon_server = self._get_horizon_server()
        base_fee = horizon_server.fetch_base_fee()
        base_reserve = 0.5
        minimum_account_balance = (2 + 1 + 3) * base_reserve  # 1 trustline and 3 signers
        required_XLM = minimum_account_balance + base_fee * 0.0000001 * 3

        self._log_info("Activating escrow account")
        self.activate_account(escrow_kp.public_key, str(math.ceil(required_XLM)))

        if asset_code != "XLM":
            self._log_info("Adding trustline to escrow account")
            self.add_trustline(asset_code, asset_issuer, escrow_kp.secret)

        preauth_tx = self._create_unlock_transaction(escrow_kp, unlock_time)
        preauth_tx_hash = preauth_tx.hash()

        # save the preauth transaction in our unlock service
        unlock_hash = stellar_sdk.strkey.StrKey.encode_pre_auth_tx(preauth_tx_hash)
        self._create_unlockhash_transaction(unlock_hash=unlock_hash, transaction_xdr=preauth_tx.to_xdr())

        self._set_escrow_account_signers(escrow_kp.public_key, destination_address, preauth_tx_hash, escrow_kp)
        self._log_info("Unlock Transaction:")
        self._log_info(preauth_tx.to_xdr())

        self.transfer(
            escrow_kp.public_key,
            amount,
            asset_code + ":" + asset_issuer,
            memo_text=memo_text,
            memo_hash=memo_hash,
            fund_transaction=fund_transaction,
            from_address=from_address,
        )
        return preauth_tx.to_xdr()

    def _create_unlock_transaction(self, escrow_kp, unlock_time):
        server = self._get_horizon_server()
        escrow_account = server.load_account(escrow_kp.public_key)
        escrow_account.increment_sequence_number()
        tx = (
            stellar_sdk.TransactionBuilder(escrow_account)
            .append_set_options_op(master_weight=0, low_threshold=1, med_threshold=1, high_threshold=1)
            .add_time_bounds(unlock_time, 0)
            .build()
        )
        tx.sign(escrow_kp)
        return tx

    def _set_account_signers(self, address, public_key_signer, preauth_tx_hash, signer_kp):
        server = self._get_horizon_server()
        if address == self.address:
            account = self.load_account()
        else:
            account = server.load_account(address)
        tx = (
            stellar_sdk.TransactionBuilder(account)
            .append_pre_auth_tx_signer(preauth_tx_hash, 1)
            .append_ed25519_public_key_signer(public_key_signer, 1)
            .append_set_options_op(master_weight=1, low_threshold=2, med_threshold=2, high_threshold=2)
            .build()
        )

        tx.sign(signer_kp)
        response = server.submit_transaction(tx)
        j.logger.info(response)
        j.logger.info(f"Set the signers of {address} to {public_key_signer} and {preauth_tx_hash}")

    def get_signing_requirements(self, address: str = None):
        address = address or self.address
        response = self._get_horizon_server().accounts().account_id(address).call()
        signing_requirements = {}
        signing_requirements["thresholds"] = response["thresholds"]
        signing_requirements["signers"] = response["signers"]
        return signing_requirements

    def modify_signing_requirements(
        self, public_keys_signers, signature_count, low_treshold=0, high_treshold=2, master_weight=2
    ):
        """modify_signing_requirements sets to amount of signatures required for the creation of multisig account. It also adds
           the public keys of the signer to this account

        Args:
            public_keys_signers (list): list of public keys of signers
            signature_count (int): amount of signatures requires to transfer funds
            low_treshold (int, optional): amount of signatures required for low security operations (transaction processing, allow trust, bump sequence). Defaults to 1.
            high_treshold (int, optional): amount of signatures required for high security operations (set options, account merge). Defaults to 2.
            master_weight (int, optional): A number from 0-255 (inclusive) representing the weight of the master key. If the weight of the master key is updated to 0, it is effectively disabled. Defaults to 2.
        """
        server = self._get_horizon_server()
        account = self.load_account()
        source_keypair = stellar_sdk.Keypair.from_secret(self.secret)

        transaction_builder = stellar_sdk.TransactionBuilder(account)
        # set the signing options
        transaction_builder.append_set_options_op(
            low_threshold=low_treshold,
            med_threshold=signature_count,
            high_threshold=high_treshold,
            master_weight=master_weight,
        )

        # For every public key given, add it as a signer to this account
        for public_key_signer in public_keys_signers:
            transaction_builder.append_ed25519_public_key_signer(public_key_signer, 1)

        transaction_builder.set_timeout(30)
        tx = transaction_builder.build()
        tx.sign(source_keypair)

        try:
            response = server.submit_transaction(tx)
            j.logger.info(response)
            j.logger.info(f"Set the signers of {self.address} to require {signature_count} signers")
        except stellar_sdk.exceptions.BadRequestError:
            j.logger.info("Transaction need additional signatures in order to send")
            return tx.to_xdr()

    def sign(self, tx_xdr: str, submit: bool = True):
        """ sign signs a transaction xdr and optionally submits it to the network

        Args:
            tx_xdr (str): transaction to sign in xdr format
            submit (bool,optional): submit the transaction tro the Stellar network
        """

        source_keypair = stellar_sdk.Keypair.from_secret(self.secret)
        tx = stellar_sdk.TransactionEnvelope.from_xdr(tx_xdr, _NETWORK_PASSPHRASES[self.network.value])
        tx.sign(source_keypair)
        if submit:
            horizon_server = self._get_horizon_server()
            horizon_server.submit_transaction(tx)
        else:
            return tx.to_xdr()

    def sign_multisig_transaction(self, tx_xdr):
        """sign_multisig_transaction signs a transaction xdr and tries to submit it to the network

           Deprecated, use sign instead

        Args:
            tx_xdr (str): transaction to sign in xdr format
        """

        try:
            self.sign(tx_xdr)
            j.logger.info("Multisig tx signed and sent")
        except UnAuthorized as e:
            j.logger.info("Transaction needs additional signatures in order to send")
            return e.transaction_xdr

    def remove_signer(self, public_key_signer):
        """remove_signer removes a public key as a signer from the source account

        Args:
            public_key_signer (str): public key of an account
        """
        server = self._get_horizon_server()
        account = self.load_account()
        tx = stellar_sdk.TransactionBuilder(account).append_ed25519_public_key_signer(public_key_signer, 0).build()

        source_keypair = stellar_sdk.Keypair.from_secret(self.secret)

        tx.sign(source_keypair)
        try:
            response = server.submit_transaction(tx)
            j.logger.info(response)
            j.logger.info("Multisig tx signed and sent")
        except stellar_sdk.exceptions.BadRequestError:
            j.logger.info("Transaction need additional signatures in order to send")
            return tx.to_xdr()

    def get_sender_wallet_address(self, transaction_hash):
        """Get the sender's wallet address from a transaction hash

        Args:
            transaction_hash (String): Transaction hash

        Returns:
            String : Wallet Hash

        """
        server = self._get_horizon_server()
        endpoint = server.operations().for_transaction(transaction_hash)
        response = endpoint.call()
        # not possible for a transaction to have more than a source, so will take first one
        wallet_address = response["_embedded"]["records"][0]["source_account"]
        return wallet_address

    def check_is_payment_transaction(self, transaction_hash):
        """Some transactions doesn't have an amount like activating the wallet
        This helper method to help in iterating in transactions

        Args:
            transaction_hash (String): Transaction hash

        Returns:
            Bool: True if transaction has amount - False if not
        """

        server = self._get_horizon_server()
        endpoint = server.operations().for_transaction(transaction_hash)
        response = endpoint.call()
        results = response["_embedded"]["records"][0]
        return results["type"] == "payment"

    def get_asset(self, code="TFT", issuer=None) -> stellar_sdk.Asset:
        """Gets an stellar_sdk.Asset object by code.
        if the code is TFT or TFTA we quickly return the Asset object based on the code.
        if the code is native (XLM) we return the Asset object with None issuer.
        if the code isn't unknown, exception is raised to manually construct the Asset object.

        Args:
            code (str, optional): code for the asset. Defaults to "TFT".
            issuer (str, optional): issuer for the asset. Defaults to None.

        Raises:
            ValueError: empty code, In case of issuer is None and not XLM or the code isn't for TFT or TFTA.
            stellar_sdk.exceptions.AssetIssuerInvalidError: Invalid issuer
        Returns:
            stellar_sdk.Asset: Asset object.
        """
        network = self.network.value
        KNOWN_ASSETS = list(_NETWORK_KNOWN_TRUSTS[network].keys()) + ["XLM"]

        if issuer and code:
            return Asset(code, issuer)

        if not code:
            raise ValueError("need to provide code")

        if not issuer and code not in KNOWN_ASSETS:
            raise ValueError(
                f"Make sure to supply the issuer for {code}, issuer is allowed to be none only in case of {KNOWN_ASSETS}"
            )

        if not issuer and code in KNOWN_ASSETS:
            asset_issuer = _NETWORK_KNOWN_TRUSTS[network].get(code, None)
            return Asset(code, asset_issuer)

    def cancel_sell_order(
        self,
        offer_id,
        selling_asset: stellar_sdk.Asset,
        buying_asset: stellar_sdk.Asset,
        price: Union[str, decimal.Decimal],
    ):
        """Deletes a selling order for amount `amount` of `selling_asset` for `buying_asset` with the price of `price`

        Args:
            selling_asset (stellar_sdk.Asset): Selling Asset object - check wallet object.get_asset_by_code function
            buying_asset (stellar_sdk.Asset): Buying Asset object - Asset object - check wallet object.get_asset_by_code function
            offer_id (int): pass the current offer id and set the amount to 0 to cancel this offer
            price (str): order price
        """
        return self._manage_sell_order(
            selling_asset=selling_asset, buying_asset=buying_asset, amount="0", price=price, offer_id=offer_id
        )

    def _manage_sell_order(
        self,
        selling_asset: stellar_sdk.Asset,
        buying_asset: stellar_sdk.Asset,
        amount: Union[str, decimal.Decimal],
        price: Union[str, decimal.Decimal],
        timeout=30,
        offer_id=0,
    ):
        """Places/Deletes a selling order for amount `amount` of `selling_asset` for `buying_asset` with the price of `price`

        Args:
            selling_asset (stellar_sdk.Asset): Selling Asset object - check wallet object.get_asset_by_code function
            buying_asset (stellar_sdk.Asset): Buying Asset object - Asset object - check wallet object.get_asset_by_code function
            amount (Union[str, decimal.Decimal]): Amount to sell.
            price (Union[str, decimal.Decimal]): Price for selling.
            timeout (int, optional): Timeout for submitting the transaction. Defaults to 30.
            offer_id: pass the current offer id and set the amount to 0 to cancel this offer or another amount to update the offer

        Raises:
            ValueError: In case of invalid issuer.
            RuntimeError: Error happened during submission of the transaction.

        Returns:
            (dict): response as the result of sumbit the transaction
        """
        server = self._get_horizon_server()
        tb = TransactionBuilder(self.load_account(), network_passphrase=_NETWORK_PASSPHRASES[self.network.value])
        try:
            tx = (
                tb.append_manage_sell_offer_op(
                    selling_code=selling_asset.code,
                    selling_issuer=selling_asset.issuer,
                    buying_code=buying_asset.code,
                    buying_issuer=buying_asset.issuer,
                    amount=amount,
                    price=price,
                    offer_id=offer_id,
                )
                .set_timeout(timeout)
                .build()
            )
        except stellar_sdk.exceptions.AssetIssuerInvalidError as e:
            raise ValueError("invalid issuer") from e
        except Exception as e:
            raise RuntimeError(
                f"error happened for placing selling order for selling: {selling_asset}, buying: {buying_asset}, amount: {amount} price: {price}"
            ) from e
        else:
            tx.sign(self.secret)
            try:
                resp = server.submit_transaction(tx)
            except Exception as e:
                raise RuntimeError(
                    f"couldn't submit sell offer, probably wallet is unfunded. Please check the error stacktrace for more information."
                ) from e
            return resp

    place_sell_order = _manage_sell_order

    def get_created_offers(self, wallet_address: str = None):
        """Returns a list of the currently created offers

        Args:
            wallet_address (Str, optional): wallet address you want to get offers to. Defaults to self.address.

        Returns:
            list
        """
        wallet_address = wallet_address or self.address
        server = self._get_horizon_server()
        endpoint = server.offers()
        endpoint.account(wallet_address)
        response = endpoint.call()
        offers = response["_embedded"]["records"]
        return offers

    def set_data_entry(self, name: str, value: str, address: str = None):
        """Sets, modifies or deletes a data entry (name/value pair) for an account

        To delete a data entry, set the value to an empty string.

        """

        address = address or self.address
        signing_key = stellar_sdk.Keypair.from_secret(self.secret)
        horizon_server = self._get_horizon_server()
        if address == self.address:
            account = self.load_account()
        else:
            account = horizon_server.load_account(address)
        base_fee = horizon_server.fetch_base_fee()
        transaction = (
            stellar_sdk.TransactionBuilder(
                source_account=account, network_passphrase=_NETWORK_PASSPHRASES[self.network.value], base_fee=base_fee,
            )
            .append_manage_data_op(name, value)
            .set_timeout(30)
            .build()
        )

        transaction.sign(signing_key)

        try:
            response = horizon_server.submit_transaction(transaction)
            j.logger.info("Transaction hash: {}".format(response["hash"]))
        except stellar_sdk.exceptions.BadRequestError as e:
            j.logger.debug(e)
            raise e

    def get_data_entries(self, address: str = None):
        address = address or self.address
        horizon_server = self._get_horizon_server()
        response = horizon_server.accounts().account_id(address).call()
        data = {}
        for data_name, data_value in response["data"].items():
            data[data_name] = base64.b64decode(data_value).decode("utf-8")
        return data
