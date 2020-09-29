# i created new fake github account
# email: tft.testing.19@gmail.com.
# password: tft_password19
# username: tfttesting
# name: Codescalers Test
# organization: fakeForTest2

from unittest import TestCase
import string

from jumpscale.loader import j


class GithubClientTest(TestCase):
    def setUp(self):
        super().setUp()

        self.instance_name = j.data.random_names.random_name()

        self.username = "tfttesting"
        self.password = "tft_password19"
        self.email = "tft.testing.19@gmail.com"

        self.client = j.clients.github.get(self.instance_name)

        self.client.username = self.username
        self.client.password = self.password

    def tearDown(self):
        j.clients.github.delete(self.instance_name)

    def random_string(self):
        return j.data.idgenerator.nfromchoices(10, string.ascii_lowercase)

    def info(self, msg):
        j.logger.info(msg)

    def test001_github_client_get_access(self):
        self.assertEqual(self.client.get_userdata()["emails"][0]["email"], self.email)

    def test002_github_create_repo(self):
        """Test case for create repo.

        **Test Scenario**
        #. create repo.
        #. Check if repo is created.
        #. Delete this repo.
        #. check that this repo is deleted.
        """
        self.info("create repo")
        repo_name = self.random_string()
        repo = self.client.create_repo(name=repo_name)

        self.info("Check if repo is created")
        self.assertIn(repo.full_name, str(self.client.get_repos()))

        self.info("Delete this repo")
        self.client.delete_repo(repo_name=repo.name)

        self.info("check that this repo is deleted.")
        self.assertNotIn(repo.full_name, str(self.client.get_repos()))
