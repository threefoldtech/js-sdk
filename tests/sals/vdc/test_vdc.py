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
    def tearDownClass(cls):
        j.sals.vdc.delete(cls.vdc.instance_name)
        super().tearDownClass()

    def test01_load_info(self):
        """Test case for loading info.

        **Test Scenario**

        - Deploy VDC.
        - Get VDC by j.sals.vdc
        - Check that VDC should be empty.
        - Load info.
        - Check that kubernetes node should be filled.
        """

        self.info("Get VDC by j.sals.vdc")
        vdc = j.sals.vdc.find(vdc_name=self.vdc_name, owner_tname=self.tname)

        self.info("Check that VDC should be empty")
        self.assertFalse(vdc.kubernetes)

        self.info("Load info")
        vdc.load_info()

        self.info("Check that kubernetes node should be filled")
        self.assertTrue(vdc.kubernetes)

    def test02_list_vdcs(self):
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

    def test03_calculate_expiration_value(self):
        """Test case for checking the expiration value.

        **Test Scenario**

        - Deploy VDC.
        - Get the expiration value.
        - Check expiration value after one hour.
        """
        timestamp_after_one_hour = self.timestamp_now + 60 * 60
        self.assertLess(int(self.vdc.calculate_expiration_value()) - timestamp_after_one_hour, 200)

    def test04_is_empty(self):
        """Test case for checking that deployed vdc is not empty.

        **Test Scenario**

        - Deploy VDC.
        - Check that the deployed vdc not empty.
        """
        self.info("Check that the deployed vdc not empty")
        self.assertEqual(self.vdc.is_empty(), False)

    def test05_find_vdc(self):
        """Test case for find vdc.

        **Test Scenario**

        - Deploy VDC.
        - Try to find this vdc
        """
        self.info("Try to find this vdc")
        self.assertTrue(j.sals.vdc.find(self.vdc.instance_name))

    def test06_add_delete_k8s_node(self):
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
        self.deployer.delete_k8s_node(wid[0])

        self.info("Check that this node has been deleted")
        self.vdc.load_info()
        self.assertEqual(len(self.vdc.kubernetes), k8s_before_add)

    def test07_apply_grace_period_action(self):
        """Test case for applying and reverting grace period action.

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
        res = j.sals.nettools.tcp_connection_test(ip_address, port=6443, timeout=20)
        self.assertFalse(res)

        self.info("Revert grace period action")
        self.vdc.revert_grace_period_action()

        self.info("Check that k8s has been reachable")
        res = j.sals.nettools.tcp_connection_test(ip_address, port=6443, timeout=20)
        self.assertFalse(res)

    def test08_renew_plan(self):
        """Test case for renewing the plan.

        **Test Scenario**

        - Deploy VDC.
        - Get the expiration date
        - Renew plan with one day.
        - Check that the expiration value has been changed.
        """
        self.info("Get the expiration date")
        pools_expiration_value = self.vdc.get_pools_expiration()

        self.info("Renew plan with one day")
        vdc_price = j.tools.zos.consumption.calculate_vdc_price(self.flavor)
        needed_tft = float(vdc_price) / 30
        self.vdc.transfer_to_provisioning_wallet(needed_tft, "test_wallet")
        self.deployer.renew_plan(1)

        self.info("Check that the expiration value has been changed")
        self.vdc.load_info()
        self.assertEqual(pools_expiration_value + 60 * 60 * 24, self.vdc.get_pools_expiration())

    def test09_transfer_to_provisioning_wallet(self):
        """Test case for transfer TFT to provisioning wallet.

        **Test Scenario**

        - Deploy VDC.
        - Get wallet balance.
        - Transfer TFT to provisioning wallet.
        - Check that the wallet balance has been changed.
        """

        self.info("Get wallet balance")
        old_wallet_balance = self.vdc.provision_wallet.get_balance().balances[0].balance
        self.info("Transfer TFT to provisioning wallet")
        tft = j.data.idgenerator.random_int(1, 2)
        self.vdc.transfer_to_provisioning_wallet(tft, "test_wallet")

        self.info("Check that the wallet balance has been changed")
        new_wallet_balance = self.vdc.provision_wallet.get_balance().balances[0].balance
        self.assertEqual(float(old_wallet_balance) + tft, float(new_wallet_balance))

    # zbd auto extend should be tested manually
    def test10_extend_zdb(self):
        """Test case for extending zdbs.

        **Test Scenario**

        - Deploy VDC.
        - Get the zdbs total size.
        - Extend zdbs.
        - Check that zdbs has been extended.
        """
        self.info("Get the zdbs total size")
        zdb_monitor = self.vdc.get_zdb_monitor()
        old_zdb_total_size = zdb_monitor.zdb_total_size

        self.info("Extend zdbs")
        vdc_identity = f"vdc_ident_{self.vdc.solution_uuid}"
        if j.core.identity.find(vdc_identity):
            j.core.identity.set_default(vdc_identity)
        zdb_monitor.extend(10, ["freefarm"])

        self.info("Check that zdbs has been extended")
        self.vdc.load_info()
        zdb_monitor = self.vdc.get_zdb_monitor()
        self.assertEqual(zdb_monitor.zdb_total_size, old_zdb_total_size + 10)
