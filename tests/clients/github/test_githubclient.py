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
from tests.base_tests import BaseTests as base


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
        if j.sals.fs.exists(path="/tmp/tfttesting/"):
            j.sals.fs.rmtree("/tmp/tfttesting/")

    def wait(self, sec, repo):
        while sec:
            if repo.full_name in str(self.client.get_repos()):
                sleep(1)
                sec -= 1
            else:
                return True
        return False

    def test01_github_client_get_access(self):
        """Test case for get access to client.

        **Test Scenario**
        - Check client email
        """
        self.assertEqual(self.client.get_userdata()["emails"][0]["email"], self.email)

    def test02_github_create_repo(self):
        """Test case for create repo.

        **Test Scenario**
        - Create repo.
        - Check if repo is created.
        """
        base.info(self, "Create repo")

        self.repo_name = base.generate_random_text()
        repo = self.client.create_repo(name=self.repo_name)

        base.info(self, "Check if repo is created")
        self.assertIn(self.repo_name, repo.full_name)

    def test03_github_delete_repo(self):
        """Test case for delete repo.

        **Test Scenario**
        - Create repo.
        - Delete this repo.
        - Check that this repo is deleted.
        """
        base.info(self, "create repo")
        repo_name = base.generate_random_text()
        repo = self.client.create_repo(name=repo_name,)

        base.info(self, "Delete this repo")
        self.client.delete_repo(repo_name=repo.name)

        self.assertTrue(self.wait(3, repo), "repo is not deleted after 3 second")
        base.info(self, "Check that this repo is deleted")
        self.assertNotIn(repo.full_name, str(self.client.get_repos()))

    def test04_github_set_file(self):
        """Test case for set file.

        **Test Scenario**
        - Create repo with auto init.
        - Create file and set to repo
        - Download dir.
        - Check if file is sent.
        - Check content
        """

        base.info(self, "Create repo")
        self.repo_name = base.generate_random_text()
        dir_name = base.generate_random_text()
        f_name = base.generate_random_text()
        content = base.generate_random_text() * 3
        self.client.create_repo(name=self.repo_name, auto_init=True)
        repo = self.client.get_repo(repo_full_name=f"tfttesting/{self.repo_name}")

        base.info(self, "Set file to repo")
        repo.set_file(path=f"{dir_name}/{f_name}.txt", content=content)

        base.info(self, "Download dir")
        repo.download_directory(src="", download_dir="/tmp")

        base.info(self, "Check if file is sent")
        self.assertEqual(j.sals.fs.is_file(f"/tmp/tfttesting/{repo.name}/{dir_name}/{f_name}.txt"), True)

        base.info(self, "Check content")
        self.assertEqual(content, j.sals.fs.read_file(f"/tmp/tfttesting/{repo.name}/{dir_name}/{f_name}.txt"))

    def test05_github_create_milestoes(self):
        """Test case for create milestones.

        **Test Scenario**
        - Create repo with auto init.
        - Create milestones
        - Check if milestones is created
        """
        base.info(self, "Create repo with auto init.")
        self.repo_name = base.generate_random_text()
        title = base.generate_random_text()
        repo = self.client.create_repo(name=self.repo_name, auto_init=True)

        base.info(self, "Create milestones")
        ceated_milestone = repo.create_milestone(title=title)

        base.info(self, "Check if milestones is created")
        milestone = repo.get_milestone(number=ceated_milestone.number)
        self.assertEqual(title, milestone.title)

    def test06_github_create_issue(self):
        """Test case for create issue.

        **Test Scenario**
        - Create repo with auto init.
        - Create issue
        - Check if issue is created
        """

        base.info(self, "Create repo with auto init")
        self.repo_name = base.generate_random_text()
        issue_title = base.generate_random_text()
        repo = self.client.create_repo(name=self.repo_name, auto_init=True)
        base.info(self, "Create issue")
        issue_created = repo.create_issue(title=issue_title)

        base.info(self, "Check if issue is created")
        self.assertEqual(issue_created.title, issue_title)

    def test06_github_issue_with_milestone(self):
        """Test case for create issue with milestone.

        **Test Scenario**
        - Create repo with auto init.
        - Create milestone
        - Create issue with milestone
        - Check if issue has milestone
        """

        base.info(self, "Create repo with auto init")
        self.repo_name = base.generate_random_text()
        issue_title = base.generate_random_text()
        milestone_title = base.generate_random_text()
        repo = self.client.create_repo(name=self.repo_name, auto_init=True)

        base.info(self, "Create milestone")
        milestone = repo.create_milestone(title=milestone_title)

        base.info(self, "Create issue with milestone")
        issue_created = repo.create_issue(title=issue_title, milestone=milestone)

        base.info(self, "Check if issue has milestone")
        self.assertEqual(issue_created.milestone.title, milestone_title)
