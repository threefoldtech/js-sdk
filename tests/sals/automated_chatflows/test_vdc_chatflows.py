import gevent
from tests.base_tests import BaseTests
import pytest
from jumpscale.loader import j
from solutions_automation.vdc import deployer
from tests.sals.vdc.vdc_base import VDCBase
from parameterized import parameterized_class


@parameterized_class(("flavor"), [("silver",), ("gold",), ("platinum",), ("diamond",)])
@pytest.mark.integration
class VDCChatflows(VDCBase):
    flavor = "silver"

    def tearDown(self):

        self.info("Delete a VDC")
        j.sals.vdc.delete(self.vdc.vdc.instance_name)

        wallet = j.clients.stellar.get("demos_wallet")
        self.vdc.vdc.provision_wallet.merge_into_account(wallet.address)
        self.vdc.vdc.prepaid_wallet.merge_into_account(wallet.address)

    def test_01_deploy_vdc(self):
        """Test case for deploying a VDC.

        **Test Scenario**

        - Deploy a VDC.
        - Check that VDC is reachable.
        - Delete a VDC
        """

        self.info("Deploy a VDC")
        vdc_name = self.random_name().lower()
        password = self.random_string()
        self.vdc = deployer.deploy_vdc(vdc_name, password, self.flavor.upper())

        self.info("Check that VDC is reachable")
        request = j.tools.http.get(f"http://{vdc.vdc.threebot.domain}", timeout=60)
        self.assertEqual(request.status_code, 200)
