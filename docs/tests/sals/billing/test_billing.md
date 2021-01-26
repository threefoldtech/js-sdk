### test_01_submit_payment

Test Case for submitting payment.

**Test Scenario**
- Submit payment to destination wallet.
- Check that payment is submitted.

### test_02_wait_payment

Test Case for waiting after submitting a payment with an expiration time.

**Test Scenario**
- Submit payment to destination wallet expire within 1 or 2 min.
- Check if it waits for 1 min or not.

### test_03_refund_failed_payments

Test Case for refunding after a failed payment.

**Test Scenario**
- Submit a payment with an amount of 2 TFT to the destination wallet.
- Get the current balance of the source wallet before the transfer.
- Transfer only 1.1 TFT from the source wallet.
- Refund failed payment to source wallet.
- Check if the source wallet has been refunded correctly.

### test_04_issue_refund

Test Case for issuing a refund.

**Test Scenario**
- Submit a payment with an amount of 1 TFT to the destination wallet.
- Get the current balance of the source wallet before the transfer.
- Transfer 1 TFT from the source wallet.
- Issue a refund for success payment to source wallet.
- Check if the source wallet refunded correctly.

### test_05_issue_refund_with_specific_amount

Test Case for issue refund with a specific amount.

**Test Scenario**
- Submit a payment with an amount of 2 TFT to the destination wallet.
- Get current the balance of the source wallet before the transfer.
- Transfer 2 TFT from source wallet.
- Issue refund for success payment to source wallet with an amount of 1 TFT.
- Check if the source wallet refunded correctly.

### test_06_check_refund

Test Case for checking refund.

**Test Scenario**
- Submit a payment with an amount of 1 TFT to destination wallet.
- Issue refund.
- Check if check_refund returns refund state.

### test_07_check_refund_raise_error

Test Case for check refund raised an error if no refund requested.

**Test Scenario**
- Submit a payment with an amount of 1 TFT to the destination wallet.
- Check if check_refund raises an error because no refund requested.

### test_08_process_refunds

Test Case for processing refunds.

**Test Scenario**
- Submit a payment with an amount of 1 TFT to the destination wallet.
- Transfer 1 TFT from the source wallet.
- Issue refund for success payment to the source wallet.
- Check if the refund success state is False.
- Run process_refunds.
- Check if the refund success state is True.

### test_09_process_payments

Test Case for processing payments.

**Test Scenario**
- Submit a payment with an amount of 1 TFT to the destination wallet.
- Check that payment is submitted and success state False.
- Transfer 1 TFT from the source wallet.
- Run process_payments.
- Check that payment success state True.

### test_10_refund_extra

Test case for refunding extra payments.

**Test Scenario**
- Submit a payment with an amount of 1 TFT to the destination wallet.
- Get the source wallet balance.
- Transfer 2 TFT from the source wallet.
- Run refund_extra.
- Get the source wallet balance.
- Check if refund_extra returns the correct amount.

### test_11_refund_extra_set_false

Test case for refunding extra payments and set refund_extra False.

**Test Scenario**
- Submit a payment with an amount of 1 TFT to destination wallet with refund_extra flag equals False.
- Transfer 2 TFT from the source wallet.
- Get the source wallet balance.
- Run refund_extra.
- Get the source wallet balance.
- Check if the balance not changed.
