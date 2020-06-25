from jumpscale.loader import j
from .base import base


class RepoMilestone(base):
    """
    milestone as defined on 1 specific repo
    """

    def __init__(self, repo, githubObj=None):
        base.__init__(self)
        self._ddict = {}
        self._githubObj = githubObj
        if githubObj is not None:
            self.load()
        self.repo = repo

    # @property
    # def api(self):
    #     if self._githubObj is None:
    #         j.application.break_into_jshell("DEBUG NOW get api for milestone")
    #     return self._githubObj

    def load(self):
        self._ddict = {}
        #self._ddict["deadline"] = j.data.time.any2HRDateTime(self.api.due_on)
        self._ddict["id"] = self.api.id
        self._ddict["url"] = self.api.url
        self._ddict["title"] = self.api.title
        self._ddict["body"] = self.api.description
        self._ddict["number"] = self.api.number

    @property
    def title(self):
        return self._ddict["title"]

    @title.setter
    def title(self, val):
        self._ddict["title"] = val
        self.api.edit(title=val)

    @property
    def ddict(self):
        if not self._ddict:
            # no dict yet, fetch from github
            self.load()
        return self._ddict



    # synonym to let the tags of super class work
    @property
    def body(self):
        return self._ddict["body"]

    @body.setter
    def body(self, val):
        if self._ddict["body"] != val:
            self._ddict["body"] = val
            self.api.edit(self.title, description=val)

    # @property
    # def deadline(self):
    #     return self._ddict["deadline"]

    # @deadline.setter
    # def deadline(self, val):
    #     #due = j.data.time.epoch2pythonDateTime(int(j.data.time.getEpochFuture(val)))

    #     self._ddict["deadline"] = val
    #     self.api.edit(title=self.title)

    @property
    def id(self):
        return self._ddict["id"]

    @property
    def url(self):
        return self._ddict["url"]

    @property
    def number(self):
        return self._ddict["number"]
