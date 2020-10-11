# i created new fake github account
# email: tft.testing.19@gmail.com.
# password: tft_password19
# username: tfttesting
# name: Codescalers Test
# organization: fakeForTest2

from unittest import TestCase
import string
from gevent import sleep
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
        self.repo_name = ""

    def tearDown(self):
        j.clients.github.delete(self.instance_name)
        if self.repo_name:
            self.client.delete_repo(repo_name=self.repo_name)

    def random_string(self):
        return j.data.idgenerator.nfromchoices(10, string.ascii_lowercase)

    def info(self, msg):
        j.logger.info(msg)

    def wait(self, sec):
        while sec:
            sleep(1)
            sec -= 1

    def test01_github_client_get_access(self):
        self.assertEqual(self.client.get_userdata()["emails"][0]["email"], self.email)

    def test02_github_create_repo(self):
        """Test case for create repo.

        **Test Scenario**
        #. create repo.
        #. Check if repo is created.
        """
        self.info("create repo")
        self.repo_name = self.random_string()
        repo = self.client.create_repo(name=self.repo_name)

        self.info("Check if repo is created")
        self.assertIn(repo.full_name, str(self.client.get_repos()))

    def test03_github_delete_repo(self):
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

        self.wait(3)  # wait 3 second to get repos
        self.info("chrck that this repo is deleted")
        self.assertNotIn(repo.full_name, str(self.client.get_repos()))

    def test04_github_set_file(self):
        """Test case for set file.

        **Test Scenario**
        #. create repo with auto init.
        #. create file and set to repo
        #. download dir.
        #. check if file is sent.
        """

        self.info("create repo")
        self.repo_name = self.random_string()
        dir_name = self.random_string()
        f_name = self.random_string()
        repo = self.client.create_repo(name=self.repo_name, auto_init=True)
        repo = self.client.get_repo(repo_full_name=repo.full_name)

        self.info("set file to repo")
        repo.set_file(path=f"{dir_name}/{f_name}.txt", content="test set file to repo")

        self.info("download dir")
        repo.download_directory(src="", download_dir="")
        self.assertEqual(j.sals.fs.is_file(f"./tfttesting/{repo.name}/{dir_name}/{f_name}.txt"), True)
        j.sals.fs.rmtree("./tfttesting")

    def test05_github_create_milestoes(self):
        """Test case for create milestones.

        **Test Scenario**
        #. create repo with auto init.
        #. create milestones
        #. check if milestones is created
        #. delete milestones
        #. check if milestones id deleted
        """
        self.info("create repo with auto init.")
        self.repo_name = self.random_string()
        title = self.random_string()
        repo = self.client.create_repo(name=self.repo_name, auto_init=True)

        self.info("create milestones")
        ceated_milestone = repo.create_milestone(title=title)

        self.info("check if milestones is created")
        milestone = repo.get_milestone(number=ceated_milestone.number)
        self.assertEqual(milestone.title, ceated_milestone.title)

    def test06_github_create_issue(self):
        """Test case for create issue.

        **Test Scenario**
        #. create repo with auto init.
        #. create issue
        #. check if issue is created
        """

        self.info("create repo with auto init")
        self.repo_name = self.random_string()
        issue_title = self.random_string()
        repo = self.client.create_repo(name=self.repo_name, auto_init=True)
        self.info("create issue")
        issue_created = repo.create_issue(title=issue_title)

        self.info("check if issue is created")
        self.assertEqual(issue_created.title, repo.get_issue(issue_created.number).title)

    def test06_github_issue_with_milestone(self):
        """Test case for create issue with milestone.

        **Test Scenario**
        #. create repo with auto init.
        #. create milestone
        #. create issue with milestone
        #. check if issue has milestone
        """

        self.info("create repo with auto init")
        self.repo_name = self.random_string()
        issue_title = self.random_string()
        milestone_title = self.random_string()
        repo = self.client.create_repo(name=self.repo_name, auto_init=True)

        self.info("create milestone")
        milestone = repo.create_milestone(title=milestone_title)

        self.info("create issue with milestone")
        issue_created = repo.create_issue(title=issue_title, milestone=milestone)

        self.info("check if issue has milestone")
        self.assertEqual(milestone.title, issue_created.milestone.title)
