from time import time

import pytest
from jumpscale.loader import j
from solutions_automation import deployer
from tests.sals.automated_chatflows.chatflows_base import ChatflowsBase
from jumpscale.packages.threebot_deployer.bottle.utils import stop_threebot_solution
from jumpscale.packages.threebot_deployer.models import USER_THREEBOT_FACTORY


@pytest.mark.integration
class ThreebotChatflows(ChatflowsBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Accept admin T&C for testing identity.
        cls.accept_terms_conditions(type_="marketplace")
        cls.solution_uuid = ""
        cls.secret = ""

    @classmethod
    def tearDownClass(cls):
        # Remove userEntry for accepting T&C
        cls.user_factory.delete(cls.user_entry_name)
        super().tearDownClass()

    def tearDown(self):
        if self.solution_uuid and self.secret:
            stop_threebot_solution(self.tname, self.solution_uuid, self.secret)

    @pytest.mark.skip("https://github.com/threefoldtech/js-sdk/issues/1672")
    def test01_deploy_threebot(self):
        """Test case for deploying a threebot.

        **Test Scenario**

        - Deploy a threebot.
        - Check that threebot is reachable.
        """
        self.info("Deploy a threebot")
        name = self.random_name()
        self.secret = self.random_name()
        threebot = deployer.deploy_threebot(solution_name=name, secret=self.secret, expiration=time() + 60 * 15, ssh="")
        self.solution_uuid = threebot.solution_id

        self.info("Check that threebot is reachable.")
        request = j.tools.http.get(f"http://{threebot.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)

    @pytest.mark.skip("https://github.com/threefoldtech/js-sdk/issues/1672")
    def test02_start_deployed_threebot(self):
        """Test case for starting a threebot.

        **Test Scenario**

        - Deploy a threebot.
        - Stop the deployed threebot
        - Start the stopped threebot.
        - Check that threebot is reachable.
        """
        self.info("Deploy a threebot")
        name = self.random_name()
        self.secret = self.random_name()
        threebot = deployer.deploy_threebot(solution_name=name, secret=self.secret, expiration=time() + 60 * 15, ssh="")
        self.solution_uuid = threebot.solution_id

        self.info("Stop the deployed threebot")
        stop_threebot_solution(self.tname, self.solution_uuid, self.secret)

        self.info("Start the stopped threebot")
        threebot = deployer.start_threebot(name, self.secret)
        self.solution_uuid = threebot.solution_id

        self.info("Check that threebot is reachable.")
        request = j.tools.http.get(f"http://{threebot.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)

    @pytest.mark.skip("https://github.com/threefoldtech/js-sdk/issues/1672")
    def test03_change_deployed_threebot_size(self):
        """Test case for changing a threebot size.

        **Test Scenario**

        - Deploy a threebot.
        - Stop the deployed threebot.
        - Change the stopped threebot size.
        - Check that threebot is reachable.
        """
        self.info("Deploy a threebot")
        name = self.random_name()
        self.secret = self.random_name()
        threebot = deployer.deploy_threebot(solution_name=name, secret=self.secret, expiration=time() + 60 * 15, ssh="")
        self.solution_uuid = threebot.solution_id

        self.info("Stop the deployed threebot")
        stop_threebot_solution(self.tname, self.solution_uuid, self.secret)

        self.info("Start the stopped threebot")
        threebot = deployer.change_threebot_size(
            name, self.secret, flavor="Gold (CPU 2 - Memory 4 GB - Disk 4 GB [SSD])"
        )
        self.solution_uuid = threebot.solution_id
        threebot_config = USER_THREEBOT_FACTORY.get(f"threebot_{self.solution_uuid}")
        threebot_container_workload = j.sals.zos.get().workloads.get(threebot_config.threebot_container_wid)
        self.assertEqual(threebot_container_workload.capacity.cpu, 2)
        self.assertEqual(threebot_container_workload.capacity.memory, 4096)
        self.assertEqual(threebot_container_workload.capacity.disk_size, 4096)

        self.info("Check that threebot is reachable.")
        request = j.tools.http.get(f"http://{threebot.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)

    @pytest.mark.skip("https://github.com/threefoldtech/js-sdk/issues/1672")
    def test04_change_deployed_threebot_location(self):
        """Test case for changing a threebot location.

        **Test Scenario**

        - Deploy a threebot.
        - Stop the deployed threebot.
        - Change the stopped threebot location.
        - Check that threebot is reachable.
        """
        self.info("Deploy a threebot")
        name = self.random_name()
        self.secret = self.random_name()
        threebot = deployer.deploy_threebot(solution_name=name, secret=self.secret, expiration=time() + 60 * 15, ssh="")
        self.solution_uuid = threebot.solution_id

        self.info("Stop the deployed threebot")
        stop_threebot_solution(self.tname, self.solution_uuid, self.secret)

        self.info("Start the stopped threebot")
        threebot = deployer.change_threebot_location(name, self.secret)
        self.solution_uuid = threebot.solution_id

        self.info("Check that threebot is reachable.")
        request = j.tools.http.get(f"http://{threebot.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)
