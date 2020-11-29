import pytest
from tests.frontend.pages.wallets.wallets import Wallets
from tests.frontend.tests.base_tests import BaseTest


@pytest.mark.integration
class WalletTests(BaseTest):
    def test_create_delete_wallet(self):
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
