from gevent import sleep
from os import getenv

from jumpscale.loader import j
from tests.base_tests import BaseTests


class GithubClientTest(BaseTests):
    def setUp(self):
        super().setUp()
        self.instance_name = j.data.random_names.random_name()

        self.FAKE_EMAIL = getenv("FAKE_EMAIL")
        self.FAKE_GITHUB_TOKEN = getenv("FAKE_GITHUB_TOKEN")

        self.client = j.clients.github.get(self.instance_name)

        self.client.accesstoken = self.FAKE_GITHUB_TOKEN
        self.repo_name = ""
        self.directory_name = ""

        if not (self.FAKE_EMAIL and self.FAKE_GITHUB_TOKEN):
            raise Exception("Please add (FAKE_EMAIL, FAKE_GITHUB_TOKEN) as environment variables")

    def tearDown(self):
        if self.repo_name:
            self.client.delete_repo(repo_name=self.repo_name)

        if self.directory_name and j.sals.fs.exists(path=f"/tmp/{self.directory_name}/"):
            j.sals.fs.rmtree(f"/tmp/{self.directory_name}/")
        j.clients.github.delete(self.instance_name)

    def wait_for_deleting_repo(self, repo, timeout=5):
        for _ in range(timeout):
            if repo.name in str(self.client.get_repos()):
                sleep(1)
            else:
                return True
        return False

    def wait_for_creating_repo(self, repo, timeout=5):
        for _ in range(timeout):
            if repo.name not in str(self.client.get_repos()):
                sleep(1)
            else:
                return True
        return False

    def test01_github_client_get_access(self):
        """Test case for get access to client.

        **Test Scenario**

        - Get client userdata.
        - Check client email.
        """
        self.assertEqual(self.client.get_userdata()["emails"][0]["email"], self.FAKE_EMAIL)

    def test02_github_create_repo(self):
        """Test case for creating a repository.

        **Test Scenario**

        - Get a github client.
        - Create a repository.
        - Check that this repository has been created.
        """
        self.info("Create a repository")
        self.repo_name = self.random_name()
        repo = self.client.create_repo(name=self.repo_name)

        self.info("Check that this repository has been created")
        self.assertTrue(self.wait_for_creating_repo(repo))

    def test03_github_delete_repo(self):
        """Test case for deleting a repository.

        **Test Scenario**

        - Get a github client.
        - Create a repository.
        - Delete this repository.
        - Check that this repository has been deleted.
        """
        self.info("Create a repository")
        repo_name = self.random_name()
        repo = self.client.create_repo(name=repo_name)
        self.assertTrue(self.wait_for_creating_repo(repo), "repository is not created after 5 second")

        self.info("Delete this repository")
        self.client.delete_repo(repo_name=repo.name)

        self.info("Check that this repository has been deleted")
        self.assertTrue(self.wait_for_deleting_repo(repo), "repository is not deleted after 5 second")

    def test04_github_set_file(self):
        """Test case for set a file to repository.

        **Test Scenario**

        - Get a github client.
        - Create repository with auto init.
        - Create file and set to repository.
        - Download directory.
        - Check if file has been sent.
        - Check downloaded file content.
        """

        self.info("Create repository with auto init")
        self.repo_name = self.random_name()
        dir_name = self.random_name()
        f_name = self.random_name()
        content = self.random_name()
        created_repo = self.client.create_repo(name=self.repo_name, auto_init=True)
        self.assertTrue(self.wait_for_creating_repo(created_repo), "repository is not created after 5 second")
        repo = self.client.get_repo(repo_full_name=created_repo.full_name)

        self.info("Create file and set to repository")
        repo.set_file(path=f"{dir_name}/{f_name}.txt", content=content)

        self.info("Download directory")
        repo.download_directory(src="", download_dir="/tmp")
        self.directory_name = repo.fullname.split("/")[0]

        self.info("Check if file has been sent")
        self.assertEqual(j.sals.fs.is_file(f"/tmp/{repo.fullname}/{dir_name}/{f_name}.txt"), True)

        self.info("Check downloaded file content")
        self.assertEqual(content, j.sals.fs.read_file(f"/tmp/{repo.fullname}/{dir_name}/{f_name}.txt"))

    def test05_github_create_milestoes(self):
        """Test case for creating a milestones.

        **Test Scenario**

        - Get a github client.
        - Create repository with auto init.
        - Create milestones.
        - Check if milestones has been created.
        """
        self.info("Create repository with auto init")
        self.repo_name = self.random_name()
        title = self.random_name()
        repo = self.client.create_repo(name=self.repo_name, auto_init=True)

        self.info("Create milestones")
        ceated_milestone = repo.create_milestone(title=title)

        self.info("Check if milestones has been created")
        milestone = repo.get_milestone(number=ceated_milestone.number)
        self.assertEqual(title, milestone.title)

    def test06_github_create_issue(self):
        """Test case for creating issue.

        **Test Scenario**

        - Get a github client.
        - Create repository with auto init.
        - Create issue.
        - Check if issue has been created.
        """

        self.info("Create repository with auto init")
        self.repo_name = self.random_name()
        issue_title = self.random_name()
        repo = self.client.create_repo(name=self.repo_name, auto_init=True)

        self.info("Create issue")
        issue_created = repo.create_issue(title=issue_title)

        self.info("Check if issue has been created")
        self.assertEqual(issue_created.title, issue_title)

    def test07_github_issue_with_milestone(self):
        """Test case for creating issue with milestone.

        **Test Scenario**

        - Create repository with auto init.
        - Create milestone.
        - Create issue with milestone.
        - Check if issue have a milestone.
        """

        self.info("Create repository with auto init")
        self.repo_name = self.random_name()
        issue_title = self.random_name()
        milestone_title = self.random_name()
        repo = self.client.create_repo(name=self.repo_name, auto_init=True)

        self.info("Create milestone")
        milestone = repo.create_milestone(title=milestone_title)

        self.info("Create issue with milestone")
        issue_created = repo.create_issue(title=issue_title, milestone=milestone)

        self.info("Check if issue have a milestone")
        self.assertEqual(issue_created.milestone.title, milestone_title)
