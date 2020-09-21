import string
import sys
from unittest import TestCase
from uuid import uuid4

sdk_location = __file__.split("tests")[0]
solution_automation_location = f"{sdk_location}solutions_automation"
sys.path.append(solution_automation_location)

import pytest
from jumpscale.loader import j
from solutions_automation import deployer


@pytest.mark.integration
class AutomatedChatflows(TestCase):
    def random_string(self):
        return j.data.idgenerator.nfromchoices(10, string.ascii_lowercase)

    def info(self, msg):
        j.logger.info(msg)

    @classmethod
    def setUpClass(cls):
        # Create the demos_wallet here or in the CI before starting the tests.
        # should start threebot server and load the needed packages here.
        # set TEST_CERT to True.
        pass

    @classmethod
    def tearDownClass(cls):
        # should stop threebot server.
        pass

    def tearDown(self):
        j.sals.reservation_chatflow.solutions.cancel_solution(self.workloads)

    def test01_wiki(self):
        """Test case for testing wiki.

        **Test Scenario**
        #. Deploy wiki.
        #. Check that wiki is accessed.
        """
        self.info("Deploy wiki.")
        name = self.random_string()
        title = self.random_string()
        repo = "https://github.com/threefoldfoundation/info_gridmanual"
        branch = "master"
        wiki = deployer.deploy_wiki(solution_name=name, title=title, repo=repo, branch=branch)
        self.workloads = wiki.workload_ids

        self.info("Check that wiki is accessed.")
        request = j.tools.http.get(f"https://{wiki.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("TF Grid 2.1 Manual", request.content.decode())
