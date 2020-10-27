from functools import lru_cache
from textwrap import dedent

from jumpscale.loader import j


class CircleResource:
    def __init__(self, taigaclient, original_object):
        self._original_object = original_object
        self._client = taigaclient
        self._api = self._client.api


class CircleIssue(CircleResource):
    def __init__(self, taigaclient, original_object):
        super().__init__(taigaclient, original_object)

    def __getattr__(self, attr):
        return getattr(self._original_object, attr)

    def __str__(self):
        return f"<Issue {self._original_object}>"

    @property
    def url(self):
        # https://circles.threefold.me/project/despiegk-tftech-software/issue/286
        return f"{self._client.host}/project/{self.project_extra_info.get('slug')}/issue/{self.id}"

    @property
    def as_md(self):
        TEMPLATE = dedent(
            """
            - **Subject:** [{{issue.subject}}]({{issue.url}})
            - **Created Date:** {{issue.created_date or 'unknown' }}
            - **Due Date:** {{issue.due_date or 'unknown' }}
            - **Owner Name:** {{issue.owner_extra_info.get('username', 'unknown')}}
            - **Owner Email:** {{issue.owner_extra_info.get('email', 'unknown')}}
            - **Project:** {{issue.project_extra_info.get('name', 'unknown')}}
    """
        )
        return j.tools.jinja2.render_template(template_text=TEMPLATE, issue=self)

    def __dir__(self):
        return dir(self._original_object) + ["as_md"]


class CircleStory(CircleResource):
    def __init__(self, taigaclient, original_object):
        super().__init__(taigaclient, original_object)

    def __getattr__(self, attr):
        return getattr(self._original_object, attr)

    def __str__(self):
        return f"<Story {self._original_object}>"

    @property
    def url(self):
        # https://circles.threefold.me/project/despiegk-tftech-software/us/214
        return f"{self._client.host}/project/{self.project_extra_info.get('slug')}/us/{self.id}"

    @property
    def as_md(self):
        TEMPLATE = dedent(
            """
            - **Subject:** [{{story.subject}}]({{story.url}})
            - **Assigned to:** {{story.assigned_to_extra_info and story.assigned_to_extra_info.get('username', 'not assigned') or 'not assigned' }}
            - **Watchers:** {{story.watchers or 'no watchers'}}
            - **Tasks**:

            """
        )
        return j.tools.jinja2.render_template(template_text=TEMPLATE, story=self)

    def tasks(self):
        # TODO
        pass

    def __dir__(self):
        return dir(self._original_object) + ["as_md"]


class CircleUser(CircleResource):
    def __init__(self, taigaclient, original_object):
        super().__init__(taigaclient, original_object)

    def __getattr__(self, attr):
        return getattr(self._original_object, attr)

    def __str__(self):
        return f"<User {self._original_object}>"

    @property
    def url(self):
        # https://circles.threefold.me/profile/ahartl
        return f"{self._client.host}/profile/{self.username}"

    @property
    def clean_name(self):
        return self.username.lower()

    def get_stories(self):
        return self._client.list_all_user_stories(self._original_object.username)

    def get_issues(self):
        return self._client.list_all_issues(self._original_object.username)

    def get_circles(self):
        circles = []
        all_circles = self._client.get_user_circles(self._original_object.username)
        for c in all_circles:
            cname = c.name.lower()
            if cname.startswith("team"):
                circles.append(TeamCircle(self._client, c))
            elif cname.startswith("funnel"):
                circles.append(FunnelCircle(self._client, c))
            elif cname.startswith("project"):
                circles.append(ProjectCircle(self._client, c))
            else:
                circles.append(Circle(self._client, c))
        return circles

    # TODO
    def get_tasks(self):
        pass

    @property
    def stories(self):
        res = []
        for s in self.get_stories():
            res.append(CircleStory(self._client, s))

        return res

    @property
    def issues(self):
        res = []
        for s in self.get_issues():
            res.append(CircleIssue(self._client, s))

        return res

    @property
    def circles(self):
        return self.get_circles()

    def __dir__(self):
        return dir(self._original_object) + ["as_md", "issues", "stories", "get_circles", "get_issues", "get_stories"]

    @property
    def as_md(self):

        TEMPLATE = dedent(
            """
            # {{user.username}}

            User profile is at: [{{user.url}}]({{user.url}})

            {% if user.circles %}
            ## Circles

            {% for c in user.circles %}

            - [{{c.name}}]({{c.clean_name}}.md) [{{c.url}}]({{c.url}})
            {% endfor %}

            {% endif %}

            {% if user.stories %}
            ## User stories
            {% for story in user.stories %}

            ### {{story.subject}}

            {{story.as_md}}

            {% endfor %}

            {% endif %}


            {% if user.issues %}
            ## Issues

            {% for issue in user.issues %}
            ### {{issue.subject}}

            {{issue.as_md}}

            {% endfor %}
            {% endif %}
                """
        )
        return j.tools.jinja2.render_template(template_text=TEMPLATE, user=self)


class Circle(CircleResource):
    def __init__(self, taigaclient, original_object):
        super().__init__(taigaclient, original_object)

    @property
    def clean_name(self):
        return self.slug.lower().replace("-", "_")

    @property
    def url(self):
        # https://circles.threefold.me/project/despiegk-tftech-software
        return f"{self._client.host}/project/{self.slug}"

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
        project_obj = project
        if not isinstance(issue, int):
            issue_id = issue.id
            issue_obj = issue
        else:
            issue_obj = self._client._get_issue_by_id(issue_id)

        if not isinstance(project, int):
            project_id = project.id
            project_obj = project
        else:
            project_obj = Circle(self._client, self._client._get_project(project_id))

        created = project_obj.create_issue(issue_obj.subject)
        if created:
            issue_obj.delete()
        return created

    def create_story(self, subject="", **attrs):
        return self._original_object.add_user_story(subject, **attrs)

    @property
    def stories(self):
        res = []
        for s in self._original_object.list_user_stories():
            res.append(CircleStory(self._client, s))

        return res

    @property
    def issues(self):
        res = []
        for s in self._original_object.list_issues():
            res.append(CircleIssue(self._client, s))
        return res

    @property
    def circle_users(self):
        return self._original_object.members_objects()

    def __dir__(self):
        return dir(self._original_object) + [
            "create_issue",
            "create_story",
            "move_issue",
            "get_project_info",
            "as_md",
            "issues",
            "stories",
            "circle_users",
        ]

    def __getattr__(self, attr):
        return getattr(self._original_object, attr)

    def __str__(self):
        return f"<Circle {self._original_object}>"

    @property
    def as_md(self):

        TEMPLATE = dedent(
            """
            # Circle {{project.name}}

            Homepage: {{project.url}}

            {% if project.stories %}
            ## Stories

            {% for story in project.stories %}

            ### {{story.subject}}
            {{story.as_md}}

            {% endfor %}

            {% endif %}


            {% if project.issues %}
            ## Issues

            {% for issue in project.issues %}

            ### {{issue.subject}}

            {{issue.as_md}}

            {% endfor %}

            {% endif %}

            """
        )
        return j.tools.jinja2.render_template(template_text=TEMPLATE, project=self)


class TeamCircle(Circle):
    def __init__(self, taigaclient, original_object):
        super().__init__(taigaclient, original_object)

    def __getattr__(self, attr):
        try:
            return getattr(self._original_object, attr)
        except Exception as e:
            if hasattr(self._original_object, "_original_object"):
                return getattr(self._original_object._original_object, attr)
            else:
                raise j.exceptions.Runtime(f"{attr} not found in {self} and not in {self._original_object}")

    def __str__(self):
        return f"<TeamCircle {self._original_object}>"


class FunnelCircle(Circle):
    def __init__(self, taigaclient, original_object):
        super().__init__(taigaclient, original_object)

    def __getattr__(self, attr):
        try:
            return getattr(self._original_object, attr)
        except Exception as e:
            if hasattr(self._original_object, "_original_object"):
                return getattr(self._original_object._original_object, attr)
            else:
                raise j.exceptions.Runtime(f"{attr} not found in {self} and not in {self._original_object}")

    def __str__(self):
        return f"<FunnelCircle {self._original_object}>"


class ProjectCircle(Circle):
    def __init__(self, taigaclient, original_object):
        super().__init__(taigaclient, original_object)

    def __getattr__(self, attr):
        try:
            return getattr(self._original_object, attr)
        except Exception as e:
            if hasattr(self._original_object, "_original_object"):
                return getattr(self._original_object._original_object, attr)
            else:
                raise j.exceptions.Runtime(f"{attr} not found in {self} and not in {self._original_object}")

    def __str__(self):
        return f"<ProjectCircle {self._original_object}>"
