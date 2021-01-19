import os
import pytest
import time
from jumpscale.loader import j
from tests.base_tests import BaseTests
from jumpscale.sals.billing.models import PAYMENT_FACTORY, REFUND_FACTORY


@pytest.mark.integration
class TestBilling(BaseTests):
    @classmethod
    def setUpClass(cls):
        cls._get_env_vars()
        cls._setup_wallets()

    @classmethod
    def tearDownClass(cls):
        # TODO: Return TFT to Mainnet Wallet

        # # Delete two wallets
        # j.clients.stellar.delete("testing_source_wallet")
        # j.clients.stellar.delete("test_destination_wallet")
        pass

    @classmethod
    def _get_env_vars(cls):
        """Get enviroment variables

        Raises:
            ValueError: Error raised if enviroment variable not found
        """
        needed_vars = ["SOURCE_WALLET_SECRET", "DESTINATION_WALLET_SECRET"]
        for var in needed_vars:
            value = os.environ.get(var)
            if not value:
                raise ValueError(f"Please add {var} as environment variables")
            setattr(cls, var.lower(), value)

    @classmethod
    def _setup_wallets(cls):
        """Create wallets and asset instance
        """
        cls.test_source_wallet = j.clients.stellar.new("testing_source_wallet", secret=cls.source_wallet_secret)
        cls.test_destination_wallet = j.clients.stellar.new(
            "test_destination_wallet", secret=cls.destination_wallet_secret
        )
        cls.asset = cls.test_source_wallet._get_asset()

    def test_01_submit_payment(self):
        """Test Case for submit payment

        **Test Scenario**
        - Submit payment to destination wallet
        - Check that payment is submited
        """
        # import ipdb; ipdb.set_trace()
        self.info("Submit payment to destination wallet")
        payment_id, memo_text = j.sals.billing.submit_payment(
            amount=1, wallet_name=self.test_destination_wallet.instance_name, expiry=1
        )
        self.info("Check if payment is active")
        payment_instance = PAYMENT_FACTORY.find_by_id(payment_id)
        self.assertEqual(payment_instance.memo_text, memo_text, "Payment is not submitted")

    def test_02_wait_payment(self):
        """Test Case for wait after submit a payment with expire time

        **Test Scenario**
        - Submit payment to destination wallet expire within 1 min
        - Check if it wait for 1 min or not
        """
        self.info("Submit payment to destination wallet expire within 1 min")
        expire_time = 1
        payment_id, memo_text = j.sals.billing.submit_payment(
            amount=1, wallet_name=self.test_destination_wallet.instance_name, expiry=expire_time
        )
        start_wait = time.time()
        wait_time = 0
        self.info("Check if it wait for 1 min or not")
        if j.sals.billing.wait_payment(payment_id) == False:
            wait_time = time.time() - start_wait

        wait_time = round(wait_time / 60)

        self.assertEqual(wait_time, 1, f"Function wait {wait_time} min but expected 1 min")

    def test_03_refund_failed_payments(self):
        """[summary]

        **Test Scenario**
        """
        pass

    def test_04_issue_refund(self):
        """[summary]
        """
        pass

    def test_05_check_refund(self):
        """[summary]

        **Test Scenario**
        """
        pass

    def test_06_process_refunds(self):
        """[summary]

        **Test Scenario**
        """
        pass

    def test_07_process_payments(self):
        """[summary]

        **Test Scenario**
        """
        pass

    def test_08_refund_extra(self):
        """[summary]

        **Test Scenario**
        """
        pass


# # underpayment. need refund
# payment_id, memo_text = j.sals.billing.submit_payment(amount=10, wallet_name=self.test_destination_wallet.instance_name, expiry=1)

# transaction_hash = self.test_source_wallet.transfer(
#     self.test_destination_wallet.address, amount=9, memo_text=memo_text, asset=f"{a.code}:{a.issuer}"
# )
# j.sals.billing.process_payments()
# result = j.sals.billing.wait_payment(payment_id)
# assert result == False
# j.sals.billing.refund_failed_payments()

# refund_transaction = self.test_source_wallet.list_transactions()[-1]
# transaction_effect = self.test_source_wallet.get_transaction_effects(refund_transaction.hash)[0]
# assert float(transaction_effect.amount) == 8.9


# # success payment. refund extra paid

# payment_id, memo_text = j.sals.billing.submit_payment(amount=10, wallet_name=self.test_destination_wallet.instance_name)

# a = self.test_source_wallet._get_asset()
# transaction_hash = self.test_source_wallet.transfer(
#     self.test_destination_wallet.address, amount=12, memo_text=memo_text, asset=f"{a.code}:{a.issuer}"
# )
# j.sals.billing.process_payments()
# result = j.sals.billing.wait_payment(payment_id)
# assert result == True


# # refund previous successful payment
# j.sals.billing.issue_refund(payment_id)
# j.sals.billing.process_refunds()

# refund_transaction = self.test_source_wallet.list_transactions()[-1]
# transaction_effect = self.test_source_wallet.get_transaction_effects(refund_transaction.hash)[0]
# assert float(transaction_effect.amount) == 9.9


# # test extra paid refund
# j.sals.billing.refund_extra()

# refund_transaction = self.test_source_wallet.list_transactions()[-1]
# transaction_effect = self.test_source_wallet.get_transaction_effects(refund_transaction.hash)[0]
# assert float(transaction_effect.amount) == 1.9


# # two payments
# payment_id, memo_text = j.sals.billing.submit_payment(amount=10, wallet_name=self.test_destination_wallet.instance_name, expiry=2)

# a = self.test_source_wallet._get_asset()
# transaction_hash = self.test_source_wallet.transfer(
#     self.test_destination_wallet.address, amount=9, memo_text=memo_text, asset=f"{a.code}:{a.issuer}"
# )
# transaction_hash = self.test_source_wallet.transfer(
#     self.test_destination_wallet.address, amount=10, memo_text=memo_text, asset=f"{a.code}:{a.issuer}"
# )
# j.sals.billing.process_payments()
# result = j.sals.billing.wait_payment(payment_id)
# assert result == True
# j.sals.billing.refund_failed_payments()

# refund_transaction = self.test_source_wallet.list_transactions()[-1]
# transaction_effect = self.test_source_wallet.get_transaction_effects(refund_transaction.hash)[0]
# assert float(transaction_effect.amount) == 8.9


# # refund extra payment with refund_extra as false

# payment_id, memo_text = j.sals.billing.submit_payment(
#     amount=10, wallet_name=self.test_destination_wallet.instance_name, refund_extra=False
# )

# a = self.test_source_wallet._get_asset()
# transaction_hash = self.test_source_wallet.transfer(
#     self.test_destination_wallet.address, amount=12, memo_text=memo_text, asset=f"{a.code}:{a.issuer}"
# )
# j.sals.billing.process_payments()
# result = j.sals.billing.wait_payment(payment_id)
# assert result == True

# j.sals.billing.issue_refund(payment_id)
# j.sals.billing.process_refunds()

# refund_transaction = self.test_source_wallet.list_transactions()[-1]
# transaction_effect = self.test_source_wallet.get_transaction_effects(refund_transaction.hash)[0]
# assert float(transaction_effect.amount) == 11.9


# # refund with specific amount
# payment_id, memo_text = j.sals.billing.submit_payment(
#     amount=10, wallet_name=self.test_destination_wallet.instance_name, refund_extra=False
# )

# a = self.test_source_wallet._get_asset()
# transaction_hash = self.test_source_wallet.transfer(
#     self.test_destination_wallet.address, amount=12, memo_text=memo_text, asset=f"{a.code}:{a.issuer}"
# )
# j.sals.billing.process_payments()
# result = j.sals.billing.wait_payment(payment_id)
# assert result == True

# j.sals.billing.issue_refund(payment_id, amount=9)
# j.sals.billing.process_refunds()

# refund_transaction = self.test_source_wallet.list_transactions()[-1]
# transaction_effect = self.test_source_wallet.get_transaction_effects(refund_transaction.hash)[0]
# assert float(transaction_effect.amount) == 8.9
