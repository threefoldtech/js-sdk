import pytest
from jumpscale.loader import j
from solutions_automation import deployer
from tests.sals.automated_chatflows.chatflows_base import ChatflowsBase


@pytest.mark.integration
class MarketplaceChatflows(ChatflowsBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Accept Marketplace T&C for testing identity.
        cls.accept_terms_conditions(type_="marketplace")

    @classmethod
    def tearDownClass(cls):
        # Remove userEntry for accepting T&C.
        cls.user_factory.delete(cls.user_entry_name)
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.solution_uuid = None

    def tearDown(self):
        if self.solution_uuid:
            j.sals.reservation_chatflow.solutions.cancel_solution_by_uuid(self.solution_uuid)
        super().tearDown()

    def test01_wiki(self):
        """Test case for deploying a wiki.

        **Test Scenario**

        - Deploy a wiki.
        - Check that the wiki is reachable.
        """
        self.info("Deploy a wiki.")
        name = self.random_name()
        title = self.random_name()
        repo = "https://github.com/threefoldfoundation/info_gridmanual"
        branch = "master"
        wiki = deployer.deploy_wiki(solution_name=name, title=title, repo=repo, branch=branch)
        self.solution_uuid = wiki.solution_id

        self.info("Check that the wiki is reachable.")
        request = j.tools.http.get(f"https://{wiki.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)
        self.assertIn("TF Grid", request.content.decode())

    def test02_blog(self):
        """Test case for deploying a blog.

        **Test Scenario**

        - Deploy a Blog.
        - Check that the blog is reachable.
        """
        self.info("Deploy blog.")
        name = self.random_name()
        title = self.random_name()
        repo = "https://github.com/threefoldfoundation/blog_threefold"
        branch = "master"
        blog = deployer.deploy_blog(solution_name=name, title=title, repo=repo, branch=branch)
        self.solution_uuid = blog.solution_id

        self.info("Check that the blog is reachable.")
        request = j.tools.http.get(f"https://{blog.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)

    def test03_website(self):
        """Test case for deploying a website.

        **Test Scenario**

        - Deploy a website.
        - Check that the website is reachable.
        """
        self.info("Deploy a website")
        name = self.random_name()
        title = self.random_name()
        repo = "https://github.com/xmonader/www_incubaid"
        branch = "master"
        website = deployer.deploy_website(solution_name=name, title=title, repo=repo, branch=branch)
        self.solution_uuid = website.solution_id

        self.info("Check that the website is reachable.")
        request = j.tools.http.get(f"https://{website.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)
        self.assertIn("We are building companies", request.content.decode())

    def test04_mattermost(self):
        """Test case for deploying Mattermost.

        **Test Scenario**

        - Deploy Mattermost.
        - Check that Mattermost is reachable.
        """
        self.info("Deploy Mattermost.")
        name = self.random_name()
        mattermost = deployer.deploy_mattermost(solution_name=name)
        self.solution_uuid = mattermost.solution_id

        self.info("Check that Mattermost is reachable.")
        request = j.tools.http.get(f"http://{mattermost.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)

    def test05_cryptpad(self):
        """Test case for deploying Cryptpad.

        **Test Scenario**

        - Deploy Cryptpad.
        - Check that Cryptpad is reachable.
        """
        self.info("Deploy Cryptpad")
        name = self.random_name()
        cryptpad = deployer.deploy_cryptpad(solution_name=name)
        self.solution_uuid = cryptpad.solution_id

        self.info("Check that Cryptpad is reachable")
        request = j.tools.http.get(f"https://{cryptpad.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)

    def test06_gitea(self):
        """Test case for deploying Gitea.

        **Test Scenario**

        - Deploy Gitea.
        - Check that Gitea is reachable.
        """
        self.info("Deploy Gitea")
        name = self.random_name()
        gitea = deployer.deploy_gitea(solution_name=name)
        self.solution_uuid = gitea.solution_id

        self.info("Check that Gitea is reachable.")
        request = j.tools.http.get(f"https://{gitea.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)

    @pytest.mark.skip("https://github.com/threefoldtech/js-sdk/issues/1672")
    def test07_discourse(self):
        """Test case for deploy Discourse.

        **Test Scenario**

        - Deploy Discourse.
        - Check that Discourse is reachable.
        """
        self.info("Deploy Discourse.")
        name = self.random_name()
        host_email = j.data.fake.email()
        smtp_host = j.data.fake.email()
        host_email_password = self.random_name()
        discourse = deployer.deploy_discourse(
            solution_name=name, host_email=host_email, smtp_host=smtp_host, host_email_password=host_email_password
        )
        self.solution_uuid = discourse.solution_id

        self.info("Check that Discourse is reachable.")
        request = j.tools.http.get(f"https://{discourse.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)
        self.assertIn("Congratulations, you installed TFT Forum!", request.content.decode())

    def test08_peertube(self):
        """Test case for deploying Peertube.

        **Test Scenario**

        - Deploy Peertube
        - Check that Peertube is reachable.
        """
        self.info("Deploy Peertube.")
        name = self.random_name()
        peertube = deployer.deploy_peertube(solution_name=name)
        self.solution_uuid = peertube.solution_id

        self.info("Check that Peertube is reachable.")
        request = j.tools.http.get(f"https://{peertube.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)
        self.assertIn("PeerTube", request.content.decode())

    def test09_taiga(self):
        """Test case for deploying Taiga.

        **Test Scenario**

        - Deploy Taiga.
        - Check that Taiga is reachable.
        """
        self.info("Deploy Taiga.")
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

        self.info("Check that Taiga is reachable.")
        request = j.tools.http.get(f"https://{taiga.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)
