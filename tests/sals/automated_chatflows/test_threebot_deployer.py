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
        """Test case for deploy threebot

        **Test Scenario**
        - create threebot
        - check access threebot
        """
        self.info("create threebot")
        name = self.random_name()
        secret = self.random_name()
        threebot = deployer.deploy_threebot(solution_name=name, secret=secret, expiration=time() + 60 * 15, ssh="")
        self.solution_uuid = threebot.solution_id

        self.info("check access threebot")
        request = j.tools.http.get(f"http://{threebot.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test02_recover_threebot(self):
        """Test case for recover threebot

        **Test Scenario**
        - create threebot
        - recover threebot
        - check access recoverd threebot
        """
        self.info("create threebot")
        name = self.random_name()
        secret = self.random_name()
        threebot = deployer.deploy_threebot(solution_name=name, secret=secret, expiration=time() + 60 * 15, ssh="")
        j.sals.reservation_chatflow.solutions.cancel_solution_by_uuid(threebot.solution_id)

        self.info("recover threebot")
        threebot = deployer.recover_threebot(
            solution_name=name, recover_password=secret, ssh=self.ssh_cl.public_key_path, expiration=time() + 60 * 15,
        )
        self.solution_uuid = threebot.solution_id

        self.info("check access recoverd threebot")
        request = j.tools.http.get(f"http://{threebot.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test03_extend_threebot(self):
        """Test case for extend threebot

        **Test Scenario**
        - create threebot
        - extend threebot
        - check expiration
        """
        self.info("create threebot")
        name = self.random_name()
        secret = self.random_name()
        now = time()
        expiration = 60 * 15
        threebot = deployer.deploy_threebot(solution_name=name, secret=secret, expiration=now + expiration, ssh="")

        self.info("extend threebot")
        extend_threebot = deployer.extend_threebot(name=name, expiration=now + expiration)
        self.solution_uuid = threebot.solution_id

        # TODO: Need to be fixed for pool reuse.
        self.info("check expiration")
        threebot_expire = extend_threebot.pool.empty_at
        calculate_expire = now + expiration * 2 + 60 * 60  # An hour from the initial deployment
        self.assertAlmostEqual(threebot_expire, int(calculate_expire), delta=300)
