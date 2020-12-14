from jumpscale.loader import j


# underpayment. need refund
client_wallet = j.clients.stellar.vdcinit
dst_wallet = j.clients.stellar.test

payment_id, memo_text = j.sals.billing.submit_payment(amount=10, wallet_name=dst_wallet.instance_name, expiry=1)

a = client_wallet.get_asset()
transaction_hash = client_wallet.transfer(
    dst_wallet.address, amount=9, memo_text=memo_text, asset=f"{a.code}:{a.issuer}"
)
j.sals.billing.process_payments()
result = j.sals.billing.wait_payment(payment_id)
assert result == False
j.sals.billing.refund_failed_payments()

refund_transaction = client_wallet.list_transactions()[-1]
transaction_effect = client_wallet.get_transaction_effects(refund_transaction.hash)[0]
assert float(transaction_effect.amount) == 8.9


# success payment. no refunds
client_wallet = j.clients.stellar.vdcinit
dst_wallet = j.clients.stellar.test

payment_id, memo_text = j.sals.billing.submit_payment(amount=10, wallet_name=dst_wallet.instance_name)

a = client_wallet.get_asset()
transaction_hash = client_wallet.transfer(
    dst_wallet.address, amount=10, memo_text=memo_text, asset=f"{a.code}:{a.issuer}"
)
j.sals.billing.process_payments()
result = j.sals.billing.wait_payment(payment_id)
assert result == True


# refund previous successful payment
j.sals.billing.issue_refund(payment_id)
j.sals.billing.process_refunds()

refund_transaction = client_wallet.list_transactions()[-1]
transaction_effect = client_wallet.get_transaction_effects(refund_transaction.hash)[0]
assert float(transaction_effect.amount) == 9.9
