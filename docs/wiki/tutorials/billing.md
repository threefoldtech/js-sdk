# What is Billing Module?
Billing module manage payments and refund requests.

# Setup to Use Billing
To use billing module, you will need to create a wallet to submit a payment.

We will use `billing_wallet` through this tutorial to refer for the wallet.

You can create a wallet using stellar client as follow:

```python
billing_wallet = j.clients.stellar.new("billing_wallet")
```

# Billing Functionality

## Submit Payment

Submit payment with a certain value, expire time and destination wallet.

To submit a payment to *billing* wallet with amount of *10 TFT* and expire in *1 minute*.

```python
payment_id, memo_text =j.sals.billing.submit_payment(amount=10, wallet_name=billing_wallet.instance_name, expiry=1)
```

- memo text is very important to complete the transaction correctly.
- payment_id will be used in all next functions.

## Wait Payment

- Wait for the payment until it performed or been expired.
> Note that waiting time set in submit_payment as expiry argument

```python
is_waiting = j.sals.billing.wait_payment(payment_id)
```

- is_waiting `True` if the payment performed.
- is_waiting `False` if the payment expired.


## Refund Failed Payments
Sometimes payment maybe failed for many reasons, one of them if the paid amount less than the needed amount in the payment, refund this failed payment needed.

This function list all failed payments and refund it.

```python
j.sals.billing.refund_failed_payments()
```

## Issue Refund
In the previous case the payment failed,so we need a refund, but this is not the only case we need a refund, sometimes even after a successful payment, we need to refund.

This function will issue a refund request, it can refund the total amount of the payment or you can refund a certain amount.

```python
refund_total = j.sals.billing.issue_refund(payment_id) # Refund the total amount
refund_custom = j.sals.billing.issue_refund(payment_id, 1) # Refund custom amount 1 TFT
```

## Check Refund
After we issue a refund, we need to check the status of this request

```python
is_refunded = j.sals.billing.check_refund(payment_id)
```
- is_refunded `True` if the refund performed.
- is_refunded `False` if the refund not performed yet.

## Process Payments
List all active payments and apply it.

```python
j.sals.billing.process_payments()
```

## Process Refunds
List all active refunds and apply it.

```python
j.sals.billing.process_refunds()
```


## Refund Extra
List all active refund extra payment and apply it.

```python
j.sals.billing.refund_extra()
```
