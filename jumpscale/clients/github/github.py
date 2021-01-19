from gevent import sleep
from jumpscale.clients.base import Client
from jumpscale.core.base import Base, fields
from jumpscale.loader import j

from github import Github, GithubObject

from .repo import GithubRepo
from .helper import retry

NotSet = GithubObject.NotSet


class GithubClient(Client):
    username = fields.String()
    password = fields.String()
    accesstoken = fields.String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = None

    @property
    def github_client(self):
        if not self.__client:
            if self.accesstoken:
                self.__client = Github(self.accesstoken)
            else:
                self.__client = Github(login_or_token=self.username, password=self.password)
        return self.__client

    @retry
    def get_repo(self, repo_full_name):
        return GithubRepo(self.github_client, repo_full_name)

    @retry
    def get_repos(self):
        l = []
        for r in self.github_client.get_user().get_repos():
            l.append(GithubRepo(self.github_client, r.full_name))
        return l

    @retry
    def get_orgs(self):
        l = []
        for o in self.github_client.get_user().get_orgs():
            l.append(o.login)
        return l

    @retry
    def get_userdata(self):
        u = self.github_client.get_user()
        el = []
        for e in u.get_emails():
            el.append(e)
        return {"name": u.name, "emails": el, "id": u.id, "avatar_url": u.avatar_url}

    @retry
    def create_repo(
        self,
        name,
        description=NotSet,
        homepage=NotSet,
        private=NotSet,
        has_issues=NotSet,
        has_wiki=NotSet,
        has_downloads=NotSet,
        auto_init=NotSet,
        gitignore_template=NotSet,
    ):

        return self.github_client.get_user().create_repo(
            name,
            description=description,
            homepage=homepage,
            private=private,
            has_issues=has_issues,
            has_wiki=has_wiki,
            has_downloads=has_downloads,
            auto_init=auto_init,
            gitignore_template=gitignore_template,
        )

    @retry
    def delete_repo(self, repo_name):
        return self.github_client.get_user().get_repo(repo_name).delete()
