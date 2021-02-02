import base64
import copy
import threading

# import collections
import urllib

from gevent import sleep
from jumpscale.clients.base import Client
from jumpscale.core.base import Base, fields
from jumpscale.loader import j

from github.GithubException import UnknownObjectException

from .base import replacelabels
from .helper import retry
from .issue import Issue
from .milestone import RepoMilestone


class GithubRepo:
    TYPES = ["story", "ticket", "task", "bug", "feature", "question", "monitor", "unknown"]
    PRIORITIES = ["critical", "urgent", "normal", "minor"]

    STATES = ["new", "accepted", "question", "inprogress", "verification", "closed"]

    def __init__(self, client, fullname):
        self.client = client
        self.fullname = fullname
        self._repoclient = None
        self._labels = None
        self._issues = None
        self._lock = threading.RLock()
        self._milestones = None

    def _log_info(self, s):
        pass

    @property
    def api(self):
        if self._repoclient is None:
            self._repoclient = self.client.get_repo(self.fullname)
        return self._repoclient

    @property
    def name(self):
        return self.fullname.split("/", 1)[-1]

    @property
    def type(self):
        if self.name in ["home"]:
            return "home"
        elif self.name.startswith("proj"):
            return "proj"
        elif self.name.startswith("org_"):
            return "org"
        elif self.name.startswith("www"):
            return "www"
        elif self.name.startswith("doc"):
            return "doc"
        elif self.name.startswith("cockpit"):
            return "cockpit"
        else:
            return "code"

    @property
    def labelnames(self):
        return [item.name for item in self.labels]

    @property
    def labels(self):
        with self._lock:
            if self._labels is None:
                self._labels = [item for item in self.api.get_labels()]

        return self._labels

    @property
    def branches(self):
        """list of `Branch` objects"""
        return list(self.api.get_branches())

    @property
    def stories(self):
        # walk overall issues find the stories (based on type)
        # only for home type repo, otherwise return []
        return self.issues_by_type("story")

    @property
    def tasks(self):
        # walk overall issues find the stories (based on type)
        # only for home type repo, otherwise return []
        return self.issues_by_type("task")

    def labelsSet(self, labels2set, ignoreDelete=["p_"], delete=True):
        """
        @param ignore all labels starting with ignore will not be deleted
        """

        for item in labels2set:
            if not isinstance(item, str):
                raise Exception("Labels to set need to be in string format, found:%s" % labels2set)

        # walk over github existing labels
        labelstowalk = copy.copy(self.labels)
        for item in labelstowalk:
            name = item.name.lower()
            if name not in labels2set:
                # label in repo does not correspond to label we need
                if name in replacelabels:
                    nameNew = replacelabels[item.name.lower()]
                    if nameNew not in self.labelnames:
                        color = self.get_color(name)
                        self._log_info(
                            "change label in repo: %s oldlabel:'%s' to:'%s' color:%s"
                            % (self.fullname, item.name, nameNew, color)
                        )
                        item.edit(nameNew, color)
                        self._labels = None
                else:
                    # no replacement
                    name = "type_unknown"
                    color = self.get_color(name)
                    try:
                        item.edit(name, color)
                    except BaseException:
                        item.delete()
                    self._labels = None

        # walk over new labels we need to set
        for name in labels2set:
            if name not in self.labelnames:
                # does not exist yet in repo
                color = self.get_color(name)
                self._log_info("create label: %s %s %s" % (self.fullname, name, color))
                self.api.create_label(name, color)
                self._labels = None

        name = ""

        if delete:
            labelstowalk = copy.copy(self.labels)
            for item in labelstowalk:
                if item.name not in labels2set:
                    self._log_info("delete label: %s %s" % (self.fullname, item.name))
                    ignoreDeleteDo = False
                    for filteritem in ignoreDelete:
                        if item.name.startswith(filteritem):
                            ignoreDeleteDo = True
                    if ignoreDeleteDo is False:
                        item.delete()
                    self._labels = None

        # check the colors
        labelstowalk = copy.copy(self.labels)
        for item in labelstowalk:
            # we recognise the label
            self._log_info("check color of repo:%s labelname:'%s'" % (self.fullname, item.name))
            color = self.get_color(item.name)
            if item.color != color:
                self._log_info("change label color for repo %s %s" % (item.name, color))
                item.edit(item.name, color)
                self._labels = None

    def getlabel(self, name):
        for item in self.labels:
            self._log_info("%s:look for name:'%s'" % (item.name, name))
            if item.name == name:
                return item
        raise Exception("Dit not find label: '%s'" % name)

    def get_issue_from_markdown(self, issueNumber, markdown):
        i = self.get_issue(issueNumber, False)
        i._loadMD(markdown)
        self.issues.append(i)
        return i

    def get_issue(self, issueNumber, die=True):
        for issue in self.issues:
            if issue.number == issueNumber:
                return issue
        # not found in cache, try to load from github
        github_issue = self.api.get_issue(issueNumber)

        if github_issue:
            issue = Issue(repo=self, githubObj=github_issue)
            self._issues.append(issue)
            return issue

        if die:
            raise Exception("cannot find issue:%s in repo:%s" % (issueNumber, self))
        else:
            i = Issue(self)
            i._ddict["number"] = issueNumber
            return i

    def issues_by_type(self, *types):
        """
        filter is method which takes  issue as argument and returns True or False to include
        """
        issues = []
        for issue in self.issues:
            if issue.type in types:
                issues.append(issue)

        return issues

    def issues_by_state(self, filter=None):
        """
        filter is method which takes  issue as argument and returns True or False to include
        """
        res = {}
        for item in self.states:
            res[item] = []
            for issue in self.issues:
                if issue.state == item:
                    if filter is None or filter(issue):
                        res[item].append(issue)
        return res

    def issues_by_priority(self, filter=None):
        """
        filter is method which takes  issue as argument and returns True or False to include
        """
        res = {}
        for item in self.priorities:
            res[item] = []
            for issue in self.issues:
                if issue.priority == item:
                    if filter is None or filter(issue):
                        res[item].append(issue)
        return res

    def issues_by_type_state(self, filter=None, collapsepriority=True):
        """
        filter is method which takes  issue as argument and returns True or False to include
        returns dict of dict keys: type, state and then issues sorted following priority
        """
        res = {}
        for type in self.types:
            res[type] = {}
            for state in self.states:
                res[type][state] = {}
                for priority in self.priorities:
                    res[type][state][priority] = []
                    for issue in self.issues:
                        if issue.type == type and issue.state == state:
                            if filter is None or filter(issue):
                                res[type][state][priority].append(issue)
                if collapsepriority:
                    # sort the issues following priority
                    temp = res[type][state]
                    res[type][state] = []
                    for priority in self.priorities:
                        for subitem in temp[priority]:
                            res[type][state].append(subitem)
        return res

    @property
    def types(self):
        return GithubRepo.TYPES

    @property
    def priorities(self):
        return GithubRepo.PRIORITIES

    @property
    def states(self):
        return GithubRepo.STATES

    @property
    def milestones(self):
        if self._milestones is None:
            self._milestones = [RepoMilestone(self, x) for x in self.api.get_milestones()]

        return self._milestones

    @property
    def milestone_titles(self):
        return [item.title for item in self.milestones]

    @property
    def milestone_names(self):
        return [item.name for item in self.milestones]

    def get_milestone(self, name, die=True):
        name = name.strip()
        if name == "":
            raise Exception("Name cannot be empty.")
        for item in self.milestones:
            if name == item.name.strip() or name == item.title.strip():
                return item
        if die:
            raise Exception("Could not find milestone with name:%s" % name)
        else:
            return None

    @retry
    def create_milestone(self, name, title, description="", deadline="", owner=""):
        self._log_info('Attempt to create milestone "%s" [%s] deadline %s' % (name, title, deadline))

        def getBody(descr, name, owner):
            out = "%s\n\n" % descr
            out += "## name:%s\n" % name
            out += "## owner:%s\n" % owner
            return out

        ms = None
        for s in [name, title]:
            ms = self.get_milestone(s, die=False)
            if ms is not None:
                break

        if ms is not None:
            if ms.title != title:
                ms.title = title
            # if ms.deadline != deadline:
            #     ms.deadline = deadline
            tocheck = getBody(description.strip(), name, owner)
            if ms.body.strip() != tocheck.strip():
                ms.body = tocheck
        else:
            # due = j.data.time.epoch2pythonDateTime(int(j.data.time.getEpochFuture(deadline)))
            self._log_info("Create milestone on %s: %s" % (self, title))
            body = getBody(description.strip(), name, owner)
            # workaround for https://github.com/PyGithub/PyGithub/issues/396
            milestone = self.api.create_milestone(title=title, description=body)
            milestone.edit(title=title)

            self._milestones.append(RepoMilestone(self, milestone))

    def delete_milestone(self, name):
        if name.strip() == "":
            raise Exception("Name cannot be empty.")
        self._log_info("Delete milestone on %s: '%s'" % (self, name))
        try:
            ms = self.get_milestone(name)
            ms.api.delete()
            self._milestones = []
        except Exception:
            self._log_info("Milestone '%s' doesn't exist. no need to delete" % name)

    def _labelsubset(self, cat):
        res = []
        for item in self.labels:
            if item.startswith(cat):
                item = item[len(cat) :].strip("_")
                res.append(item)
        res.sort()
        return res

    def get_color(self, name):

        # colors={'state_question':'fbca04',
        #  'priority_urgent':'d93f0b',
        #  'state_verification':'006b75',
        #  'priority_minor':'',
        #  'type_task':'',
        #  'type_feature':'',
        #  'process_wontfix':"ffffff",
        #  'priority_critical':"b60205",
        #  'state_inprogress':"e6e6e6",
        #  'priority_normal':"e6e6e6",
        #  'type_story':"ee9a00",
        #  'process_duplicate':"",
        #  'state_closed':"5319e7",
        #  'type_bug':"fc2929",
        #  'state_accepted':"0e8a16",
        #  'type_question':"fbca04",
        #  'state_new':"1d76db"}

        if name.startswith("state"):
            return "c2e0c6"  # light green

        if name.startswith("process"):
            return "d4c5f9"  # light purple

        if name.startswith("type"):
            return "fef2c0"  # light yellow

        if name in ("priority_critical", "task_no_estimation"):
            return "b60205"  # red

        if name.startswith("priority_urgent"):
            return "d93f0b"

        if name.startswith("priority"):
            return "f9d0c4"  # roze

        return "ffffff"

    @retry
    def set_file(self, path, content, message="update file"):
        """
        Creates or updates the file content at path with given content
        :param path: file path `README.md`
        :param content: Plain content of file
        :return:
        """
        bytes = content.encode()
        encoded = base64.encodebytes(bytes)

        params = {"message": message, "content": encoded.decode()}

        path = urllib.parse.quote(path)
        try:
            obj = self.api.get_contents(path)
            params["sha"] = obj.sha
            if base64.decodebytes(obj.content.encode()) == bytes:
                return
        except UnknownObjectException:
            pass

        self._log_info('Updating file "%s"' % path)
        self.api._requester.requestJsonAndCheck("PUT", self.api.url + "/contents/" + path, input=params)

    @property
    def issues(self):
        with self._lock:
            if self._issues is None:
                issues = []
                for item in self.api.get_issues(state="all"):
                    issues.append(Issue(self, githubObj=item))

                self._issues = issues

        return self._issues

    def download_directory(self, src, download_dir, branch=None):
        dest = j.sals.fs.join_paths(download_dir, self.api.full_name)
        j.sals.fs.mkdirs(dest)
        branch = branch or self.api.default_branch
        contents = self.api.get_dir_contents(src, ref=branch)

        for content in contents:
            if content.type == "dir":
                dir_path = j.sals.fs.join_paths(dest, content.path)
                j.sals.fs.mkdirs(dir_path)
                self.download_directory(content.path, download_dir, branch)
            else:
                file_path = j.sals.fs.join_paths(dest, content.path)
                j.sals.fs.mkdirs(j.sals.fs.dirname(file_path))
                file_content = self.api.get_contents(content.path, ref=branch)
                with open(file_path, "+w") as f:
                    f.write(base64.b64decode(file_content.content).decode())

        return j.sals.fs.join_paths(dest, src)

    def get_git_tree(self, sha_or_branch):
        """return a list of `GitTreeElement` for every element in source tree"""
        return self.api.get_git_tree(sha_or_branch).tree

    def __str__(self):
        return "gitrepo:%s" % self.fullname

    __repr__ = __str__
