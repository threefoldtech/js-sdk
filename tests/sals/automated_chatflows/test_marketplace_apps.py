import string

import pytest
from jumpscale.core.base import StoredFactory
from jumpscale.loader import j
from jumpscale.packages.marketplace.bottle.models import UserEntry
from solutions_automation import deployer

from chatflows_base import ChatflowsBase


@pytest.mark.integration
class MarketplaceChatflows(ChatflowsBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Accept Marketplace T&C for testing identity.
        explorer_url = j.core.identity.me.explorer.url
        if "testnet" in explorer_url:
            explorer_name = "testnet"
        elif "devnet" in explorer_url:
            explorer_name = "devnet"
        elif "explorer.grid.tf" in explorer_url:
            explorer_name = "mainnet"
        cls.user_entry_name = f"{explorer_name}_{cls.tname.replace('.3bot', '')}"
        cls.marketplace_user_factory = StoredFactory(UserEntry)
        marketplace_user_entry = cls.marketplace_user_factory.get(cls.user_entry_name)
        marketplace_user_entry.has_agreed = True
        marketplace_user_entry.tname = cls.tname
        marketplace_user_entry.save()

    @classmethod
    def tearDownClass(cls):
        # Remove userEntry for accepting T&C.
        cls.marketplace_user_factory.delete(cls.user_entry_name)
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.solution_uuid = None

    def tearDown(self):
        if self.solution_uuid:
            j.sals.reservation_chatflow.solutions.cancel_solution_by_uuid(self.solution_uuid)
        super().tearDown()

    def random_name(self):
        # Only lower case for subdomain.
        return j.data.idgenerator.nfromchoices(10, string.ascii_lowercase)

    def test01_wiki(self):
        """Test case for testing wiki.

        **Test Scenario**
        - Deploy wiki.
        - Check that wiki is accessed.
        """
        self.info("Deploy wiki.")
        name = self.random_name()
        title = self.random_name()
        repo = "https://github.com/threefoldfoundation/info_gridmanual"
        branch = "master"
        wiki = deployer.deploy_wiki(solution_name=name, title=title, repo=repo, branch=branch)
        self.solution_uuid = wiki.solution_id

        self.info("Check that wiki is accessed.")
        request = j.tools.http.get(f"https://{wiki.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("TF Grid", request.content.decode())

    def test02_blog(self):
        """Test case for testing blog.

        **Test Scenario**
        - Deploy Blog
        - Check if blog is accessed

        """
        self.info("Deploy blog...")
        name = self.random_name()
        title = self.random_name()
        repo = "https://github.com/threefoldfoundation/blog_threefold"
        branch = "master"
        blog = deployer.deploy_blog(solution_name=name, title=title, repo=repo, branch=branch)
        self.solution_uuid = blog.solution_id

        self.info("Check if blog is accessed..")
        request = j.tools.http.get(f"https://{blog.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test03_website(self):
        """Test case for testing website.

        **Test Scenario**
        - Deploy Website
        - Check if website is accessed

        """
        self.info("Deploy Website")
        name = self.random_name()
        title = self.random_name()
        repo = "https://github.com/xmonader/www_incubaid"
        branch = "master"
        website = deployer.deploy_website(solution_name=name, title=title, repo=repo, branch=branch)
        self.solution_uuid = website.solution_id

        self.info("Check if website is accessed")
        request = j.tools.http.get(f"https://{website.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("We are building companies", request.content.decode())

    def test04_mattermost(self):
        """Test case for testing mattermost.
        **Test Scenario**
        - Deploy Mattermost
        - Check if Mattermost is accessed

        """
        self.info("Deploy Mattermost")
        name = self.random_name()
        mattermost = deployer.deploy_mattermost(solution_name=name)
        self.solution_uuid = mattermost.solution_id

        self.info("Check if Mattermost is accessed")
        request = j.tools.http.get(f"http://{mattermost.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test05_cryptpad(self):
        """Test case for testing cryptpad.

        **Test Scenario**
        - Deploy Cryptpad
        - Check if Cryptpad is accessed
        """
        self.info("Deploy Cryptpad")
        name = self.random_name()
        cryptpad = deployer.deploy_cryptpad(solution_name=name)
        self.solution_uuid = cryptpad.solution_id

        self.info("Check if Crypted is accessed")
        request = j.tools.http.get(f"https://{cryptpad.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test06_gitea(self):
        """Test case for testing gitea.

        **Test Scenario**
        - Deploy Gitea
        - Check if Gitea is accessed
        """
        self.info("Deploy Gitea")
        name = self.random_name()
        gitea = deployer.deploy_gitea(solution_name=name)
        self.solution_uuid = gitea.solution_id

        self.info("Check if Gitea is accessed")
        request = j.tools.http.get(f"https://{gitea.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test07_discourse(self):
        """Test case for testing discourse.

        **Test Scenario**
        - Deploy Discourse
        - Check if Discourse is accessed
        """
        self.info("Deploy Discourse")
        name = self.random_name()
        host_email = j.data.fake.email()
        smtp_host = j.data.fake.email()
        host_email_password = self.random_name()
        discourse = deployer.deploy_discourse(
            solution_name=name, host_email=host_email, smtp_host=smtp_host, host_email_password=host_email_password
        )
        self.solution_uuid = discourse.solution_id

        self.info("Check if Discourse is accessed")
        request = j.tools.http.get(f"https://{discourse.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("Congratulations, you installed TFT Forum!", request.content.decode())

    def test08_peertube(self):
        """Test case for testing peertube.

        **Test Scenario**
        - Deploy Peertube
        - Check if Peertube is accessed
        """
        self.info("Deploy Peertube")
        name = self.random_name()
        peertube = deployer.deploy_peertube(solution_name=name)
        self.solution_uuid = peertube.solution_id

        self.info("Check if Peertube is accessed")
        request = j.tools.http.get(f"https://{peertube.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("PeerTube", request.content.decode())

    def test09_taiga(self):
        """Test case for testing taiga.

        **Test Scenario**
        - Deploy Taiga
        - Check if Taiga is accessed
        """
        self.info("Deploy Taiga")
        name = self.random_name()
        host_email = j.data.fake.email()
        smtp_host = j.data.fake.email()
        host_email_password = self.random_name()
        secret = self.random_name()
        taiga = deployer.deploy_taiga(
            solution_name=name,
            host_email=host_email,
            smtp_host=smtp_host,
            host_email_password=host_email_password,
            secret=secret,
        )
        self.solution_uuid = taiga.solution_id

        self.info("Check if Taiga is accessed")
        request = j.tools.http.get(f"https://{taiga.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
