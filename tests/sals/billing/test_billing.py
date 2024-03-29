import os
import time
from random import randint

import pytest
from jumpscale.clients.stellar import TRANSACTION_FEES
from jumpscale.loader import j
from jumpscale.sals.billing.models import PAYMENT_FACTORY, REFUND_FACTORY
from tests.base_tests import BaseTests


@pytest.mark.integration
class TestBilling(BaseTests):
    @classmethod
    def setUpClass(cls):
        cls.info("Setup all requirements")
        cls._get_env_vars()
        cls._setup_wallets()
        cls.payment_ids = []
        cls.refund_ids = []

    @classmethod
    def tearDownClass(cls):
        cls.info("Clean-up and teardown")
        destination_wallet_balance = round(cls.test_destination_wallet.get_balance_by_asset() - TRANSACTION_FEES, 6)
        if destination_wallet_balance > 0:
            cls.info(f"Transfer all TFT from destination wallet")
            transaction_hash = cls.test_destination_wallet.transfer(
                cls.test_source_wallet.address,
                amount=destination_wallet_balance,
                asset=f"{cls.asset.code}:{cls.asset.issuer}",
            )

            cls.info("Check if destination wallet is empty")
            assert round(cls.test_destination_wallet.get_balance_by_asset()) == 0

        cls.info("Delete all payment instances")
        for id in cls.payment_ids:
            PAYMENT_FACTORY.delete(f"payment_{id}")

        cls.info("Delete all refund instances")
        for id in cls.refund_ids:
            REFUND_FACTORY.delete(f"refund_{id}")

    @classmethod
    def _get_env_vars(cls):
        """Get environment variables

        Raises:
            ValueError: Error raised if environment variable not found
        """
        cls.info("Get needed environment variables")
        needed_vars = ["SOURCE_WALLET_SECRET", "DESTINATION_WALLET_SECRET"]
        for var in needed_vars:
            value = os.environ.get(var)
            if not value:
                raise ValueError(f"Please add {var} as environment variables")
            setattr(cls, var.lower(), value)

    @classmethod
    def _setup_wallets(cls):
        """Create wallets and asset instance
        In this test, 2 wallets used
        - Source wallet: Wallet that sends TFT.
        - Destination wallet: Wallet that receives TFT.
        """
        cls.info("Setup wallets for testing")
        cls.test_source_wallet = j.clients.stellar.new("testing_source_wallet", secret=cls.source_wallet_secret)
        cls.test_destination_wallet = j.clients.stellar.new(
            "test_destination_wallet", secret=cls.destination_wallet_secret
        )
        cls.asset = cls.test_source_wallet._get_asset()

    def test_01_submit_payment(self):
        """Test Case for submitting payment.

        **Test Scenario**
        - Submit payment to destination wallet.
        - Check that payment is submitted.
        """
        self.info("Submit payment to destination wallet")
        payment_id, memo_text = j.sals.billing.submit_payment(
            amount=1, wallet_name=self.test_destination_wallet.instance_name, expiry=1
        )
        self.payment_ids.append(payment_id)

        self.info("Check if payment is active")
        payment_instance = PAYMENT_FACTORY.find_by_id(payment_id)
        self.assertEqual(payment_instance.memo_text, memo_text, "Payment is not submitted")

    def test_02_wait_payment(self):
        """Test Case for waiting after submitting a payment with an expiration time.

        **Test Scenario**
        - Submit payment to destination wallet expire within 1 or 2 min.
        - Check if it waits for 1 min or not.
        """
        self.info("Submit payment to destination wallet expire within 1 or 2 min")
        expire_time = randint(1, 2)
        payment_id, memo_text = j.sals.billing.submit_payment(
            amount=1, wallet_name=self.test_destination_wallet.instance_name, expiry=expire_time
        )
        self.payment_ids.append(payment_id)
        start_wait = time.time()
        wait_time = 0

        self.info(f"Check if it waits for {expire_time} min or not")
        if j.sals.billing.wait_payment(payment_id) == False:
            wait_time = time.time() - start_wait
        wait_time = round(wait_time / 60)
        self.assertEqual(wait_time, expire_time, f"Function wait {wait_time} min but expected {expire_time} min")

    def test_03_refund_failed_payments(self):
        """Test Case for refunding after a failed payment.

        **Test Scenario**
        - Submit a payment with an amount of 2 TFT to the destination wallet.
        - Get the current balance of the source wallet before the transfer.
        - Transfer only 1.1 TFT from the source wallet.
        - Refund failed payment to source wallet.
        - Check if the source wallet has been refunded correctly.
        """
        payment_amount = 2.0
        transfer_amount = 1.1
        self.info("Submit a payment with amount of 2 TFT to destination wallet")
        payment_id, memo_text = j.sals.billing.submit_payment(
            amount=payment_amount, wallet_name=self.test_destination_wallet.instance_name, expiry=1
        )
        self.payment_ids.append(payment_id)
        self.refund_ids.append(payment_id)

        self.info("Get current balance of source wallet")
        balance_before_transfer = self.test_source_wallet.get_balance_by_asset()

        self.info("Transfer 1.1 TFT from source wallet")
        transaction_hash = self.test_source_wallet.transfer(
            self.test_destination_wallet.address,
            amount=transfer_amount,
            memo_text=memo_text,
            asset=f"{self.asset.code}:{self.asset.issuer}",
        )
        j.sals.billing.process_payments()

        self.info("Check if payment failed")
        self.assertFalse(j.sals.billing.wait_payment(payment_id), "This payment must be failed")

        self.info("Refund failed payment to source wallet")
        j.sals.billing.refund_failed_payments()

        self.info("Check if the source wallet refunded correctly")
        # Get balance after refund
        balance_after_refund = self.test_source_wallet.get_balance_by_asset()
        # Check if the difference between two balances is 2 TRANSACTION_FEES.
        self.assertAlmostEqual(balance_before_transfer - balance_after_refund, 2 * TRANSACTION_FEES)

    def test_04_issue_refund(self):
        """Test Case for issuing a refund.

        **Test Scenario**
        - Submit a payment with an amount of 1 TFT to the destination wallet.
        - Get the current balance of the source wallet before the transfer.
        - Transfer 1 TFT from the source wallet.
        - Issue a refund for success payment to source wallet.
        - Check if the source wallet refunded correctly.
        """
        payment_amount = 1.0
        transfer_amount = 1.0

        self.info("Submit a payment with amount of 1 TFT to destination wallet")
        payment_id, memo_text = j.sals.billing.submit_payment(
            amount=payment_amount, wallet_name=self.test_destination_wallet.instance_name, expiry=1
        )
        self.payment_ids.append(payment_id)
        self.refund_ids.append(payment_id)

        self.info("Get current balance of source wallet")
        balance_before_transfer = self.test_source_wallet.get_balance_by_asset()

        self.info("Transfer 1 TFT from source wallet")
        transaction_hash = self.test_source_wallet.transfer(
            self.test_destination_wallet.address,
            amount=transfer_amount,
            memo_text=memo_text,
            asset=f"{self.asset.code}:{self.asset.issuer}",
        )
        j.sals.billing.process_payments()

        self.info("Check if payment success")
        self.assertTrue(j.sals.billing.wait_payment(payment_id), "This payment must be success")

        self.info("Issue refund for the success payment to source wallet")
        j.sals.billing.issue_refund(payment_id)
        j.sals.billing.process_refunds()

        self.info("Check if the source wallet refunded correctly")
        # Get balance after refund
        balance_after_refund = self.test_source_wallet.get_balance_by_asset()
        # Check if the difference between two balances is 2 TRANSACTION_FEES.
        self.assertAlmostEqual(balance_before_transfer - balance_after_refund, 2 * TRANSACTION_FEES)

    def test_05_issue_refund_with_specific_amount(self):
        """Test Case for issue refund with a specific amount.

        **Test Scenario**
        - Submit a payment with an amount of 2 TFT to the destination wallet.
        - Get current the balance of the source wallet before the transfer.
        - Transfer 2 TFT from source wallet.
        - Issue refund for success payment to source wallet with an amount of 1 TFT.
        - Check if the source wallet refunded correctly.
        """
        payment_amount = 2.0
        transfer_amount = 2.0
        refund_amount = 1.0

        self.info("Submit a payment with amount of 2 TFT to destination wallet")
        payment_id, memo_text = j.sals.billing.submit_payment(
            amount=payment_amount, wallet_name=self.test_destination_wallet.instance_name, expiry=1
        )
        self.payment_ids.append(payment_id)
        self.refund_ids.append(payment_id)

        self.info("Get current balance of source wallet")
        balance_before_transfer = self.test_source_wallet.get_balance_by_asset()

        self.info("Transfer 1 TFT from source wallet")
        transaction_hash = self.test_source_wallet.transfer(
            self.test_destination_wallet.address,
            amount=transfer_amount,
            memo_text=memo_text,
            asset=f"{self.asset.code}:{self.asset.issuer}",
        )
        j.sals.billing.process_payments()

        self.info("Check if payment success")
        self.assertTrue(j.sals.billing.wait_payment(payment_id), "This payment must be success")

        self.info("Issue refund for the success payment to source wallet")
        j.sals.billing.issue_refund(payment_id, amount=refund_amount)
        j.sals.billing.process_refunds()

        self.info("Check if the source wallet refunded correctly")
        # Get balance after refund
        balance_after_refund = self.test_source_wallet.get_balance_by_asset()
        # Check if the difference between two balances is 2 TRANSACTION_FEES.
        self.assertAlmostEqual(balance_before_transfer - balance_after_refund, refund_amount + 2 * TRANSACTION_FEES)

    def test_06_check_refund(self):
        """Test Case for checking refund.

        **Test Scenario**
        - Submit a payment with an amount of 1 TFT to destination wallet.
        - Issue refund.
        - Check if check_refund returns refund state.
        """
        self.info("Submit a payment with amount of 1 TFT to destination wallet")
        payment_id, memo_text = j.sals.billing.submit_payment(
            amount=1, wallet_name=self.test_destination_wallet.instance_name, expiry=1
        )
        self.payment_ids.append(payment_id)
        self.refund_ids.append(payment_id)

        self.info("Issue Refund")
        j.sals.billing.issue_refund(payment_id)

        self.info("Check if check_refund returns refund state")
        # Returned result will be False as refund not completed because no transfer happen
        # No transfer happen to save TFT transaction fees
        self.assertFalse(j.sals.billing.check_refund(payment_id))

    def test_07_check_refund_raise_error(self):
        """Test Case for check refund raised an error if no refund requested.

        **Test Scenario**
        - Submit a payment with an amount of 1 TFT to the destination wallet.
        - Check if check_refund raises an error because no refund requested.
        """
        self.info("Submit a payment with amount of 1 TFT to destination wallet")
        payment_id, memo_text = j.sals.billing.submit_payment(
            amount=1, wallet_name=self.test_destination_wallet.instance_name, expiry=1
        )
        self.payment_ids.append(payment_id)

        self.info("Check if check_refund raise error because no refund requested")
        with self.assertRaises(j.exceptions.Input):
            j.sals.billing.check_refund(payment_id)

    def test_08_process_refunds(self):
        """Test Case for processing refunds.

        **Test Scenario**
        - Submit a payment with an amount of 1 TFT to the destination wallet.
        - Transfer 1 TFT from the source wallet.
        - Issue refund for success payment to the source wallet.
        - Check if the refund success state is False.
        - Run process_refunds.
        - Check if the refund success state is True.
        """
        self.info("Submit a payment with amount of 1 TFT to destination wallet")
        payment_id, memo_text = j.sals.billing.submit_payment(
            amount=1, wallet_name=self.test_destination_wallet.instance_name, expiry=1
        )
        self.payment_ids.append(payment_id)
        self.refund_ids.append(payment_id)

        self.info("Transfer 1 TFT from source wallet")
        transaction_hash = self.test_source_wallet.transfer(
            self.test_destination_wallet.address,
            amount=1,
            memo_text=memo_text,
            asset=f"{self.asset.code}:{self.asset.issuer}",
        )
        j.sals.billing.process_payments()
        self.assertTrue(j.sals.billing.wait_payment(payment_id), "This payment must be success")

        self.info("Issue refund for the success payment to source wallet")
        j.sals.billing.issue_refund(payment_id)
        refund_instance = REFUND_FACTORY.find(f"refund_{payment_id}")
        self.assertFalse(refund_instance.success)

        self.info("Check if process_refunds update all refund requests")
        j.sals.billing.process_refunds()
        # Update refund_instance after process_refund
        refund_instance = REFUND_FACTORY.find(f"refund_{payment_id}")
        self.assertTrue(refund_instance.success)

    def test_09_process_payments(self):
        """Test Case for processing payments.

        **Test Scenario**
        - Submit a payment with an amount of 1 TFT to the destination wallet.
        - Check that payment is submitted and success state False.
        - Transfer 1 TFT from the source wallet.
        - Run process_payments.
        - Check that payment success state True.
        """
        self.info("Submit a payment with amount of 1 TFT to destination wallet")
        payment_id, memo_text = j.sals.billing.submit_payment(
            amount=1, wallet_name=self.test_destination_wallet.instance_name, expiry=1
        )
        self.payment_ids.append(payment_id)
        payment_instance = PAYMENT_FACTORY.find_by_id(payment_id)

        self.info("Check that payment is submitted and success state False")
        self.assertFalse(payment_instance.result.success)

        self.info("Transfer 1 TFT from source wallet")
        transaction_hash = self.test_source_wallet.transfer(
            self.test_destination_wallet.address,
            amount=1,
            memo_text=memo_text,
            asset=f"{self.asset.code}:{self.asset.issuer}",
        )

        self.info("Run process_payments")
        j.sals.billing.process_payments()

        self.info("Check that payment success state True")
        payment_instance = PAYMENT_FACTORY.find_by_id(payment_id)
        self.assertTrue(payment_instance.result.success)

    def test_10_refund_extra(self):
        """Test case for refunding extra payments.

        **Test Scenario**
        - Submit a payment with an amount of 1 TFT to the destination wallet.
        - Get the source wallet balance.
        - Transfer 2 TFT from the source wallet.
        - Run refund_extra.
        - Get the source wallet balance.
        - Check if refund_extra returns the correct amount.
        """
        self.info("Submit a payment with amount of 1 TFT to destination wallet")
        payment_id, memo_text = j.sals.billing.submit_payment(
            amount=1, wallet_name=self.test_destination_wallet.instance_name, expiry=1
        )
        self.payment_ids.append(payment_id)
        self.refund_ids.append(payment_id)
        payment_instance = PAYMENT_FACTORY.find_by_id(payment_id)

        self.info("Get current balance of source wallet")
        balance_before_transfer = self.test_source_wallet.get_balance_by_asset()

        self.info("Transfer 2 TFT from source wallet")
        transaction_hash = self.test_source_wallet.transfer(
            self.test_destination_wallet.address,
            amount=2,
            memo_text=memo_text,
            asset=f"{self.asset.code}:{self.asset.issuer}",
        )
        j.sals.billing.process_payments()

        self.info("Run refund_extra")
        j.sals.billing.refund_extra()

        self.info("Get current balance of source wallet")
        balance_after_refund = self.test_source_wallet.get_balance_by_asset()

        self.info("Check if refund_extra return correct amount")
        self.assertAlmostEqual(
            balance_after_refund, balance_before_transfer - payment_instance.amount - 2 * TRANSACTION_FEES
        )

    def test_11_refund_extra_set_false(self):
        """Test case for refunding extra payments and set refund_extra False.

        **Test Scenario**
        - Submit a payment with an amount of 1 TFT to destination wallet with refund_extra flag equals False.
        - Transfer 2 TFT from the source wallet.
        - Get the source wallet balance.
        - Run refund_extra.
        - Get the source wallet balance.
        - Check if the balance not changed.
        """
        self.info("Submit a payment with amount of 1 TFT to destination wallet")
        payment_id, memo_text = j.sals.billing.submit_payment(
            amount=1, wallet_name=self.test_destination_wallet.instance_name, expiry=1, refund_extra=False
        )
        self.payment_ids.append(payment_id)
        self.refund_ids.append(payment_id)

        self.info("Transfer 2 TFT from source wallet")
        transaction_hash = self.test_source_wallet.transfer(
            self.test_destination_wallet.address,
            amount=2,
            memo_text=memo_text,
            asset=f"{self.asset.code}:{self.asset.issuer}",
        )
        j.sals.billing.process_payments()

        self.info("Get current balance of source wallet")
        balance_before_refund = self.test_source_wallet.get_balance_by_asset()

        self.info("Run refund_extra")
        j.sals.billing.refund_extra()

        self.info("Get current balance of source wallet")
        balance_after_refund = self.test_source_wallet.get_balance_by_asset()

        self.info("Check if balance before and after refund not changed")
        self.assertEqual(balance_after_refund, balance_before_refund)
