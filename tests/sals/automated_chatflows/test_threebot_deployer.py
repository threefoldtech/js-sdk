import os
from time import time

import pytest
from jumpscale.loader import j
from solutions_automation import deployer

from tests.sals.automated_chatflows.chatflows_base import ChatflowsBase


@pytest.mark.integration
class ThreebotChatflows(ChatflowsBase):
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

    def test01_deploy_threebot(self):
        """Test case for deploying a threebot.

        **Test Scenario**
        - Deploy a threebot.
        - Check that threebot is reachable.
        """
        self.info("Deploy a threebot")
        name = self.random_name()
        secret = self.random_name()
        threebot = deployer.deploy_threebot(solution_name=name, secret=secret, expiration=time() + 60 * 15, ssh="")
        self.solution_uuid = threebot.solution_id

        self.info("Check that threebot is reachable.")
        request = j.tools.http.get(f"http://{threebot.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test02_recover_threebot(self):
        """Test case for recovering a threebot.

        **Test Scenario**
        - Deploy a threebot.
        - Delete the threebot has been deployed.
        - Recover the threebot has been deleted.
        - Check that the threebot has been recovered is reachable.
        """
        self.info("Deploy a threebot.")
        name = self.random_name()
        secret = self.random_name()
        threebot = deployer.deploy_threebot(solution_name=name, secret=secret, expiration=time() + 60 * 15, ssh="")

        self.info("Delete the threebot has been deployed.")
        j.sals.reservation_chatflow.solutions.cancel_solution_by_uuid(threebot.solution_id)

        self.info("Recover the threebot has been deleted.")
        threebot = deployer.recover_threebot(
            solution_name=name, recover_password=secret, ssh=self.ssh_cl.public_key_path, expiration=time() + 60 * 15,
        )
        self.solution_uuid = threebot.solution_id

        self.info("Check that the threebot has been recovered is reachable.")
        request = j.tools.http.get(f"http://{threebot.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test03_extend_threebot(self):
        """Test case for extending a threebot.

        **Test Scenario**
        - Deploy a threebot.
        - Extend the threebot has been deployed.
        - Check that the expiration is increased with the extending time.
        """
        self.info("Deploy a threebot.")
        name = self.random_name()
        secret = self.random_name()
        now = time()
        expiration = 60 * 15
        threebot = deployer.deploy_threebot(solution_name=name, secret=secret, expiration=now + expiration, ssh="")

        self.info("Extend the threebot has been deployed.")
        threebot_expire = threebot.pool.empty_at
        extend_threebot = deployer.extend_threebot(name=name, expiration=threebot_expire + expiration)
        self.solution_uuid = threebot.solution_id

        self.info("Check that the expiration is increased with the extending time.")
        new_expire = extend_threebot.pool.empty_at
        calculated_expire = threebot_expire + expiration
        self.assertAlmostEqual(new_expire, calculated_expire, delta=100)
