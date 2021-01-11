import pytest
from tests.frontend.pages.wallets.wallets import Wallets
from tests.frontend.tests.base_tests import BaseTest


@pytest.mark.integration
@pytest.mark.skip("https://github.com/threefoldtech/js-sdk/issues/2062")
class WalletTests(BaseTest):
    def test01_create_delete_wallet(self):
        """Test case for creating a wallet and deleting it.

        **Test Scenario**

        - Create a wallet.
        - Check that the wallet has been created in the wallets cards.
        - Delete the wallet.
        - Check that the wallet has been deleted from the wallets cards.
        """
        self.info("Create a wallet.")
        wallet_name = self.random_name()
        wallets = Wallets(self.driver)
        wallets.load()
        wallets.create(wallet_name)

        self.info("Check that the wallet has been created in the wallets cards.")
        all_wallets = wallets.list()
        self.assertIn(wallet_name, all_wallets.keys())

        self.info("Delete the wallet.")
        wallets.delete(wallet_name)

        self.info("Check that the wallet has been deleted from the wallets cards.")
        all_wallets = wallets.list()
        self.assertNotIn(wallet_name, all_wallets.keys())

    def test02_add_funded_wallet(self):
        """Test case for creating a funded wallet and deleting it.

        **Test Scenario**
        - Create a funded wallet.
        - Check that the wallet has been created in the wallets cards.
        - Check the wallet balances.
        - Delete the wallet.
        - Check that the wallet has been deleted from the wallets cards.
        """
        self.info("Create a funded wallet.")
        wallet_name = self.random_name()
        wallets = Wallets(self.driver)
        wallets.load()
        wallets.add_funded(wallet_name)

        self.info("Check that the wallet has been created in the wallets cards.")
        all_wallets = wallets.list()
        self.assertIn(wallet_name, all_wallets.keys())

        self.info("Check the wallet balances")
        balances = wallets.get_balance(wallet_name)
        self.assertEqual(balances[0], "TFT 1000.0000000")
        self.assertEqual(balances[1], "XLM 9999.9999900")

        self.info("Delete the wallet.")
        wallets.delete(wallet_name)

        self.info("Check that the wallet has been deleted from the wallets cards.")
        all_wallets = wallets.list()
        self.assertNotIn(wallet_name, all_wallets.keys())

    def test03_import_wallet(self):
        """Test case for importing a wallet and deleting it.

        **Test Scenario**
        - Create a wallet.
        - Delete the wallet.
        - Import deleted wallet.
        - Check that the wallet has been imported.
        - Delete the wallet.
        """
        self.info("Create a wallet")
        wallet_name = self.random_name()
        wallets = Wallets(self.driver)
        wallets.load()
        wallets.create(wallet_name)
        wallet_secret = wallets.get_secret(wallet_name)

        self.info("Delete the wallet")
        wallets.delete(wallet_name)

        self.info("Import deleted wallet")
        wallets.import_(name=wallet_name, secret=wallet_secret, network="TEST")

        self.info(" Check that the wallet has been imported")
        all_wallets = wallets.list()
        self.assertNotIn(wallet_name, all_wallets.keys())

        self.info("Delete the wallet")
        wallets.delete(wallet_name)
