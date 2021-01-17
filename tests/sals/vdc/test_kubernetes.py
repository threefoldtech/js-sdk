import pytest
from jumpscale.loader import j
from parameterized import parameterized_class

from .vdc_base import VDCBase


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
    def deploy_vdc(cls):
        cls.vdc_name = cls.random_name()
        cls.password = cls.random_string()
        cls.vdc = j.sals.vdc.new(cls.vdc_name, cls.tname, cls.flavor)

        cls.info("Transfer needed TFT to deploy vdc for an hour to the provisioning wallet.")
        vdc_price = j.tools.zos.consumption.calculate_vdc_price(cls.flavor)
        needed_tft = float(vdc_price) / 24 / 30 + 0.2  # 0.2 transaction fees for creating the pool and extend it
        cls.vdc.transfer_to_provisioning_wallet(needed_tft, "test_wallet")

        cls.info("Deploy VDC.")
        deployer = cls.vdc.get_deployer(password=cls.password)
        minio_ak = cls.random_name()
        minio_sk = cls.random_string()
        kube_config = deployer.deploy_vdc(minio_ak, minio_sk)
        return kube_config

    @classmethod
    def tearDownClass(cls):
        # j.sals.vdc.delete(cls.vdc.instance_name) Todo: Uncomment before merging with development_vdc
        super().tearDownClass()

    def test_01_add_helm_hepo(self):
        pass
