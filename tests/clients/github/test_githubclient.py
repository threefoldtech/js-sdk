# i created new fake github account
# email: tft.testing.19@gmail.com.
# password: tft_password19
# username: tfttesting
# name: Codescalers Test
# organization: fakeForTest2

from unittest import TestCase
import string
from time import sleep
from os import path

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
        sleep(5)
        self.assertNotIn(repo.full_name, str(self.client.get_repos()))

    def test003_github_delete_repo(self):
        """Test case for delete repo.

        **Test Scenario**
        #. create repo.
        #. Delete this repo.
        #. check that this repo is deleted.
        """
        self.info("create repo")
        repo_name = self.random_string()
        repo = self.client.create_repo(name=repo_name,)

        self.info("Delete this repo")
        self.client.delete_repo(repo_name=repo.name)

        sleep(5)
        self.info("chrck that this repo is deleted")
        self.assertNotIn(repo.full_name, str(self.client.get_repos()))

    def test004_github_set_file(self):
        """Test case for set file.

        **Test Scenario**
        #. create repo with auto init.
        #. create file and set to repo
        #. download dir.
        #. check if file is sent.
        #. delete repo
        """
        self.info("create repo")
        repo_name = self.random_string()
        repo = self.client.create_repo(name=repo_name, auto_init=True)
        repo = self.client.get_repo(repo_full_name=repo.full_name)

        self.info("create file and set to repo")
        with open("test.txt", "+w") as f:
            f.write("test write to file")
            repo.set_file(path="test.txt", content="txt")

        self.info("download dir")
        import pdb

        pdb.set_trace()
        dir_ = repo.download_directory(src="/test", download_dir="/yutyktfwlo")

        self.assertEqual(path.exists("test.txt"), True)
