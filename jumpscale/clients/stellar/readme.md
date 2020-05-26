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
