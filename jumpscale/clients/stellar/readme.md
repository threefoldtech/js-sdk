# Stellar client and wallet

## Create a new wallet

```python
# valid types for network: STD and TEST, by default it is set to STD
wallet = j.clients.stellar.new('my_wallet', network='TEST')
# available as `j.clients.stellar.my_wallet` from now on
```

## restore a wallet from a secret

```python
# valid types for network: STD and TEST, by default it is set to STD
wallet = j.clients.stellar.new('my_wallet', network='TEST', secret='S.....')
# available as `j.clients.stellar.my_wallet` from now on
```

## Trustlines

As an example, add a trustline to TFT:GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3 (TFT on testnet):

``` python
wallet.add_trustline('TFT','GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3')
```

and remove it again:

``` python
wallet.delete_trustline('TFT','GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3')
```

Check more about trustlines: [here](https://www.stellar.org/developers/guides/concepts/assets.html#trustlines)

## Transferring assets

Send 1000 TFT to another address:

```python
j.clients.stellar.my_wallet.transfer('<destination address>',"1000", asset="TFT:GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3")
'9c6888ea3d461aff4605246e9e58c07c172513b3d8dc4a621edd745fec1b17a4'
```

The returned string is the hash of the transaction.

Send 1000 TFT to another address but time locked until within 10 minutes:

> **For locked token support**: install following threebot package: [https://github.com/threefoldfoundation/tft-stellar/tree/master/ThreeBotPackages/unlock-service](https://github.com/threefoldfoundation/tft-stellar/tree/master/ThreeBotPackages/unlock-service)!

```python
j.clients.stellar.my_wallet.transfer('<destination address>',"1000", asset="TFT:GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3", locked_until=time.time()+10*60)

'AAAAAAbKy5zVPcXiRCYKwpv6SkIXXJRCV97nwH9PtRniy+7fAAAAZAADNQcAAAADAAAAAQAAAABeQs2iAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAFAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAABAAAAAQAAAAEAAAABAAAAAQAAAAEAAAAAAAAAAAAAAAAAAAAB4svu3wAAAEAE6w7jduF+Vx0zwKTlLkxCSaogT/q3nyso1VowS0tL6mLFJ0/+afCe4dbubvzXy9AuBbaF9h0vgslESCey0IcB'
```
The returned string is the unlocktransaction

## Adding memo_text to a payment


```python
j.clients.stellar.my_wallet.transfer('<destination address>',"10", asset="TFT:GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3", memo_text="test")
'9c6888ea3d461aff4605246e9e58c07c172513b3d8dc4a621edd745fec1b17a4'
```

## checking the balance of an account

```python
JSX> j.clients.stellar.my_wallet.get_balance()
Balances
  1000.0000000 TFT:GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3
  9999.9999900 XLM
Locked balances:
 - Escrow account GADMVS442U64LYSEEYFMFG72JJBBOXEUIJL55Z6AP5H3KGPCZPXN6MHD with unknown unlockhashes ['TDTGRL5ZDC6JLYP2GCSFRQONSH7JP7BA4HKFHO2UMLTLBXOQZN2AHXGY']
- 1000.0000000 TFT:GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3
- 3.9999600 XLM
```

after adding the unlock transaction:

```python
JSX> j.clients.stellar.my_wallet.set_unlock_transaction('AAAAAAbKy5zVPcXiRCYKwpv6SkIXXJRCV97nwH9PtRniy+7fAAAAZAADNQcAAAADAAAAAQAAAABeQs2iAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAFAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAABAAAAAQAAAAEAAAABAAAAAQAAAAEAAAAAAAAAAAAAAAAAAAAB4svu3wAAAEAE6w7jduF+Vx0zwKTlLkxCSaogT/q3nyso1VowS0tL6mLFJ0/+afCe4dbubvzXy9AuBbaF9h0vgslESCey0IcB')
JSX> j.clients.stellar.my_wallet.get_balance()
Balances
  1000.0000000 TFT:GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3
  9999.9999900 XLM
Locked balances:
 - Locked until February 11 2020 15:52:02 on escrow account GADMVS442U64LYSEEYFMFG72JJBBOXEUIJL55Z6AP5H3KGPCZPXN6MHD
- 1000.0000000 TFT:GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3
- 3.9999600 XLM
```

## claim locked funds

When the proper unlock transaction is added to the wallet, the funds can be claimed

```python
JSX> j.clients.stellar.my_wallet.set_unlock_transaction('AAAAAAbKy5zVPcXiRCYKwpv6SkIXXJRCV97nwH9PtRniy+7fAAAAZAADNQcAAAADAAAAAQAAAABeQs2iAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAFAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAABAAAAAQAAAAEAAAABAAAAAQAAAAEAAAAAAAAAAAAAAAAAAAAB4svu3wAAAEAE6w7jduF+Vx0zwKTlLkxCSaogT/q3nyso1VowS0tL6mLFJ0/+afCe4dbubvzXy9AuBbaF9h0vgslESCey0IcB')
JSX> j.clients.stellar.my_wallet.claim_locked_funds()
JSX> j.clients.stellar.my_wallet.get_balance()
Balances
  2000.0000000 TFT:GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3
  10003.9999100 XLM
```

## Transaction history and details

To get the list of transaction together with optional memotexts:

```python

JSX> j.clients.stellar.testwallet.list_transactions()
[20640a09de753c2540ac91225108d03d30a849b203cd0b13b9cfb55d56049698 created at 2020-02-05T13:46:15Z, d36c31c2966b3f25b1743455a510c3f4ead60546882410dd190c169f1c990b76 created at 2020-02-05T13:53:48Z, b2e97f13134ede6228363f3ad39c1f4ff717a382fd58c29eaa50cfa9019b1517 created at 2020-02-05T19:38:49Z, 3b001c9250de959bfc92975e689957b02bba28210fba32b4be275e9aff5146df created at 2020-02-11T15:16:24Z, 0eee1e29067a4352af1054204afd5498b64c7f4c98c3b37efeac23f801920587 created at 2020-02-11T15:24:55Z, b579cc0af56b254c28f48a9538416d9046cdb7f564f35e45d94df70576aa5069 created at 2020-02-11T15:42:09Z, a3396578b1c6493983d624fdbc5505f687a74028e065ab5b9d024a73aec13625 created at 2020-02-11T15:42:24Z, b9719b7ea2d6cce8892e34265eced707de79316b755b91c2f1414186010206d4 created at 2020-02-11T15:45:38Z, 4d68486e4abda14f380696cadc8e6b6a47f2eca58a5c8c389f5f2e004ffec82d created at 2020-02-11T16:10:04Z, 9c6888ea3d461aff4605246e9e58c07c172513b3d8dc4a621edd745fec1b17a4 created at 2020-02-14T09:14:56Z with memo text 'test']
```

An optional address can be supllied if the wanted transaction list is not for the current wallet address.

To get the effects of a transaction on an address:

```python
j.clients.stellar.testwallet.get_transaction_effects('9c6888ea3d461aff4605246e9e58c07c172513b3d8dc4a621edd745fec1b17a4')
[10.0000000 TFT:GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3]
```

As with `list_transactions`, an optional address can be supllied if the wanted transaction effects are not for the current wallet address.

## Multisignature Transactions

First convert your account to a multisignature account:

In this example we create a multisignature account with 1 other wallet with 2 signatures that are needed in order to transfer funds.

```python

JSX> j.clients.stellar.my_wallet.modify_signing_requirements([otherwallet.address], 2)

# transfer funds to a destination. Now transfer will return a transaction in xdr which needs to be signed
JSX> tx_xdr = j.clients.stellar.my_wallet.transfer(destination_address, "5")

# second signer to the multisig account needs to sign this transaction xdr in order to submit the transaction to the Stellar network.
# in case there are more than 2 signers the ouput of this function also needs to be signed by the other signers of the multisignature account.
JSX> j.clients.stellar.other_wallet.sign_multisig_transaction(tx_xdr)
```

If you need to remove a signer from a multisignature account:

```python

JSX> tx = j.clients.stellar.my_wallet.modify_signing_requirements([], 1)

# second signer to the multisig account needs to sign this transaction xdr in order to submit the transaction to the Stellar network.
# in case there are more than 2 signers the ouput of this function also needs to be signed by the other signers of the multisignature account.
JSX> j.clients.stellar.other_wallet.sign_multisig_transaction(tx_xdr)

# last step is to remove the signer from the account
JSX> j.clients.stellar.my_wallet.remove_signer(other_wallet.address)
```

## Creating a sell order

Here is an example of placing a selling order of XLM for TFT

### Get the wallet

```python
JS-NG> w = j.clients.stellar.get("w1")
```

### Placinng a sell order

Here we place a sell order with selling amount `5 XLM` for `20 TFT`

```python
JS-NG> w.place_sell_order(selling_asset="XLM", buying_asset="TFT", amount=decimal.Decimal(5), price=decimal.Decimal(20))
{'_links': {'self': {'href': 'https://horizon-testnet.stellar.org/transactions/f02035d9e3b499db9691dd22375cee4306bb829c1a19c21641215c56cdf426ad'}, 'account': {'href': 'https://horizon-testnet.stellar.org/accounts/GC5JO4Z2MKVBA5LSJGI75D35YPVJZOLQYO2ZUXUH4HYYGTCRUW652BXP'}, 'ledger': {'href': 'https://horizon-testnet.stellar.org/ledgers/1017898'}, 'operations': {'href': 'https://horizon-testnet.stellar.org/transactions/f02035d9e3b499db9691dd22375cee4306bb829c1a19c21641215c56cdf426ad/operations{?cursor,limit,order}', 'templated': True}, 'effects': {'href': 'https://horizon-testnet.stellar.org/transactions/f02035d9e3b499db9691dd22375cee4306bb829c1a19c21641215c56cdf426ad/effects{?cursor,limit,order}', 'templated': True}, 'precedes': {'href': 'https://horizon-testnet.stellar.org/transactions?order=asc&cursor=4371838620688384'}, 'succeeds': {'href': 'https://horizon-testnet.stellar.org/transactions?order=desc&cursor=4371838620688384'}, 'transaction': {'href': 'https://horizon-testnet.stellar.org/transactions/f02035d9e3b499db9691dd22375cee4306bb829c1a19c21641215c56cdf426ad'}}, 'id': 'f02035d9e3b499db9691dd22375cee4306bb829c1a19c21641215c56cdf426ad', 'paging_token': '4371838620688384', 'successful': True, 'hash': 'f02035d9e3b499db9691dd22375cee4306bb829c1a19c21641215c56cdf426ad', 'ledger': 1017898, 'created_at': '2020-07-02T15:31:27Z', 'source_account': 'GC5JO4Z2MKVBA5LSJGI75D35YPVJZOLQYO2ZUXUH4HYYGTCRUW652BXP', 'source_account_sequence': '4356973738852368', 'fee_account': 'GC5JO4Z2MKVBA5LSJGI75D35YPVJZOLQYO2ZUXUH4HYYGTCRUW652BXP', 'fee_charged': '100', 'max_fee': '100', 'operation_count': 1, 'envelope_xdr': 'AAAAAgAAAAC6l3M6YqoQdXJJkf6PfcPqnLlww7WaXofh8YNMUaW93QAAAGQAD3qlAAAAEAAAAAEAAAAAAAAAAAAAAABe/f3qAAAAAAAAAAEAAAAAAAAAAwAAAAAAAAABVEZUAAAAAAA5/GQbeotMseuGw9LomxJQHv5mNT8nihPVgEwpv/efZAAAAAAC+vCAAAAAFAAAAAEAAAAAAAAAAAAAAAAAAAABUaW93QAAAECxmsKeKmpboSMzbxF9OD+TCg6hz6aGpfYAbqL7r3TrzC6VB5usSG2ibfWBPJUE3TquBaNtvUV5lTLTq67v+VcG', 'result_xdr': 'AAAAAAAAAGQAAAAAAAAAAQAAAAAAAAADAAAAAAAAAAAAAAAAAAAAALqXczpiqhB1ckmR/o99w+qcuXDDtZpeh+Hxg0xRpb3dAAAAAAEGUEAAAAAAAAAAAVRGVAAAAAAAOfxkG3qLTLHrhsPS6JsSUB7+ZjU/J4oT1YBMKb/3n2QAAAAAAvrwgAAAABQAAAABAAAAAAAAAAAAAAAA', 'result_meta_xdr': 'AAAAAgAAAAIAAAADAA+IKgAAAAAAAAAAupdzOmKqEHVySZH+j33D6py5cMO1ml6H4fGDTFGlvd0AAAAXP4YQQAAPeqUAAAAPAAAACQAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAQAAAAAAAAAAAAAAABHhowAAAAAAAAAAAAAAAAEAD4gqAAAAAAAAAAC6l3M6YqoQdXJJkf6PfcPqnLlww7WaXofh8YNMUaW93QAAABc/hhBAAA96pQAAABAAAAAJAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAABAAAAAAAAAAAAAAAAEeGjAAAAAAAAAAAAAAAAAQAAAAUAAAAAAA+IKgAAAAIAAAAAupdzOmKqEHVySZH+j33D6py5cMO1ml6H4fGDTFGlvd0AAAAAAQZQQAAAAAAAAAABVEZUAAAAAAA5/GQbeotMseuGw9LomxJQHv5mNT8nihPVgEwpv/efZAAAAAAC+vCAAAAAFAAAAAEAAAAAAAAAAAAAAAAAAAADAA+IKgAAAAAAAAAAupdzOmKqEHVySZH+j33D6py5cMO1ml6H4fGDTFGlvd0AAAAXP4YQQAAPeqUAAAAQAAAACQAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAQAAAAAAAAAAAAAAABHhowAAAAAAAAAAAAAAAAEAD4gqAAAAAAAAAAC6l3M6YqoQdXJJkf6PfcPqnLlww7WaXofh8YNMUaW93QAAABc/hhBAAA96pQAAABAAAAAKAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAABAAAAAAAAAAAAAAAAFNyTgAAAAAAAAAAAAAAAAwAPiBYAAAABAAAAALqXczpiqhB1ckmR/o99w+qcuXDDtZpeh+Hxg0xRpb3dAAAAAVRGVAAAAAAAOfxkG3qLTLHrhsPS6JsSUB7+ZjU/J4oT1YBMKb/3n2QAAAAAA7ikXX//////////AAAAAQAAAAEAAAAA7msoAAAAAAAAAAAAAAAAAAAAAAAAAAABAA+IKgAAAAEAAAAAupdzOmKqEHVySZH+j33D6py5cMO1ml6H4fGDTFGlvd0AAAABVEZUAAAAAAA5/GQbeotMseuGw9LomxJQHv5mNT8nihPVgEwpv/efZAAAAAADuKRdf/////////8AAAABAAAAAQAAAAEqBfIAAAAAAAAAAAAAAAAAAAAAAAAAAAA=', 'fee_meta_xdr': 'AAAAAgAAAAMAD4gWAAAAAAAAAAC6l3M6YqoQdXJJkf6PfcPqnLlww7WaXofh8YNMUaW93QAAABc/hhCkAA96pQAAAA8AAAAJAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAABAAAAAAAAAAAAAAAAEeGjAAAAAAAAAAAAAAAAAQAPiCoAAAAAAAAAALqXczpiqhB1ckmR/o99w+qcuXDDtZpeh+Hxg0xRpb3dAAAAFz+GEEAAD3qlAAAADwAAAAkAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAR4aMAAAAAAAAAAAA=', 'memo_type': 'none', 'signatures': ['sZrCnipqW6EjM28RfTg/kwoOoc+mhqX2AG6i+69068wulQebrEhtom31gTyVBN06rgWjbb1FeZUy06uu7/lXBg=='], 'valid_after': '1970-01-01T00:00:00Z', 'valid_before': '2020-07-02T15:31:54Z'}

JS-NG>
```

### Get created offers

```python
JS-NG> j.clients.stellar.tfta_acceptance.get_created_offers()
[{'_links': {'self': {'href': 'https://horizon-testnet.stellar.org/offers/18835153'}, 'offer_maker': {'href': 'https://horizon-testnet.stellar.org/accounts/GCTN24HWKYSDT4VBW76LZMBUZM5TEL7TUEJ7NLVLMJ4HL4HXUYJEZN7O'}}, 'id': '18835153', 'paging_token': '18835153', 'seller': 'GCTN24HWKYSDT4VBW76LZMBUZM5TEL7TUEJ7NLVLMJ4HL4HXUYJEZN7O', 'selling': {'asset_type': 'credit_alphanum4', 'asset_code': 'TFT', 'asset_issuer': 'GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3'}, 'buying': {'asset_type': 'native'}, 'amount': '1000.0000000', 'price_r': {'n': 16574973, 'd': 10000000}, 'price': '1.6574973', 'last_modified_ledger': 1127455, 'last_modified_time': '2020-07-09T13:39:17Z'}, {'_links': {'self': {'href': 'https://horizon-testnet.stellar.org/offers/18858735'}, 'offer_maker': {'href': 'https://horizon-testnet.stellar.org/accounts/GCTN24HWKYSDT4VBW76LZMBUZM5TEL7TUEJ7NLVLMJ4HL4HXUYJEZN7O'}}, 'id': '18858735', 'paging_token': '18858735', 'seller': 'GCTN24HWKYSDT4VBW76LZMBUZM5TEL7TUEJ7NLVLMJ4HL4HXUYJEZN7O', 'selling': {'asset_type': 'credit_alphanum4', 'asset_code': 'TFT', 'asset_issuer': 'GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3'}, 'buying': {'asset_type': 'native'}, 'amount': '10.0000000', 'price_r': {'n': 17652249, 'd': 10000000}, 'price': '1.7652249', 'last_modified_ledger': 1128742, 'last_modified_time': '2020-07-09T15:35:39Z'}]
```

### Cancel a selling order

```python
JS-NG> wallet = j.clients.stellar.tfta_acceptance
JS-NG> tft = wallet.get_asset("TFT")
JS-NG> xlm = wallet.get_asset("XLM")
JS-NG> j.clients.stellar.tfta_acceptance.manage_sell_order(offer_id=18858735, selling_asse
     1 t=tft, buying_asset=xlm, price="1.7652249")
{'_links': {'self': {'href': 'https://horizon-testnet.stellar.org/transactions/4f60ec3cf15c9b8001492e3bb4546b980c992ab761e426b79ac80a833e0fdad6'}, 'account': {'href': 'https://horizon-testnet.stellar.org/accounts/GCTN24HWKYSDT4VBW76LZMBUZM5TEL7TUEJ7NLVLMJ4HL4HXUYJEZN7O'}, 'ledger': {'href': 'https://horizon-testnet.stellar.org/ledgers/1172324'}, 'operations': {'href': 'https://horizon-testnet.stellar.org/transactions/4f60ec3cf15c9b8001492e3bb4546b980c992ab761e426b79ac80a833e0fdad6/operations{?cursor,limit,order}', 'templated': True}, 'effects': {'href': 'https://horizon-testnet.stellar.org/transactions/4f60ec3cf15c9b8001492e3bb4546b980c992ab761e426b79ac80a833e0fdad6/effects{?cursor,limit,order}', 'templated': True}, 'precedes': {'href': 'https://horizon-testnet.stellar.org/transactions?order=asc&cursor=5035093240320000'}, 'succeeds': {'href': 'https://horizon-testnet.stellar.org/transactions?order=desc&cursor=5035093240320000'}, 'transaction': {'href': 'https://horizon-testnet.stellar.org/transactions/4f60ec3cf15c9b8001492e3bb4546b980c992ab761e426b79ac80a833e0fdad6'}}, 'id': '4f60ec3cf15c9b8001492e3bb4546b980c992ab761e426b79ac80a833e0fdad6', 'paging_token': '5035093240320000', 'successful': True, 'hash': '4f60ec3cf15c9b8001492e3bb4546b980c992ab761e426b79ac80a833e0fdad6', 'ledger': 1172324, 'created_at': '2020-07-12T09:28:38Z', 'source_account': 'GCTN24HWKYSDT4VBW76LZMBUZM5TEL7TUEJ7NLVLMJ4HL4HXUYJEZN7O', 'source_account_sequence': '4835171102621724', 'fee_account': 'GCTN24HWKYSDT4VBW76LZMBUZM5TEL7TUEJ7NLVLMJ4HL4HXUYJEZN7O', 'fee_charged': '100', 'max_fee': '100', 'operation_count': 1, 'envelope_xdr': 'AAAAAgAAAACm3XD2ViQ58qG3/LywNMs7Mi/zoRP2rqtieHXw96YSTAAAAGQAES2QAAAAHAAAAAEAAAAAAAAAAAAAAABfCtfkAAAAAAAAAAEAAAAAAAAAAwAAAAFURlQAAAAAADn8ZBt6i0yx64bD0uibElAe/mY1PyeKE9WATCm/959kAAAAAAAAAAAAAAAAAQ1aGQCYloAAAAAAAR/C7wAAAAAAAAAB96YSTAAAAEDCdPuJ6a/N/kOVMuZcKZN0OlwOsvh3obSO+koEPvzGS77ICWad4/r2XBxMYUOKvmb4fnOoGUayGPEBQlLCuFAA', 'result_xdr': 'AAAAAAAAAGQAAAAAAAAAAQAAAAAAAAADAAAAAAAAAAAAAAACAAAAAA==', 'result_meta_xdr': 'AAAAAgAAAAIAAAADABHjZAAAAAAAAAAApt1w9lYkOfKht/y8sDTLOzIv86ET9q6rYnh18PemEkwAAAAXSHbdEAARLZAAAAAbAAAABQAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAQAAAAPmd4lCAAAAAAAAAAAAAAAAAAAAAAAAAAEAEeNkAAAAAAAAAACm3XD2ViQ58qG3/LywNMs7Mi/zoRP2rqtieHXw96YSTAAAABdIdt0QABEtkAAAABwAAAAFAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAABAAAAA+Z3iUIAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAYAAAADABE5JgAAAAIAAAAApt1w9lYkOfKht/y8sDTLOzIv86ET9q6rYnh18PemEkwAAAAAAR/C7wAAAAFURlQAAAAAADn8ZBt6i0yx64bD0uibElAe/mY1PyeKE9WATCm/959kAAAAAAAAAAAF9eEAAQ1aGQCYloAAAAAAAAAAAAAAAAAAAAACAAAAAgAAAACm3XD2ViQ58qG3/LywNMs7Mi/zoRP2rqtieHXw96YSTAAAAAABH8LvAAAAAwAR42QAAAAAAAAAAKbdcPZWJDnyobf8vLA0yzsyL/OhE/auq2J4dfD3phJMAAAAF0h23RAAES2QAAAAHAAAAAUAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAEAAAAD5neJQgAAAAAAAAAAAAAAAAAAAAAAAAABABHjZAAAAAAAAAAApt1w9lYkOfKht/y8sDTLOzIv86ET9q6rYnh18PemEkwAAAAXSHbdEAARLZAAAAAcAAAABAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAQAAAAPb8gRIAAAAAAAAAAAAAAAAAAAAAAAAAAMAEeK4AAAAAQAAAACm3XD2ViQ58qG3/LywNMs7Mi/zoRP2rqtieHXw96YSTAAAAAFURlQAAAAAADn8ZBt6i0yx64bD0uibElAe/mY1PyeKE9WATCm/959kAAAAAmCQPIB//////////wAAAAEAAAABAAAAAAAAAAAAAAACWgHFAAAAAAAAAAAAAAAAAQAR42QAAAABAAAAAKbdcPZWJDnyobf8vLA0yzsyL/OhE/auq2J4dfD3phJMAAAAAVRGVAAAAAAAOfxkG3qLTLHrhsPS6JsSUB7+ZjU/J4oT1YBMKb/3n2QAAAACYJA8gH//////////AAAAAQAAAAEAAAAAAAAAAAAAAAJUC+QAAAAAAAAAAAAAAAAA', 'fee_meta_xdr': 'AAAAAgAAAAMAEeK4AAAAAAAAAACm3XD2ViQ58qG3/LywNMs7Mi/zoRP2rqtieHXw96YSTAAAABdIdt10ABEtkAAAABsAAAAFAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAABAAAAA+Z3iUIAAAAAAAAAAAAAAAAAAAAAAAAAAQAR42QAAAAAAAAAAKbdcPZWJDnyobf8vLA0yzsyL/OhE/auq2J4dfD3phJMAAAAF0h23RAAES2QAAAAGwAAAAUAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAEAAAAD5neJQgAAAAAAAAAAAAAAAAAAAAA=', 'memo_type': 'none', 'signatures': ['wnT7iemvzf5DlTLmXCmTdDpcDrL4d6G0jvpKBD78xku+yAlmneP69lwcTGFDir5m+H5zqBlGshjxAUJSwrhQAA=='], 'valid_after': '1970-01-01T00:00:00Z', 'valid_before': '2020-07-12T09:29:08Z'}

```
