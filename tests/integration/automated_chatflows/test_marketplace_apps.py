import sys
from unittest import TestCase
from uuid import uuid4
import base_test as base

sdk_location = __file__.split("tests")[0]
solution_automation_location = f"{sdk_location}solutions_automation"
sys.path.append(solution_automation_location)
import pytest
from jumpscale.loader import j
from solutions_automation import deployer


@pytest.mark.integration
class AutomatedChatflows(TestCase):
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
        j.sals.reservation_chatflow.solutions.cancel_solution_by_uuid(self.solution_uuid)

    def test01_wiki(self):
        """Test case for testing wiki.

        **Test Scenario**
        #. Deploy wiki.
        #. Check that wiki is accessed.
        """
        base.info("Deploy wiki.")
        name = base.random_string()
        title = base.random_string()
        repo = "https://github.com/threefoldfoundation/info_gridmanual"
        branch = "master"
        wiki = deployer.deploy_wiki(solution_name=name, title=title, repo=repo, branch=branch)
        self.solution_uuid = wiki.solution_id

        base.info("Check that wiki is accessed.")
        request = j.tools.http.get(f"https://{wiki.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("TF Grid 2.1 Manual", request.content.decode())

    def test02_blog(self):
        """Test case for testing blog.

        **Test Scenario**
        #. Deploy Blog
        #. Check if blog is accessed

        """
        base.info("Deploy blog...")
        name = base.random_string()
        title = base.random_string()
        repo = "https://github.com/threefoldfoundation/blog_threefold"
        branch = "master"
        blog = deployer.deploy_blog(solution_name=name, title=title, repo=repo, branch=branch)
        self.solution_uuid = blog.solution_id

        base.info("Check if blog is accessed..")
        request = j.tools.http.get(f"https://{blog.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("TF Grid 2.1 Manual", request.content.decode())

    def test03_website(self):
        """Test case for testing website.

        **Test Scenario**
        #. Deploy Website
        #. Check if website is accessed

        """
        base.info("Deploy Website")
        name = base.random_string()
        title = base.random_string()
        repo = "https://github.com/xmonader/www_incubaid"
        branch = "master"
        website = deployer.deploy_website(solution_name=name, title=title, repo=repo, branch=branch)
        self.solution_uuid = website.solution_id

        base.info("Check if website is accessed")
        request = j.tools.http.get(f"https://{website.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("We are building companies", request.content.decode())

    def test04_mattermost(self):
        """Test case for testing mattermost.
        **Test Scenario**
        #. Deploy Mattermost
        #. Check if Mattermost is accessed

        """
        base.info("Deploy Mattermost")
        name = base.random_string()
        mattermost = deployer.deploy_mattermost(solution_name=name)
        self.solution_uuid = mattermost.solution_id

        base.info("Check if Mattermost is accessed")
        request = j.tools.http.get(f"http://{mattermost.domain}", verify=False)

        self.assertEqual(request.status_code, 200)
        self.assertIn("By proceeding to create your account and use Mattermost", request.content.decode())

    def test05_cryptpad(self):
        """Test case for testing cryptpad.

        **Test Scenario**
        #. Deploy Cryptpad
        #. Check if Cryptpad is accessed
        """
        base.info("Deploy Cryptpad")
        name = base.random_string()
        cryptpad = deployer.deploy_cryptpad(solution_name=name)
        self.solution_uuid = cryptpad.solution_id

        base.info("Check if Crypted is accessed")
        request = j.tools.http.get(f"https://{cryptpad.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test06_gitea(self):
        """Test case for testing cryptpad.

        **Test Scenario**
        #. Deploy Gitea
        #. Check if Gitea is accessed
        """
        base.info("Deploy Gitea")
        name = base.random_string()
        gitea = deployer.deploy_gitea(solution_name=name)
        self.solution_uuid = gitea.solution_id

        base.info("Check if Gitea is accessed")
        request = j.tools.http.get(f"https://{gitea.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test07_discourse(self):
        """Test case for testing discourse.

        **Test Scenario**
        #. Deploy Discourse
        #. Check if Discourse is accessed
        """
        base.info("Deploy Discourse")
        name = base.random_string()
        host_email = j.data.fake.email()
        smtp_host = j.data.fake.email()
        host_email_password = base.random_string()
        discourse = deployer.deploy_discourse(
            solution_name=name, host_email=host_email, smtp_host=smtp_host, host_email_password=host_email_password
        )
        self.solution_uuid = discourse.solution_id

        base.info("Check if Discourse is accessed")
        request = j.tools.http.get(f"https://{discourse.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("Congratulations, you installed TFT Forum!", request.content.decode())

    def test08_peertube(self):
        """Test case for testing peertube.

        **Test Scenario**
        #. Deploy Peertube
        #. Check if Peertube is accessed
        """
        base.info("Deploy Peertube")
        name = base.random_string()
        peertube = deployer.deploy_peertube(solution_name=name)
        self.solution_uuid = peertube.solution_id

        base.info("Check if Peertube is accessed")
        request = j.tools.http.get(f"https://{peertube.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("PeerTube", request.content.decode())

    def test09_taiga(self):
        """Test case for testing taiga.

        **Test Scenario**
        #. Deploy Taiga
        #. Check if Taiga is accessed
        """
        base.info("Deploy Taiga")
        name = base.random_string()
        host_email = j.data.fake.email()
        smtp_host = j.data.fake.email()
        host_email_password = base.random_string()
        secret = base.random_string()
        taiga = deployer.deploy_taiga(
            solution_name=name,
            host_email=host_email,
            smtp_host=smtp_host,
            host_email_password=host_email_password,
            secret=secret,
        )
        self.solution_uuid = taiga.solution_id

        base.info("Check if Taiga is accessed")
        request = j.tools.http.get(f"https://{taiga.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
