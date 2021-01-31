import gevent
from tests.base_tests import BaseTests
import pytest
from jumpscale.loader import j
from solutions_automation.vdc import deployer
from tests.sals.vdc.vdc_base import VDCBase
from parameterized import parameterized_class


# @parameterized_class(("flavor"), [("silver",), ("gold",), ("platinum",), ("diamond",)])
@pytest.mark.integration
class VDCChatflows(VDCBase):
    flavor = "silver"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        wallet = j.clients.stellar.get("demotest_wallets_wallet")
        cls.vdc.provision_wallet.merge_into_account(wallet.address)
        cls.vdc.prepaid_wallet.merge_into_account(wallet.address)
        super().tearDownClass()

    def test_01_deploy_vdc(self):
        """Test case for deploying a VDC.

        **Test Scenario**

        - Deploy a VDC.
        - Check that VDC is reachable.
        """

        self.info("Deploy a VDC")
        vdc_name = self.random_name()
        password = self.random_string()
        vdc = deployer.deploy_vdc(vdc_name, password, self.flavor.upper())

        self.info("Check that VDC is reachable")
        request = j.tools.http.get(f"http://{vdc.domain}", verify=False, timeout=60)
        self.assertEqual(request.status_code, 200)
