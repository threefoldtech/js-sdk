import pytest
from jumpscale.loader import j
from parameterized import parameterized_class

from .vdc_base import VDCBase


@parameterized_class(("flavor"), [("silver",), ("gold",), ("platinum",), ("diamond",)])
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
        cls.deployer = cls.vdc.get_deployer(password=cls.password)
        minio_ak = cls.random_name()
        minio_sk = cls.random_string()
        kube_config = cls.deployer.deploy_vdc(minio_ak, minio_sk)
        cls.expiration_value = cls.vdc.calculate_expiration_value()
        return kube_config

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

    def test02_calculate_expiration_value(self):
        """Test case for checking the expiration value.

        **Test Scenario**

        - Deploy VDC.
        - Get the expiration value.
        - Check expiration value after one hour.
        """
        self.assertEqual(int(self.expiration_value), j.data.time.get().timestamp + 60 * 60)

    def test_03_is_empty(self):
        """Test case for checking that deployed vdc not empty.

        **Test Scenario**

        - Deploy VDC.
        - Check that the deployed vdc not empty.
        """
        self.info("Check that the deployed vdc not empty")
        self.assertEqual(self.vdc.is_empty(), False)

    def test_04_load_info(self):
        """Test case for load info.

        **Test Scenario**

        - Deploy VDC.
        - Check instance_name should be empty.
        - Load info.
        - Check instace_name should be filled.
        """
        self.info("Check instance_name should be empty")
        self.assertFalse(self.vdc.instance_name)

        self.info("Load info")
        self.vdc.load_info()

        self.info("Check instace_name should be filled")
        self.assertTrue(self.vdc.instance_name)

    def test_05_find_vdc(self):
        """Test case for find vdc.

        **Test Scenario**

        - Deploy VDC.
        - Try to find this vdc
        """
        self.info("Try to find this vdc")
        self.assertTrue(j.sals.vdc.find(self.vdc.instance_name))

    def test_06_add_delete_k8s_node(self):
        """Test case for adding and deleting node.

        **Test Scenario**

        - Deploy VDC.
        - Add kubernetes node.
        - Check that the node has been added.
        - Delete this node.
        - Check that this node has been deleted.
        """
        self.vdc.load_info()
        k8s_before_add = len(self.vdc.kubernetes)

        self.info("Add kubernetes node")
        wid = self.deployer.add_k8s_nodes("medium")

        self.info("Check that node has been added")
        self.vdc.load_info()
        self.assertEqual(len(self.vdc.kubernetes), k8s_before_add + 1)

        self.info("Delete this node")
        self.deployer.delete_k8s_node(wid)

        self.info("Check that this node has been deleted")
        self.vdc.load_info()
        self.assertEqual(len(self.vdc.kubernetes), k8s_before_add)

    def test_07_apply_grace_period_action(self):
        """Test case for applay and revert grace period action.

        **Test Scenario**

        - Deploy VDC.
        - Apply grace period action.
        - Check that k8s hasn't been reachable.
        - Revert grace period action.
        - Check that k8s has been reachable.
        """

        self.info("Apply grace period action")
        self.vdc.apply_grace_period_action()

        self.info("Check that k8s hasn't been reachable")
        k8s = self.vdc.get_kubernetes_monitor()
        ip_address = k8s.nodes[0].ip_address
        res = j.sals.nettools.tcp_connection_test(ip_address, port=22, timeout=20)
        self.assertFalse(res)

        self.info("Revert grace period action")
        self.vdc.revert_grace_period_action()

        self.info("Check that k8s has been reachable")
        res = j.sals.nettools.tcp_connection_test(ip_address, port=22, timeout=20)
        self.assertFalse(res)

    def test08_renew_plan(self):
        """Test case for renew plan.

        **Test Scenario**

        - Deploy VDC.
        - Get the expiration date
        - Renew plan with one day.
        - Check that the expiration value has been changed.
        """
        expiration_value = self.vdc.expiration_date

        self.info("Renew plan with one day")
        self.deployer.renew_plan(1)

        self.info("Check that the expiration value has been changed")
        self.vdc.load_info()
        self.assertNotEqual(expiration_value, self.vdc.expiration_date)

    def test09_transfer_to_provisioning_wallet(self):
        """Test case for transfer 0.1 tft to provisioning wallet.

        **Test Scenario**

        - Deploy VDC.
        - Get wallet balance.
        - Transfer 0.1 TFT to provisioning wallet.
        - Check that the wallet balance has been changed.
        """

        self.info("Get wallet balance")
        old_wallet_balance = self.vdc.provision_wallet.get_balance().balances[0].balance  # [0.61 TFT:addres, 0.0 XLM]

        self.info("Transfer 0.1 TFT to provisioning wallet")
        vdc_price = j.tools.zos.consumption.calculate_vdc_price(self.flavor)
        needed_tft = float(vdc_price) / 24 / 30 + 0.1
        self.vdc.transfer_to_provisioning_wallet(needed_tft, "test_wallet")

        self.info("Check that the wallet balance has been changed")
        new_wallet_balance = self.vdc.provision_wallet.get_balance().balances[0].balance
        self.assertEqual(float(old_wallet_balance), float(new_wallet_balance) + 0.1)
