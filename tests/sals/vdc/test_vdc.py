import pytest
from jumpscale.loader import j
from parameterized import parameterized_class

from .vdc_base import VDCBase


# @parameterized_class(("flavor"), [("silver",), ("gold",), ("platinum",), ("diamond",)])
@parameterized_class(("flavor"), [("silver",)])
@pytest.mark.integration
class TestVDC(VDCBase):
    flavor = "silver"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kube_config = cls.deploy_vdc()
        if not cls.kube_config:
            raise RuntimeError("VDC is not deployed")

    @classmethod
    def tearDownClass(cls):
        j.sals.vdc.delete(cls.vdc.instance_name)
        super().tearDownClass()

    def test_01_list_vdcs(self):
        """Test case for listing deployed vdcs.

        **Test Scenario**

        - Deploy VDC.
        - List deployed vdcs.
        - Check that the vdc has been deployed is in the list.
        """
        self.info("List deployed vdcs.")
        vdcs = j.sals.vdc.list(self.tname)

        self.info("Check that the vdc has been deployed is in the list.")
        found = False
        for vdc in vdcs:
            if vdc.vdc_name == self.vdc_name:
                found = True
                break
        self.assertTrue(found)
