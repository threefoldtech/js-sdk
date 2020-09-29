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

    def test02_blog(self):
        """

        **Test Scenario**
        #. Deploy Blog
        #. Check if blog is accessed

        """
        self.info("Deploy blog...")
        name = self.random_string()
        title = self.random_string()
        repo = "https://github.com/threefoldfoundation/info_gridmanual"
        branch = "master"
        blog = deployer.deploy_blog(solution_name=name, title=title, repo=repo, branch=branch)
        self.workloads = blog.workload_ids

        self.info("Check if blog is accessed..")
        request = j.tools.http.get(f"https://{blog.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("TF Grid 2.1 Manual", request.content.decode())

    def test03_website(self):
        """
        **Test Scenario**
        #. Deploy Website
        #. Check if website is accessed

        """
        self.info("Deploy Website")
        name = self.random_string()
        title = self.random_string()
        repo = "https://github.com/threefoldfoundation/info_gridmanual"
        branch = "master"
        website = deployer.deploy_website(solution_name=name, title=title, repo=repo, branch=branch)
        self.workloads = website.workload_ids

        self.info("Check if website is accessed")
        request = j.tools.http.get(f"https://{website.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("TF Grid 2.1 Manual", request.content.decode())

    def test04_mattermost(self):
        """
        **Test Scenario**
        #. Deploy Mattermost
        #. Check if Mattermost is accessed

        """
        self.info("Deploy Mattermost")
        name = self.random_string()
        mattermost = deployer.deploy_mattermost(solution_name=name)
        # self.workloads = mattermost.workload_ids

        self.info("Check if Mattermost is accessed")
        request = j.tools.http.get(f"https://{mattermost.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("TF Grid 2.1 Manual", request.content.decode())

    def test05_cryptpad(self):
        """
        **Test Scenario**
        #. Deploy Cryptpad
        #. Check if Cryptpad is accessed
        """
        self.info("Deploy Cryptpad")
        name = self.random_string()
        cryptpad = deployer.deploy_cryptpad(solution_name=name)
        self.workloads = cryptpad.workload_ids

        self.info("Check if Crypted is accessed")
        request = j.tools.http.get(f"https://{cryptpad.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test06_gitea(self):
        """
        **Test Scenario**
        #. Deploy Gitea
        #. Check if Gitea is accessed
        """
        self.info("Deploy Gitea")
        name = self.random_string()
        gitea = deployer.deploy_gitea(solution_name=name)
        # self.workloads = gitea.workload_ids

        self.info("Check if Gitea is accessed")
        request = j.tools.http.get(f"https://{gitea.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test07_discourse(self):
        """
        **Test Scenario**
        #. Deploy Discourse
        #. Check if Discourse is accessed
        """
        self.info("Deploy Discourse")
        name = self.random_string()
        host_email = "test@gmail.com"
        smtp_host = "hassanm@incubaid.com"
        host_email_password = self.random_string()
        discourse = deployer.deploy_discourse(
            solution_name=name, host_email=host_email, smtp_host=smtp_host, host_email_password=host_email_password
        )
        self.workloads = discourse.workload_ids

        self.info("Check if Discourse is accessed")
        request = j.tools.http.get(f"https://{discourse.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("Congratulations, you installed TFT Forum!", request.content.decode())

    def test08_peertube(self):
        """
        **Test Scenario**
        #. Deploy Peertube
        #. Check if Peertube is accessed
        """
        self.info("Deploy Peertube")
        name = self.random_string()
        peertube = deployer.deploy_peertube(solution_name=name)
        # self.workloads = peertube.workload_ids

        self.info("Check if Peertube is accessed")
        request = j.tools.http.get(f"https://{peertube.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("PeerTube", request.content.decode())

    def test09_taiga(self):
        """
        **Test Scenario**
        #. Deploy Taiga
        #. Check if Taiga is accessed
        """
        self.info("Deploy Taiga")
        name = self.random_string()
        host_email = "test@gmail.com"
        smtp_host = "hassanm@incubaid.com"
        host_email_password = self.random_string()
        secret = self.random_string()
        taiga = deployer.deploy_taiga(
            solution_name=name,
            host_email=host_email,
            smtp_host=smtp_host,
            host_email_password=host_email_password,
            secret=secret,
        )
        self.workloads = taiga.workload_ids

        self.info("Check if Taiga is accessed")
        request = j.tools.http.get(f"https://{taiga.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
