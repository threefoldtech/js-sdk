import pytest
import urllib.request
from random import randint
from tests.frontend.tests.base_tests import BaseTest
from tests.frontend.pages.wallets.wallets import Wallets
from tests.frontend.pages.threebot_deployer.threebot_deployer import ThreebotDeployer


@pytest.mark.integration
class ThreebotDeployerTests(BaseTest):

    wallet_name = "wallet_{}".format(randint(1, 500))

    def setUp(self):
        super().setUp()
        # if not hasattr(ThreebotDeployerTests, "wallet_name"):
        self.wallet_name = self.random_name()
        self.create_wallet(self.wallet_name)

        self.threebot_deployer = ThreebotDeployer(self.driver)
        self.threebot_deployer.load()

    def tearDown(self):
        self.wallet_name = self.random_name()
        self.create_wallet(self.wallet_name)
        super().tearDown()

    def test01_deploy_and_delete_3bot(self):
        """
        Test case to test deploy and delete a 3bot instance

        **Test Scenario**
        #. Create a wallet.
        #. Create a threebot instance.
        #. Check that the threebot instance has been created successfully.
        #. Delete the threebot instance.
        #. Check that the threebot instance has been deleted successfully.
        #. Delete the wallet.
        """
        self.info("Create a wallet")

        self.info("Create a threebot instance")
        threebot_name = "threebot{}".format(randint(1, 1000))
        password = randint(1, 500000)
        threebot_instance_url = self.threebot_deployer.deploy_new_3bot(
            my_3bot_instances=threebot_name, password=password, wallet_name=self.wallet_name
        )

        self.info("Check that the threebot instance has been created successfully")
        self.assertEqual(urllib.request.urlopen(threebot_instance_url).getcode(), 200)

        my_3bot_instances = self.threebot_deployer.view_my_3bot("RUNNING")
        self.assertIn(threebot_name, my_3bot_instances)

        self.info("Delete the threebot instance")
        self.threebot_deployer.delete_threebot_instance(my_3bot_instances=threebot_name, password=password)

        self.info("Check that the threebot instance has been deleted successfully")
        my_3bot_instances = self.threebot_deployer.view_my_3bot("DELETED")
        self.assertIn(threebot_name, my_3bot_instances)

        self.info("Delete the wallet")

    def test02_start_and_stop_my_3bot_instance(self):
        """
        Test case to test start and stop a 3bot instance

        **Test Scenario**
        #. Create a wallet.
        #. Create a threebot instance.
        #. Stopped the new created 3bot instance.
        #. Check that the 3bot instance has been stopped successfully.
        #. Start the 3bot instance.
        #. Check that the 3bot instance has been started successfully.
        #. Delete the 3bot instance.
        #. Delete the wallet.
        """

        self.info("Create a wallet")

        self.info("Create a threebot instance")
        threebot_name = "threebot{}".format(randint(1, 1000))
        password = randint(1, 500000)
        self.threebot_deployer.deploy_new_3bot(
            my_3bot_instances=threebot_name, password=password, wallet_name=self.wallet_name
        )

        self.info("Stopped the new created 3bot instance")
        self.stop_running_3bot_instance(my_3bot_instance_name=threebot_name, password=password)

        self.info("Check that the 3bot instance has been stopped successfully")
        my_3bot_instances = self.threebot_deployer.view_my_3bot("STOPPED")
        self.assertIn(threebot_name, my_3bot_instances)

        self.info("Start the 3bot instance")
        threebot_instance_url = self.start_stopped_3bot_instance(
            my_3bot_instance_name=threebot_name, password=password, wallet_name=self.wallet_name
        )

        self.info("Check that the 3bot instance has been started successfully")
        self.assertEqual(urllib.request.urlopen(threebot_instance_url).getcode(), 200)
        my_3bot_instances = self.threebot_deployer.view_my_3bot("RUNNING")
        self.assertIn(threebot_name, my_3bot_instances)

        self.info("Delete the 3bot instance")
        self.threebot_deployer.delete_threebot_instance(my_3bot_instances=threebot_name, password=password)

        self.info("Delete the wallet")

    def create_wallet(self, wallet_name):
        self.info("Create a wallet")
        wallets = Wallets(self.driver)
        wallets.load()
        wallets.add_funded(wallet_name)

    def delete_wallet(self, wallet_name):
        self.info("Delete the wallet")
        wallets = Wallets(self.driver)
        wallets.load()
        wallets.delete(wallet_name)
