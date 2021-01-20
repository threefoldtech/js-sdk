### test_01_submit_payment

Test Case for submit payment

**Test Scenario**
- Submit payment to destination wallet
- Check that payment is submitted

### test_02_wait_payment

Test Case for wait after submit a payment with expire time

**Test Scenario**
- Submit payment to destination wallet expire within 1 min
- Check if it wait for 1 min or not

### test_03_refund_failed_payments

Test Case for refund after failed payment

**Test Scenario**
- Submit a payment with amount of 2 TFT to destination wallet
- Get current balance of source wallet before transfer
- Transfer only 1.1 TFT from source wallet
- Refund failed payment to source wallet
- Check if the source wallet refunded correctly

### test_04_issue_refund

Test Case for issue refund

**Test Scenario**
- Submit a payment with amount of 1 TFT to destination wallet
- Get current balance of source wallet before transfer
- Transfer 1 TFT from source wallet
- Issue refund for success payment to source wallet
- Check if the source wallet refunded correctly

### test_05_issue_refund_with_specific_amount

Test Case for issue refund with specific amount

**Test Scenario**
- Submit a payment with amount of 2 TFT to destination wallet
- Get current balance of source wallet before transfer
- Transfer 2 TFT from source wallet
- Issue refund for success payment to source wallet with amount of 1 TFT
- Check if the source wallet refunded correctly

### test_06_check_refund

Test Case for check refund

**Test Scenario**
- Submit a payment with amount of 1 TFT to destination wallet
- Issue refund
- Check if check_refund returns refund state

### test_07_check_refund_raise_error

Test Case for check refund raised error if no refund requested

**Test Scenario**
- Submit a payment with amount of 1 TFT to destination wallet
- Check if check_refund raise error because no refund requested

### test_08_process_refunds

Test Case for process refunds

**Test Scenario**
- Submit a payment with amount of 1 TFT to destination wallet
- Transfer 1 TFT from source wallet
- Issue refund for success payment to source wallet
- Check if refund success state is False
- Run process_refunds
- Check if refund success state is True

### test_09_process_payments

Test Case for process payments

**Test Scenario**
- Submit a payment with amount of 1 TFT to destination wallet
- Check that payment is submitted and success state False
- Transfer 1 TFT from source wallet
- Run process_payments
- Check that payment success state True

### test_10_refund_extra

Test case for refund extra payments

**Test Scenario**
- Submit a payment with amount of 1 TFT to destination wallet
- Get source wallet balance
- Transfer 2 TFT from source wallet
- Run refund_extra
- Get source wallet balance
- Check if refund_extra return correct amount

### test_11_refund_extra_set_false

Test case for refund extra payments and set refund_extra False

**Test Scenario**
- Submit a payment with amount of 1 TFT to destination wallet with refund_extra flag equals False
- Transfer 2 TFT from source wallet
- Get source wallet balance
- Run refund_extra
- Get source wallet balance
- Check if balance not changed
