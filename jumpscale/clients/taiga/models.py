from functools import lru_cache


class UserEx:
    def __init__(self, api, original_object):
        self._original_object = original_object
        self._api = api

    def get_stories(self):
        pass

    def get_issues(self):
        pass

    def get_circles(self):
        pass


class TaigaProject:
    def __init__(self, api, original_object):
        self._original_object = original_object
        self._api = api

    def __dir__(self):
        return dir(self._original_object)

    def __getattr__(self, attr):
        return getattr(self._original_object, attr)

    def __str__(self):
        return f"<Project {self._original_object.id}: {self._original_object.name}>"

    @lru_cache(maxsize=128)
    def get_project_info(self):
        prios = list(map(lambda x: (str(x), x.id), self._original_object.list_priorities()))
        severities = list(map(lambda x: (str(x), x.id), self._original_object.list_severities()))
        statuses = list(map(lambda x: (str(x), x.id), self._original_object.list_issue_statuses()))
        issues_types = list(map(lambda x: (str(x), x.id), self._original_object.list_issue_types()))

        return f"prios: {prios}, severities: {severities}, issues_types: {issues_types}, statuses: {statuses}"

    def create_issue(self, subject, prio=None, status=None, issue_type=None, severity=None):
        prio = prio or self._original_object.list_priorities()[0].id
        status = status or self._original_object.list_issue_statuses()[0].id
        severity = severity or self._original_object.list_severities()[0].id
        issue_type = issue_type or self._original_object.list_issue_types()[0].id

        return self._original_object.add_issue(subject, prio, status, issue_type, severity)

    def move_issue(self, issue, project):
        issue_id = issue
        issue_obj = issue
        project_id = project
        projet_obj = project
        if not isinstance(issue, int):
            issue_id = issue.id
            issue_obj = issue
        else:
            issue_obj = self._api._get_issue_by_id(issue_id)

        if not isinstance(project, int):
            project_id = project.id
            project_obj = project
        else:
            project_obj = TaigaProject(self._api, self._api._get_project(project_id))

        created = project_obj.create_issue(issue_obj.subject)
        if created:
            issue_obj.delete()
        return created

    __repr__ = __str__


class Task:
    def __init__(self, api, original_object):
        self._original_object = original_object
        self._api = api


class Circle(TaigaProject):
    def __init__(self, api, original_object):
        self._original_object = original_object
        self._api = api

    def create_new_story(self, subject="", **attrs):
        return self._original_object.add_user_story(subject(subject, **attrs))


class TeamCircle(Circle):
    def __init__(self, api, original_object):
        self._original_object = original_object
        self._api = api


class FunnelCircle(Circle):
    def __init__(self, api, original_object):
        self._original_object = original_object
        self._api = api


class ProjectCircle(Circle):
    def __init__(self, api, original_object):
        self._original_object = original_object
        self._api = api
