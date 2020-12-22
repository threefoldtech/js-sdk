from functools import lru_cache
from textwrap import dedent

from jumpscale.loader import j
import yaml


class CircleResource:
    def __init__(self, taigaclient, original_object):
        self._original_object = original_object
        self._client = taigaclient
        self._api = self._client.api

    def check_by_name(self, list_obj, name_to_find):
        """Check if list contains name, used to check priorities, severities, statuses, types and etc
            and return the equivalent id.

        Args:
            list_obj (list): list of objects that we need to search into
            name_to_find (str): word to search for in the list

        Returns:
            int: Id of the matched object if found, or id of the first object in the list.
        """
        for obj in list_obj:
            if obj.name == name_to_find:
                return obj.id

        return list_obj[0].id


class CircleIssue(CircleResource):
    def __init__(self, taigaclient, original_object):
        super().__init__(taigaclient, original_object)

    def __getattr__(self, attr):
        return getattr(self._original_object, attr)

    def __str__(self):
        return f"<Issue {self._original_object}>"

    @property
    def url(self):
        # https://circles.threefold.me/project/despiegk-tftech-software/issue/55
        return f"{self._client.host}/project/{self.project_extra_info.get('slug')}/issue/{self.ref}"

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

    @property
    def as_yaml(self):
        obj = {}
        if self.assigned_to_extra_info is not None:
            obj["assigned_to"] = {
                "username": self.assigned_to_extra_info.get("username"),
                "id": self.assigned_to,
                "email": self.assigned_to_extra_info.get("email"),
            }
        obj["basic_info"] = {
            "subject": self.subject,
            "id": self.id,
            "description": self.description if hasattr(self, "description") else "",
            "tags": self.tags,
            "version": self.version,
            "url": self.url,
        }
        obj["project"] = {
            "name": self.project_extra_info.get("name"),
            "id": self.project,
        }
        obj["status"] = {
            "name": self.status_extra_info.get("name"),
            "id": self.status,
        }
        obj["severity"] = {
            "name": self._client.api.severities.get(self.severity).name,
            "id": self.severity,
        }
        obj["priority"] = {
            "name": self._client.api.priorities.get(self.priority).name,
            "id": self.priority,
        }
        obj["type"] = {
            "name": self._client.api.issue_types.get(self.type).name,
            "id": self.type,
        }
        obj["date"] = {
            "created_date": self.created_date,
            "modified_date": self.modified_date,
            "due_date": self.due_date,
            "due_date_reason": self.due_date_reason,
            "due_date_status": self.due_date_status,
            "finished_date": self.finished_date,
        }
        owner = {
            "username": self.owner_extra_info["username"],
            "id": self.owner,
            "email": self.owner_extra_info["email"],
        }
        watchers_objects = [self._client.api.users.get(id) for id in self.watchers]
        watchers = [f"({watcher.id}) {watcher.username}" for watcher in watchers_objects]
        obj["membership"] = {"owner": owner, "watchers": watchers}

        obj["statistics"] = {
            "total_voters": self.total_voters,
            "total_watchers": self.total_watchers,
        }
        obj["custom_fields"] = self._client.get_issue_custom_fields(self.id)
        obj["additional_info"] = {
            "is_blocked": self.is_blocked,
            "is_closed": self.is_closed,
            "is_voter": self.is_voter,
            "is_watcher": self.is_watcher,
            "blocked_note": self.blocked_note,
        }
        return yaml.dump(obj)

    def __dir__(self):
        return dir(self._original_object) + ["as_yaml", "url", "as_md"]


class CircleStory(CircleResource):
    def __init__(self, taigaclient, original_object):
        super().__init__(taigaclient, original_object)

    def __getattr__(self, attr):
        return getattr(self._original_object, attr)

    def __str__(self):
        return f"<Story {self._original_object}>"

    @property
    def url(self):
        # https://circles.threefold.me/project/despiegk-tftech-software/us/4
        return f"{self._client.host}/project/{self.project_extra_info.get('slug')}/us/{self.ref}"

    @property
    def circle_tasks(self):
        return [CircleTask(self._client, task) for task in self.list_tasks()]

    @property
    def as_md(self):
        TEMPLATE = dedent(
            """
            - **Subject:** [{{story.subject}}]({{story.url}})
            - **Assigned to:** {{story.assigned_to_extra_info and story.assigned_to_extra_info.get('username', 'not assigned') or 'not assigned' }}
            - **Watchers:** {{story.watchers or 'no watchers'}}
            {% if story.tasks %}
            - **Tasks**:
                {% for task in story.circle_tasks %}
                - [**{{task.subject}}**]({{task.url}})
                {% endfor %}
            {% endif %}
            """
        )
        return j.tools.jinja2.render_template(template_text=TEMPLATE, story=self)

    @property
    def as_yaml(self):
        obj = {}
        if self.assigned_to_extra_info is not None:
            obj["assigned_to"] = {
                "username": self.assigned_to_extra_info.get("username") or None,
                "id": self.assigned_to,
                "email": self.assigned_to_extra_info.get("email"),
            }

        obj["basic_info"] = {
            "subject": self.subject,
            "id": self.id,
            "description": self.description if hasattr(self, "description") else "",
            "tags": self.tags,
            "version": self.version,
            "url": self.url,
        }
        obj["project"] = {
            "name": self.project_extra_info.get("name"),
            "id": self.project,
        }
        obj["status"] = {
            "name": self.status_extra_info.get("name"),
            "id": self.status,
        }

        obj["date"] = {
            "created_date": self.created_date,
            "modified_date": self.modified_date,
            "due_date": self.due_date,
            "due_date_reason": self.due_date_reason,
            "due_date_status": self.due_date_status,
            "finish_date": self.finish_date,
        }
        owner = {
            "username": self.owner_extra_info["username"],
            "id": self.owner,
            "email": self.owner_extra_info["email"],
        }
        watchers_objects = [self._client.api.users.get(id) for id in self.watchers]
        watchers = [f"({watcher.id}) {watcher.username}" for watcher in watchers_objects]
        obj["membership"] = {"owner": owner, "watchers": watchers}
        obj["requirements"] = {
            "client_requirement": self.client_requirement,
            "team_requirement": self.team_requirement,
        }
        obj["statistics"] = {
            "total_attachments": self.total_attachments,
            "total_comments": self.total_comments,
            "total_voters": self.total_voters,
            "total_watchers": self.total_watchers,
        }
        obj["custom_fields"] = self._client.get_story_custom_fields(self.id)
        obj["tasks"] = [task.id for task in self.tasks]
        obj["additional_info"] = {
            "is_blocked": self.is_blocked,
            "is_closed": self.is_closed,
            "is_voter": self.is_voter,
            "is_watcher": self.is_watcher,
            "blocked_note": self.blocked_note,
            "generated_from_issue": self.generated_from_issue,
            "generated_from_task": self.generated_from_task,
        }
        return yaml.dump(obj)

    @property
    def tasks(self):
        return self.list_tasks()

    def __dir__(self):
        return dir(self._original_object) + ["as_yaml", "circle_tasks", "url", "as_md"]


class CircleTask(CircleResource):
    def __init__(self, taigaclient, original_object):
        super().__init__(taigaclient, original_object)

    def __getattr__(self, attr):
        return getattr(self._original_object, attr)

    def __str__(self):
        return f"<Task {self._original_object}>"

    @property
    def url(self):
        # https://circles.threefold.me/project/despiegk-tftech-software/task/2
        return f"{self._client.host}/project/{self.project_extra_info.get('slug')}/task/{self.ref}"

    @property
    def as_md(self):
        TEMPLATE = dedent(
            """
            - **Subject:** [{{task.subject}}]({{task.url}})
            - **Created Date:** {{task.created_date or 'unknown' }}
            - **Due Date:** {{task.due_date or 'unknown' }}
            - **Owner Name:** {{task.owner_extra_info.get('username', 'unknown')}}
            - **Owner Email:** {{task.owner_extra_info.get('email', 'unknown')}}
            - **Project:** {{task.project_extra_info.get('name', 'unknown')}}
            """
        )
        return j.tools.jinja2.render_template(template_text=TEMPLATE, task=self)

    @property
    def as_yaml(self):
        obj = {}
        if self.assigned_to_extra_info is not None:
            obj["assigned_to"] = {
                "username": self.assigned_to_extra_info.get("username") or None,
                "id": self.assigned_to,
                "email": self.assigned_to_extra_info.get("email"),
            }

        obj["basic_info"] = {
            "subject": self.subject,
            "id": self.id,
            "description": self.description if hasattr(self, "description") else "",
            "tags": self.tags,
            "version": self.version,
            "url": self.url,
        }
        obj["project"] = {
            "name": self.project_extra_info.get("name"),
            "id": self.project,
        }
        obj["status"] = {
            "name": self.status_extra_info.get("name"),
            "id": self.status,
        }
        obj["user_story"] = {
            "subject": self.user_story_extra_info.get("subject"),
            "id": self.user_story,
        }
        obj["date"] = {
            "created_date": self.created_date,
            "modified_date": self.modified_date,
            "due_date": self.due_date,
            "due_date_reason": self.due_date_reason,
            "due_date_status": self.due_date_status,
            "finished_date": self.finished_date,
        }
        owner = {
            "username": self.owner_extra_info["username"],
            "id": self.owner,
            "email": self.owner_extra_info["email"],
        }
        watchers_objects = [self._client.api.users.get(id) for id in self.watchers]
        watchers = [f"({watcher.id}) {watcher.username}" for watcher in watchers_objects]
        obj["membership"] = {"owner": owner, "watchers": watchers}
        obj["statistics"] = {
            "total_comments": self.total_comments,
            "total_voters": self.total_voters,
            "total_watchers": self.total_watchers,
        }
        obj["additional_info"] = {
            "is_blocked": self.is_blocked,
            "is_closed": self.is_closed,
            "is_voter": self.is_voter,
            "is_watcher": self.is_watcher,
            "blocked_note": self.blocked_note,
        }
        return yaml.dump(obj)

    def __dir__(self):
        return dir(self._original_object) + ["as_yaml", "url", "as_md"]


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
            elif cname.startswith("archive"):
                pass  # to not included in as_md property
            else:
                circles.append(Circle(self._client, c))
        return circles

    def get_tasks(self):
        return self._client.list_all_tasks(self._original_object.username)

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

    @property
    def tasks(self):
        return self.get_tasks()

    @property
    def as_md(self):

        TEMPLATE = dedent(
            """
            # {{user.username}}

            User profile is at: [{{user.url}}]({{user.url}})

            {% if user.circles %}
            ## Circles

            {% for c in user.circles %}

            '[{{c.name}}]({{c.clean_name}}.md) [{{c.url}}]({{c.url}})
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

            {% if user.tasks %}
            ## Tasks

            {% for task in user.tasks %}
            ### {{task.subject}}

            {{task.as_md}}

            {% endfor %}
            {% endif %}

            """
        )
        return j.tools.jinja2.render_template(template_text=TEMPLATE, user=self)

    @property
    def as_yaml(self):
        obj = {}
        obj["basic_info"] = {
            "username": self.username,
            "email": self.email,
            "id": self.id,
            "full_name": self.full_name,
            "bio": self.bio,
            "lang": self.lang,
            "public_key": self.public_key,
            "photo": self.photo,
            "url": self.url,
        }
        obj["date"] = {"date_joined": self.date_joined, "timezone": self.timezone}
        obj["statistics"] = {
            "total_private_projects": self.total_private_projects,
            "total_public_projects": self.total_public_projects,
        }
        obj["roles"] = self.roles
        obj["limits"] = {
            "max_memberships_private_projects": self.max_memberships_private_projects,
            "max_memberships_public_projects": self.max_memberships_public_projects,
            "max_private_projects": self.max_private_projects,
            "max_public_projects": self.max_memberships_public_projects,
        }
        obj["terms"] = {
            "accepted_terms": self.accepted_terms,
            "read_new_terms": self.read_new_terms,
        }
        return yaml.dump(obj)

    def __dir__(self):
        return dir(self._original_object) + [
            "as_yaml",
            "as_md",
            "issues",
            "stories",
            "tasks",
            "get_circles",
            "get_issues",
            "get_stories",
            "get_tasks",
            "url",
            "clean_name",
        ]


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

    def copy_issue(self, issue, project):
        """Copy issue to specific project

        Args:
            issue (int , CircleIssue): issue or issue id to be copied
            to_project (int, Circle, FunnelCircle, ProjectCircle, TeamCircle):  circle or circle id to copy issue into

        Returns:
            Issue: created issue object
        """
        issue_id = issue
        issue_obj = issue
        project_id = project
        project_obj = project
        if not isinstance(issue, int):
            issue_id = issue.id
            issue_obj = issue
        else:
            issue_obj = self._client.api.issues.get(issue_id)

        if not isinstance(project, int):
            project_id = project.id
            project_obj = project
        else:
            project_obj = Circle(self._client, self._client.api.projects.get(project_id))

        issue_priority = self.check_by_name(
            project_obj.priorities, self._client.api.priorities.get(issue_obj.priority).name
        )
        issue_type = self.check_by_name(
            project_obj.list_issue_types(), self._client.api.issue_types.get(issue_obj.type).name
        )
        issue_severity = self.check_by_name(
            project_obj.list_severities(), self._client.api.severities.get(issue_obj.severity).name
        )
        issue_status = self.check_by_name(project_obj.list_issue_statuses(), issue_obj.status_extra_info["name"])
        issue_custom_field = self._client.get_issue_custom_fields(issue_id)

        created = project_obj.add_issue(
            issue_obj.subject,
            issue_priority,
            issue_status,
            issue_type,
            issue_severity,
            description=issue_obj.description,
            watchers=issue_obj.watchers,
            assigned_to=issue_obj.assigned_to,
        )

        for field in issue_custom_field:
            is_found = False
            new_attr = None
            for attr in project_obj.list_issue_attributes():
                if attr.name == field["name"] and not is_found:
                    created.set_attribute(attr.id, field["value"])
                    is_found = True

            if not is_found:
                new_attr = project_obj.add_issue_attribute(field["name"])
                created.set_attribute(new_attr.id, field["value"])

        return created

    def move_issue(self, issue, project):
        """Move issue to specific project
        HINT: Move will delete the issue from original circle

        Args:
            issue (int , CircleIssue): issue or issue id to be movied
            to_project (int, Circle, FunnelCircle, ProjectCircle, TeamCircle):  circle or circle id to move issue into

        Returns:
            Issue: created issue object
        """
        issue_id = issue
        issue_obj = issue
        project_id = project
        project_obj = project
        if not isinstance(issue, int):
            issue_id = issue.id
            issue_obj = issue
        else:
            issue_obj = self._client.api.issues.get(issue_id)

        if not isinstance(project, int):
            project_id = project.id
            project_obj = project
        else:
            project_obj = Circle(self._client, self._client.api.projects.get(project_id))

        created = self.copy_issue(issue_obj, project_obj)

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
            "as_yaml",
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

            - Homepage: {{project.url}}
            - Modified Date: {{project.modified_date}}

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

    @property
    def as_yaml(self):
        obj = {}
        obj["basic_info"] = {
            "name": self.name,
            "slug": self.slug,
            "id": self.id,
            "description": self.description if hasattr(self, "description") else "",
            "tags": self.tags,
            "is_private": self.is_private,
            "looking_for_people_note": self.looking_for_people_note,
            "url": self.url,
        }
        obj["date"] = {
            "created_date": self.created_date,
            "modified_date": self.modified_date,
        }
        obj["modules"] = {
            "is_backlog_activated": self.is_backlog_activated,
            "is_issues_activated": self.is_issues_activated,
            "is_kanban_activated": self.is_kanban_activated,
            "is_wiki_activated": self.is_wiki_activated,
            "videoconferences": self.videoconferences,
        }
        owner = {
            "username": self.owner["username"],
            "id": self.owner["id"],
            "email": self.owner["email"],
        }
        members = [
            {"name": member.full_name, "id": member.id, "role": member.role_name,} for member in self.list_memberships()
        ]
        other_membership = {
            "i_am_owner": self.i_am_owner,
            "i_am_admin": self.i_am_admin,
            "i_am_member": self.i_am_member,
        }
        obj["membership"] = {
            "owner": owner,
            "members": members,
            "others": other_membership,
        }
        obj["statistics"] = {
            "total_activity": self.total_activity,
            "total_fans": self.total_fans,
            "total_watchers": self.total_watchers,
        }
        obj["stories"] = [story.id for story in self.stories]
        obj["stories_attributes"] = [st_attr.name for st_attr in self.list_user_story_attributes()]
        obj["issues"] = [issue.id for issue in self.issues]
        obj["issues_attributes"] = [issue_attr.name for issue_attr in self.list_issue_attributes()]
        return yaml.dump(obj)


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


class ArchiveCircle(Circle):
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
        return f"<ArchiveCircle {self._original_object}>"
