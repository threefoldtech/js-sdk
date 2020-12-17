import pytest
from jumpscale.loader import j
from solutions_automation import deployer
from tests.sals.automated_chatflows.chatflows_base import ChatflowsBase
from gevent import sleep


@pytest.mark.integration
class PoolChatflows(ChatflowsBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Accept admin T&C for testing identity.
        cls.accept_terms_conditions(type_="marketplace")
        cls.solution_uuid = ""

    @classmethod
    def tearDownClass(cls):
        # Remove userEntry for accepting T&C
        cls.user_factory.delete(cls.user_entry_name)
        super().tearDownClass()

    def tearDown(self):
        if self.solution_uuid:
            j.sals.reservation_chatflow.solutions.cancel_solution_by_uuid(self.solution_uuid)
        super().tearDown()

    def test01_create_pool(self):
        """Test case for creating a pool.

        **Test Scenario**

        - Create a pool with some CU and SU units.
        - Check that the pool has been created with the same units.
        """
        self.info("Create a pool with some CU and SU units.")
        name = self.random_name()
        cu = j.data.idgenerator.random_int(0, 2)
        su = j.data.idgenerator.random_int(1, 2)
        time_unit = "Day"
        time_to_live = j.data.idgenerator.random_int(1, 2)
        pool = deployer.create_pool(
            solution_name=name, cu=cu, su=su, time_unit=time_unit, time_to_live=time_to_live, wallet_name="demos_wallet"
        )

        self.info("Check that the pool has been created with the same units.")
        reservation_id = pool.pool_data.reservation_id
        pool_data = j.sals.zos.get().pools.get(reservation_id)
        calculated_su = su * time_to_live * 60 * 60 * 24
        calculated_cu = cu * time_to_live * 60 * 60 * 24
        self.assertEqual(pool_data.cus, float(calculated_cu))
        self.assertEqual(pool_data.sus, float(calculated_su))

    def test02_extend_pool(self):
        """Test case for extending a pool.

        **Test Scenario**

        - Create a pool with some CU and SU units.
        - Extend the pool has been created.
        - Check that the pool has been extended with the same units.
        """
        self.info("Create a pool with some CU and SU units.")
        name = self.random_name()
        pool = deployer.create_pool(solution_name=name, wallet_name="demos_wallet")
        reservation_id = pool.pool_data.reservation_id

        self.info("Extend the pool has been created.")
        cu = j.data.idgenerator.random_int(0, 2)
        su = j.data.idgenerator.random_int(1, 2)
        time_unit = "Day"
        time_to_live = j.data.idgenerator.random_int(1, 2)
        deployer.extend_pool(
            pool_name=name, wallet_name="demos_wallet", cu=cu, su=su, time_unit=time_unit, time_to_live=time_to_live,
        )

        self.info("Check that the pool has been extended with the same units.")
        pool_data = j.sals.zos.get().pools.get(reservation_id)

        calculated_cu = (1 * 1 * 60 * 60 * 24) + (cu * time_to_live * 60 * 60 * 24)
        calculated_su = (1 * 1 * 60 * 60 * 24) + (su * time_to_live * 60 * 60 * 24)

        self.assertEqual(pool_data.cus, float(calculated_cu))
        self.assertEqual(pool_data.sus, float(calculated_su))
