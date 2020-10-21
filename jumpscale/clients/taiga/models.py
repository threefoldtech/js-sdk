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
