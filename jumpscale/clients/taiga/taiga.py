"""
# Taiga client

## Initialization

Using username and  password:
```
client = j.clients.taiga.new('test', host="https://staging.circles.threefold.me/", username='admin', password='123456')
```
OR using a token

```
client = j.clients.taiga.new('test', host="https://staging.circles.threefold.me/", token='extra secret token string')
```
## Listing

### Listing issues

To get the issues of the user with id 123:
```
client.list_all_issues(123)
```
To get the issues of all users:
```
client.list_all_issues()

```
### Listing projects

To list all projects:
```
client.list_all_projects()
```

To list all projects not start with **ARCHIVE**:
```
client.list_all_active_projects()

```
### Listing user stories

To list the user stories of the user with id 123:

```
client.list_all_user_stories(123)
```

To list the user stories of all users:

```
client.list_all_user_stories()
```

### Listing tasks

To list the tasks of the user with id 123:

```
client.list_all_tasks(123)
```

To list the tasks of all users :

```
client.list_all_tasks()
```


### List team circles

```
client.list_team_circles()
```


### List project circles

```
client.list_project_circles()
```

### List funnel circles

```
client.list_funnel_circles()

```

## Custom Fields

### Get

To get issue custom fields for the issue with id 123

```
custom_fields = client.get_issue_custom_fields(123)
```

To get user story custom fields for the story with id 123

```
custom_fields = client.get_story_custom_fields(123)
```

### Validate

To validate custom field according to [specs](https://github.com/threefoldtech/circles_reporting_tool/blob/master/specs/funnel.md#custom-fields)

```
client.validate_custom_fields(custom_fields)
```

## Creating

### Create new circle

if you want full control on the circle creation on priorities, severities, .. etc, you can use `_create_new_circle` method


```
def _create_new_circle(
    self,
    name,
    type_="team",
    description="desc",
    severities=None,
    issues_statuses=None,
    priorities=None,
    issues_types=None,
    user_stories_statuses=None,
    tasks_statuses=None,
    custom_fields=None
    **attrs,
):
```
otherwise you can use `create_new_project_circle,`, `create_new_team_circle`, `create_new_funnel_circle`


### Create new story

```
circle_object.create_story("abc")
```

### Create a new  issue

```
create_issue("my issue")
```

## Exporting

### Export users and circles

```
client.export_as_md("/tmp/taigawiki")
```

### Export users

```
client.export_users_as_md("/tmp/taigawiki")
```
### Export circles
```
client.export_circles_as_md("/tmp/taigawiki")
```

### Export users and circles periodically

To export users and circles periodically each 10 minutes
```
client.export_as_md_periodically("/tmp/taigawiki", period= 600)
```
> **period** use seconds as time unit.

### Export objects as yaml
To export All objects as yaml all you need is

```
client.export_as_yaml("/tmp/exported_taiga_dir")
```

This will export resources (users, projects, issues, stories, tasks) in `/tmp/exported_taiga_dir/$object_type/$object_id.yaml

## Importing

### Importing from yaml files

To import from yaml files _files which exported using export_as_yaml_

```
client.import_from_yaml("/tmp/exported_taiga_dir")
```
This will import resources (projects, issues, stories, tasks) as a new instance _import basic info till now_

## Operations

### Move a story to a project

```
client.move_story_to_circle(789, 123) # story id, project id
```

### Copy and Move Issue using project object
```
project_object.copy_issue(issue_id_or_issue_object, project_id_or_project_object)
project_object.move_issue(issue_id_or_issue_object, project_id_or_project_object)
```
> Keep in mind that move will delete the issue from the original project

### Resources urls
All of resources e.g (user, issue, user_story, circle, task) have `url, as_md and as_yaml` properties
"""

import copy
from collections import defaultdict
from functools import lru_cache
from textwrap import dedent
import dateutil
import dateutil.utils
import gevent
from gevent.event import Event
import yaml
from jumpscale.clients.base import Client
from jumpscale.clients.taiga.models import (
    Circle,
    CircleIssue,
    CircleStory,
    CircleTask,
    CircleUser,
    FunnelCircle,
    ProjectCircle,
    TeamCircle,
)
from jumpscale.core.base import fields
from jumpscale.loader import j

from taiga import TaigaAPI
from taiga.exceptions import TaigaRestException
from taiga.models.models import Milestones
from pathlib import Path


class TaigaClient(Client):
    def credential_updated(self, value):
        self._api = None

    host = fields.String(default="https://projects.threefold.me")
    username = fields.String(on_update=credential_updated)
    password = fields.Secret(on_update=credential_updated)
    token = fields.Secret(on_update=credential_updated)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api = None
        self.text = ""

    def __hash__(self):
        return hash(str(self))

    @property
    def api(self):
        if not self._api:
            api = TaigaAPI(host=self.host)
            if self.token:
                api.token = self.token
            else:
                if not self.username or not self.password:
                    raise j.exceptions.Runtime("Token or username and password are required")
                api.auth(self.username, self.password)
            self._api = api
        return self._api

    @lru_cache(maxsize=2048)
    def _get_project(self, project_id):
        return self.api.projects.get(project_id)

    @lru_cache(maxsize=2048)
    def _get_milestone(self, milestone_id):
        if milestone_id:
            return self.api.milestones.get(milestone_id)

    @lru_cache(maxsize=2048)
    def _get_priority(self, priority_id):
        return self.api.priorities.get(priority_id)

    @lru_cache(maxsize=2048)
    def _get_assignee(self, assignee_id):
        return CircleUser(self, self.api.users.get(assignee_id))

    _get_user_by_id = _get_assignee

    def _get_users_by_ids(self, ids=None):
        ids = ids or []
        return [self._get_user_by_id(x) for x in ids]

    def _get_issues_by_ids(self, ids=None):
        ids = ids or []
        return [self._get_issue_by_id(x) for x in ids]

    def _get_task_by_id(self, id):
        return self.api.tasks.get(id)

    @lru_cache(maxsize=2048)
    def _get_issue_status(self, status_id):
        return self.api.issue_statuses.get(status_id)

    @lru_cache(maxsize=2048)
    def _get_user_stories_status(self, status_id):
        return self.api.user_story_statuses.get(status_id)

    @lru_cache(maxsize=2048)
    def _get_task_status(self, status_id):
        return self.api.task_statuses.get(status_id)

    @lru_cache(maxsize=2048)
    def _get_user_id(self, username):
        user = self.api.users.list(username=username)
        if user:
            user = user[0]
            return user.id
        else:
            raise j.exceptions.Input(f"Couldn't find user with username: {username}")

    @lru_cache(maxsize=2048)
    def _get_user_by_name(self, username):
        theid = self._get_user_id(username)
        return self._get_user_by_id(theid)

    def get_issue_custom_fields(self, id):
        """Get Issue Custom fields

        Args:
            id (int): Issue id

        Returns:
            List: List of dictionaries {name: "custom field name", value: {values as dict}}
        """
        issue = self.api.issues.get(id)
        issue_attributes = issue.get_attributes()["attributes_values"]
        project_attributes = self._get_project(issue.project).list_issue_attributes()
        custom_fields = []
        for p_attr in project_attributes:
            for k, value in issue_attributes.items():
                if p_attr.id == int(k):
                    try:
                        custom_fields.append({"name": p_attr.name, "value": yaml.full_load(value)})
                    except:
                        custom_fields.append({"name": p_attr.name, "value": value})
                    break

        return custom_fields

    def get_story_custom_fields(self, id):
        """Get User_Story Custom fields

        Args:
            id (int): User_Story id

        Returns:
            List: List of dictionaries {name: "custom field name", value: {values as dict}}
        """
        user_story = self.api.user_stories.get(id)
        user_story_attributes = user_story.get_attributes()["attributes_values"]
        project_attributes = self._get_project(user_story.project).list_user_story_attributes()
        custom_fields = []
        for p_attr in project_attributes:
            for k, value in user_story_attributes.items():
                if p_attr.id == int(k):
                    try:
                        custom_fields.append({"name": p_attr.name, "value": yaml.full_load(value)})
                    except:
                        custom_fields.append({"name": p_attr.name, "value": value})
                    break

        return custom_fields

    def get_user_circles(self, username):
        """Get circles owned by user

        Args:
            username (str): Name of the user
        """
        user_id = self._get_user_id(username)
        circles = self.api.projects.list(member=user_id)
        user_circles = []
        for circle in circles:
            if circle.owner["id"] == user_id:
                user_circles.append(self._resolve_object(circle))
        return user_circles

    def get_circles_issues(self, project_id):
        """Get all issues in a circle/project

        Args:
            project_id (int): id of the circle/project

        Raises:
            j.exceptions.NotFound: if couldn't find circle with specified id
        """
        try:
            circle = self.api.projects.get(project_id)
        except TaigaRestException:
            raise j.exceptions.NotFound(f"Couldn't find project with id: {project_id}")

        circle_issues = []
        for issue in circle.list_issues():
            issue.project = self._get_project(issue.project)
            issue.milestone = self._get_milestone(issue.milestone)
            issue.priority = self._get_priority(issue.priority)
            issue.assignee = self._get_assignee(issue.assigned_to)
            issue.status = self._get_issue_status(issue.status)
            circle_issues.append(issue)
        return circle_issues

    def get_user_stories(self, username):
        """Get all stories of a user

        Args:
            username (str): Name of the user
        """
        user_id = self._get_user_id(username)
        user_stories = self.api.user_stories.list(assigned_to=user_id)
        user_stories = []
        for user_story in user_stories:
            # user_story.project = self._get_project(user_story.project)
            # user_story.milestone = self._get_milestone(user_story.milestone)
            user_story.status = self._get_user_stories_status(user_story.status)
            user_stories.append(user_story)
        return user_stories

    def get_user_tasks(self, username):
        """Get all tasks of a user

        Args:
            username (str): Name of the user
        """
        user_id = self._get_user_id(username)
        user_tasks = self.api.tasks.list(assigned_to=user_id)
        user_tasks = []
        for user_task in user_tasks:
            # user_task.project = self._get_project(user_task.project)
            # user_task.milestone = self._get_milestone(user_task.milestone)
            user_task.status = self._get_task_status(user_task.status)
            user_tasks.append(self._resolve_object(user_task))

        return user_tasks

    def move_story_to_circle(self, story_id, project_id):
        """Moves a story to another circle/project

        Args:
            story_id (int): User story id
            project_id (int): circle/project id

        Raises:
            j.exceptions.NotFound: No user story with specified id found
            j.exceptions.NotFound: No project with specified id found
            j.exceptions.Runtime: [description]

        Returns:
            int: New id of the migrated user story
        """

        def _get_project_status(project_statuses, status):
            for project_status in project_statuses:
                if project_status.name == status:
                    return project_status.id

        try:
            user_story = self.api.user_stories.get(story_id)
        except TaigaRestException:
            raise j.exceptions.NotFound(f"Couldn't find user story with id: {story_id}")

        project_stories_statuses = self.api.user_story_statuses.list(project=project_id)
        status = self._get_user_stories_status(user_story.status)
        story_status_id = _get_project_status(project_stories_statuses, status)

        try:
            migrate_story = self.api.user_stories.create(
                project=project_id,
                subject=user_story.subject,
                assigned_to=user_story.assigned_to,
                milestone=user_story.milestone,
                status=story_status_id,
                tags=user_story.tags,
            )
        except TaigaRestException:
            raise j.exceptions.NotFound(f"No project with id: {project_id} found")
        try:
            comments = self.api.history.user_story.get(story_id)
            comments = sorted(comments, key=lambda c: dateutil.parser.isoparse(c["created_at"]))

            for comment in comments:
                migrate_story.add_comment(comment["comment_html"])

            project_tasks_statuses = self.api.task_statuses.list(project=project_id)
            for task in user_story.list_tasks():
                status = self._get_task_status(task.status)
                task_status_id = _get_project_status(project_tasks_statuses, status)
                migrate_task = migrate_story.add_task(
                    subject=task.subject,
                    status=task_status_id,
                    due_date=task.due_date,
                    milestone=task.milestone,
                    assigned_to=task.assigned_to,
                    tags=task.tags,
                    project=migrate_story.project,
                    user_story=migrate_story.id,
                )
                comments = self.api.history.task.get(migrate_task.id)
                comments = sorted(comments, key=lambda c: dateutil.parser.isoparse(c["created_at"]))

                for comment in comments:
                    migrate_task.add_comment(comment["comment_html"])

        except Exception as e:
            self.api.user_stories.delete(migrate_story.id)
            raise j.exceptions.Runtime(f"Failed to migrate story error was: {str(e)}")

        self.api.user_stories.delete(story_id)
        return migrate_story.id

    def list_all_issues(self, username="", full_info=False):
        """
        List all issues for specific user if you didn't pass user_id will list all the issues
        HINT: Using full_info will take a longer time

        Args:
            username (str): username.
            full_info (bool): flag used to get object with full info. Defaults to False.

        Returns:
            List: List of taiga.models.models.Issue.
        """
        if username:
            user_id = self._get_user_id(username)
            if not full_info:
                return [CircleIssue(self, self._resolve_object(x)) for x in self.api.issues.list(assigned_to=user_id)]
            else:
                return [CircleIssue(self, self.api.issues.get(x.id)) for x in self.api.issues.list(assigned_to=user_id)]
        else:
            if not full_info:
                return [CircleIssue(self, self._resolve_object(x)) for x in self.api.issues.list()]
            else:
                return [CircleIssue(self, self.api.issues.get(x.id)) for x in self.api.issues.list()]

    def list_all_tasks(self, username="", full_info=False):
        """
        List all tasks for specific user if you didn't pass user_id will list all the tasks
        HINT: Using full_info will take a longer time

        Args:
            username (str): username.
            full_info (bool): flag used to get object with full info. Defaults to False.

        Returns:
            List: List of taiga.models.models.Task.
        """
        if username:
            user_id = self._get_user_id(username)
            if not full_info:
                return [CircleTask(self, self._resolve_object(x)) for x in self.api.tasks.list(assigned_to=user_id)]
            else:
                return [CircleTask(self, self.api.tasks.get(x.id)) for x in self.api.tasks.list(assigned_to=user_id)]
        else:
            if not full_info:
                return [CircleTask(self, self._resolve_object(x)) for x in self.api.tasks.list()]
            else:
                return [CircleTask(self, self.api.tasks.get(x.id)) for x in self.api.tasks.list()]

    def list_all_projects(self, full_info=False):
        """
        List all projects
        HINT: Using full_info will take a longer time

        Args:
            full_info(bool): flag used to get object with full info. Defaults to False.

        Returns:
            List: List of taiga.models.models.Project.
        """
        if not full_info:
            return [Circle(self, self._resolve_object(x)) for x in self.api.projects.list()]
        else:
            return [Circle(self, self.api.projects.get(x.id)) for x in self.api.projects.list()]

    def list_all_active_projects(self, full_info=False):
        """
        List all projects not starting with "ARHCIVE"
        HINT: Using full_info will take a longer time

        Args:
            full_info (bool): [description]. Defaults to False.

        Returns:
            [type]: [description]
        """
        return [
            Circle(self, p)
            for p in self.list_projects_by(lambda x: not x.name.startswith("ARCHIVE_"), full_info=full_info)
        ]

    def list_all_milestones(self):
        """
        List all milestones

        Returns:
            List: List of taiga.models.models.Milestone.
        """
        return [self._resolve_object(x) for x in self.api.milestones.list()]

    def list_all_user_stories(self, username="", full_info=False):
        """
        List all user stories for specific user if you didn't pass user_id will list all the available user stories
        HINT: Using full_info will take a longer time

        Args:
            username (str): username.
            full_info(bool): flag used to get object with full info. Defaults to False

        Returns:
            List: List of CircleStory.
        """
        if username:
            user_id = self._get_user_id(username)
            if not full_info:
                return [
                    CircleStory(self, self._resolve_object(x)) for x in self.api.user_stories.list(assigned_to=user_id)
                ]
            else:
                return [
                    CircleStory(self, self.api.user_stories.get(x.id))
                    for x in self.api.user_stories.list(assigned_to=user_id)
                ]
        else:
            if not full_info:
                return [CircleStory(self, self._resolve_object(x)) for x in self.api.user_stories.list()]
            else:
                return [CircleStory(self, self.api.user_stories.get(x.id)) for x in self.api.user_stories.list()]

    def list_all_users(self, full_info=False):
        """
        List all user stories for specific user if you didn't pass user_id will list all the available user stories
        HINT: Using full_info will take a longer time
        Args:
            username (str): username.
            full_info(bool): flag used to get object with full info. Defaults to False

        Returns:
            List: List of CircleUser.
        """
        circles = self.list_all_projects()
        users = set()
        for c in circles:
            for m in c.members:
                users.add(m)

        return [CircleUser(self, self._get_user_by_id(uid)) for uid in users]

    def get_issue_by_id(self, issue_id):
        """Get issue
        Args:
            issue_id: the id of the desired issue

        Returns:
            Issue object: issue
        """
        return CircleIssue(self, self.api.issues.get(issue_id))

    def _resolve_object(self, obj):
        resolvers = {
            "owners": self._get_users_by_ids,
            "watchers": self._get_users_by_ids,
            "members": self._get_users_by_ids,
            "project": self._get_project,
            "circle": self._get_project,
            "milestone": self._get_milestone,
            "task_status": self._get_task_status,
            "assigned_to": self._get_user_by_id,
            "owner": self._get_user_by_id,
            "issues": self._get_issues_by_ids,
            "tasks": self._get_task_by_id,
        }
        newobj = copy.deepcopy(obj)
        for k in dir(newobj):
            v = getattr(newobj, k)
            if isinstance(v, int) or isinstance(v, list) and v and isinstance(v[0], int):
                if k in resolvers:
                    resolved = None
                    resolver = resolvers[k]
                    try:
                        copied_v = copy.deepcopy(v)
                        resolved = lambda: resolver(copied_v)

                        if isinstance(v, list):
                            setattr(newobj, f"{k}_objects", resolved)
                        else:
                            setattr(newobj, f"{k}_object", resolved)

                    except Exception as e:
                        import traceback

                        traceback.print_exc()

                        j.logger.error(f"error {e}")

        return newobj

    def list_projects_by(self, fn=lambda x: True, full_info=False):
        return [p for p in self.list_all_projects(full_info=full_info) if fn(p)]

    def list_team_circles(self):
        return [TeamCircle(self, p) for p in self.list_projects_by(lambda x: x.name.startswith("TEAM_"))]

    def list_project_circles(self):
        return [ProjectCircle(self, p) for p in self.list_projects_by(lambda x: x.name.startswith("PROJECT_"))]

    def list_funnel_circles(self):
        return [FunnelCircle(self, p) for p in self.list_projects_by(lambda x: x.name.startswith("FUNNEL_"))]

    def validate_custom_fields(self, attributes):
        """Validate custom fields values to match our requirements

        Args:
            attributes (List): Output from get_issue/story_custom_fields functions

        Raises:
            j.exceptions.Validation: Raise validation exception if any input not valid

        Returns:
            bool: Return True if no exception raised and print logs
        """

        for attr in attributes:
            name = attr.get("name")
            value = attr.get("value")

            period = value.get("period", "onetime")
            duration = value.get("duration", 1)
            amount = value.get("amount", 0)
            currency = value.get("currency", "eur")
            start_date = value.get("start_date", f"{dateutil.utils.today().month}:{dateutil.utils.today().year}",)
            confidence = value.get("confidence", 100)
            user = value.get("user")
            part = value.get("part", "0%")
            type = value.get("type", "revenue")

            if name not in ["bookings", "commission"]:
                raise j.exceptions.Validation(
                    f'Name: ({name}) is unknown custom field, please select one of the following ["bookings", "commission"]'
                )

            if period not in ["onetime", "month", "year"]:
                raise j.exceptions.Validation(
                    f'Period: ({period}) not found, please select one of following ["onetime", "month", "year"]'
                )

            if duration < 1 or duration > 120:
                raise j.exceptions.Validation(f"Duration: ({duration}) is not in range, please select it from 1 to 120")

            if not isinstance(amount, int):
                raise j.exceptions.Validation(f"Amount: ({amount}) is not integer, please add int value")

            if currency.replace(" ", "").lower() not in [
                "usd",
                "chf",
                "eur",
                "gbp",
                "egp",
            ]:
                raise j.exceptions.Validation(
                    f'Currency: ({currency}) is not supported, please use one of the following currencies ["usd", "chf", "eur", "gbp", "egp"]'
                )
            try:
                date = start_date.split(":")
                month = int(date[0])
                year = int(date[1]) if len(date) > 1 else dateutil.utils.today().year
                if month < 1 or month > 12:
                    raise j.exceptions.Validation(
                        "Please use values from 1 to 12 in Month field, follow format like MONTH:YEAR as 11:2020 or MONTH as 11"
                    )
            except ValueError as e:
                raise j.exceptions.Validation(
                    "Please use numeric date with the following format MONTH:YEAR as 11:2020 or MONTH as 11"
                )
            except AttributeError as e:
                pass  # Will check what happen if start_date not provide

            if confidence % 10 != 0:
                j.exceptions.Validation(f"Confidence: ({confidence}) not multiple of 10, it must be multiple of 10")

            part_tmp = part.replace("%", "")
            if user != None and user not in self.list_all_users():
                raise j.exceptions.Validation(f"User: ({user}) is not found")

            if int(part_tmp) < 0 or int(part_tmp) > 100:
                j.exceptions.Validation(f"Part: ({part}) is a not a valid percentage, it must be from 0% to 100%")

            if type not in ["revenue", "booking"]:
                raise j.exceptions.Validation(
                    f'Type: ({type}) is not supported type, please choose one of the following ["revenue" , "booking"]'
                )

            j.logger.info(f"Attribute: {name} passed")

        return True

    def _create_new_circle(
        self,
        name,
        type_="team",
        description="desc",
        severities=None,
        issues_statuses=None,
        priorities=None,
        issues_types=None,
        user_stories_statuses=None,
        tasks_statuses=None,
        custom_fields=None,
        **attrs,
    ):
        severities = severities or ["Low", "Mid", "High"]
        priorities = priorities or [
            "Wishlist",
            "Minor",
            "Normal",
            "Important",
            "Critical",
        ]
        issues_statuses = issues_statuses or [
            "New",
            "In progress",
            "Ready for test",
            "Closed",
            "Needs Info",
            "Rejected",
            "Postponed",
        ]
        issues_types = issues_types or []
        user_stories_statuses = user_stories_statuses or []
        tasks_statuses = tasks_statuses or []
        custom_fields = custom_fields or []

        type_ = type_.upper()
        project_name = f"{type_}_{name}"
        p = self.api.projects.create(project_name, description=description)
        for t in tasks_statuses:
            try:
                p.add_task_status(t)
            except Exception as e:
                # check if duplicated
                j.logger.debug(f"skipping task {t} {e}")

        for t in priorities:
            try:
                p.add_priority(t)
            except Exception as e:
                # check if duplicated
                j.logger.debug(f"skipping prio {t} {e}")

        for t in severities:
            try:
                p.add_severity(t)
            except Exception as e:
                # check if duplicated
                j.logger.debug(f"skipping sever {t} {e}")

        for t in issues_statuses:
            try:
                p.add_issue_status(t)
            except Exception as e:
                # check if duplicated
                j.logger.debug(f"skipping status {t} {e}")

        for t in user_stories_statuses:
            try:
                p.add_user_story_status(t)
            except Exception as e:
                # check if duplicated
                j.logger.debug(f"skipping user status {t} {e}")

        for t in issues_types:
            try:
                p.add_issue_type(t)
            except Exception as e:
                # check if duplicated
                j.logger.debug(f"skipping issue type {t} {e}")

        for t in custom_fields:
            try:
                p.add_issue_attribute(t)
                p.add_user_story_attribute(t)
            except Exception as e:
                # check if duplicated
                j.logger.debug(f"skipping custom field type {t} {e}")

        return p

    def create_new_project_circle(
        self, name, description="", **attrs,
    ):
        """Creates a new project circle.

        Args:
            name (str): circle name
            description (str, optional): circle description. Defaults to "".

        Returns:
            [ProjectCircle]: Project circle
        """

        attrs = {
            "is_backlog_activated": False,
            "is_issues_activated": True,
            "is_kanban_activated": True,
            "is_private": False,
            "is_wiki_activated": True,
        }
        issues_types = ["Bug", "Question", "Enhancement"]
        severities = ["Wishlist", "Minor", "Normal", "Important", "Critical"]
        priorities = None

        story_statuses = [
            "New",
            "to-start",
            "in-progress",
            "Blocked",
            "Implemented",
            "Verified",
            "Archived",
        ]
        item_statuses = ["New", "to-start", "in-progress", "Blocked", "Done"]
        issues_statuses = [
            "New",
            "to-start",
            "in-progress",
            "Blocked",
            "Implemented",
            "Closed",
            "Rejected",
            "Postponed",
            "Archived",
        ]

        return ProjectCircle(
            self,
            self._create_new_circle(
                name,
                type_="project",
                description=description,
                severities=severities,
                issues_statuses=issues_statuses,
                priorities=priorities,
                issues_types=issues_types,
                user_stories_statuses=story_statuses,
                tasks_statuses=item_statuses,
                **attrs,
            ),
        )

    def create_new_team_circle(self, name, description="", **attrs):
        """Creates a new team circle. using sprints & timeline (does not use kanban)

        Args:
            name (str): circle name
            description (str, optional): circle description. Defaults to "".
            severities (List[str], optional): list of strings to represent severities. Defaults to None.
            issues_statuses (List[str], optional): list of strings to represent issues_stauses. Defaults to None.
            priorities (List[str], optional): list of strings to represent priorities. Defaults to None.
            issues_types (List[str], optional): list of strings to represent issues types. Defaults to None.
            user_stories_statuses (List[str], optional): list of strings to represent user stories. Defaults to None.
            tasks_statuses (List[str], optional): list of strings to represent task statuses. Defaults to None.

        Returns:
            [TeamCircle]: team circle
        """

        attrs = {
            "is_backlog_activated": True,
            "is_issues_activated": True,
            "is_kanban_activated": False,
            "is_private": False,
            "is_wiki_activated": True,
        }
        issues_types = ["Bug", "Question", "Enhancement"]
        severities = ["Wishlist", "Minor", "Normal", "Important", "Critical"]
        priorities = None

        story_statuses = [
            "New",
            "to-start",
            "in-progress",
            "Blocked",
            "Implemented",
            "Verified",
            "Archived",
        ]
        item_statuses = ["New", "to-start", "in-progress", "Blocked", "Done"]
        issues_statuses = [
            "New",
            "to-start",
            "in-progress",
            "Blocked",
            "Implemented",
            "Closed",
            "Rejected",
            "Postponed",
            "Archived",
        ]

        return TeamCircle(
            self,
            self._create_new_circle(
                name,
                type_="team",
                description=description,
                severities=severities,
                issues_statuses=issues_statuses,
                priorities=priorities,
                issues_types=issues_types,
                user_stories_statuses=story_statuses,
                tasks_statuses=item_statuses,
                **attrs,
            ),
        )

    def create_new_funnel_circle(self, name, description="", **attrs):
        """Creates a new funnel circle. using sprints & timeline (does not use kanban)

        Args:
            name (str): circle name
            description (str, optional): circle description. Defaults to "".

        Returns:
            [FunnelCircle]: funnel circle
        """
        attrs = {
            "is_backlog_activated": False,
            "is_issues_activated": True,
            "is_kanban_activated": True,
            "is_private": False,
            "is_wiki_activated": True,
        }

        severities = ["unknown", "low", "25%", "50%", "75%", "90%"]
        priorities = ["Low", "Normal", "High"]
        issues_types = "opportunity"

        issues_statuses = [
            "New",
            "Interested",
            "Deal",
            "Blocked",
            "NeedInfo",
            "Lost",
            "Postponed",
            "Won",
        ]
        story_statuses = [
            "New",
            "Proposal",
            "Contract",
            "Blocked",
            "NeedInfo",
            "Closed",
        ]
        task_statuses = ["New", "In progress", "Verification", "Needs info", "Closed"]

        custom_fields = ["bookings", "commission"]

        return FunnelCircle(
            self,
            self._create_new_circle(
                name,
                type_="funnel",
                description=description,
                severities=severities,
                issues_statuses=issues_statuses,
                priorities=priorities,
                issues_types=issues_types,
                user_stories_statuses=story_statuses,
                tasks_statuses=task_statuses,
                custom_fields=custom_fields,
                **attrs,
            ),
        )

    def export_circles_as_md(self, wikipath="/tmp/taigawiki", modified_only=True, full_info=False):
        """export circles into {wikipath}/src/circles
        HINT: Using full_info will take longer time

        Args:
            wikipath (str, optional): wiki path. Defaults to "/tmp/taigawiki".
            full_info (bool): export object with full info. Defaults to False
        """
        path = j.sals.fs.join_paths(wikipath, "src", "circles")

        j.sals.fs.mkdirs(path)
        circles = self.list_all_active_projects(full_info=full_info)

        def write_md_for_circle(circle):
            circle_md = circle.as_md
            circle_mdpath = j.sals.fs.join_paths(path, f"{circle.clean_name}.md")
            if not (
                modified_only and j.sals.fs.exists(circle_mdpath) and j.sals.fs.read_ascii(circle_mdpath) == circle_md
            ):
                j.sals.fs.write_ascii(circle_mdpath, circle_md)

        circles_mdpath = j.sals.fs.join_paths(path, "circles.md")
        circles_mdcontent = "# circles\n\n"
        for c in circles:
            circles_mdcontent += f"- [{c.name}](./{c.clean_name}.md)\n"

        j.sals.fs.write_ascii(circles_mdpath, circles_mdcontent)

        greenlets = [gevent.spawn(write_md_for_circle, gcircle_obj) for gcircle_obj in circles]
        gevent.joinall(greenlets)

    def export_users_as_md(self, wikipath="/tmp/taigawiki", modified_only=True, full_info=False):
        """export users into {wikipath}/src/users
        HINT: Using full_info will take longer time

        Args:
            wikipath (str, optional): wiki path. Defaults to "/tmp/taigawiki".
            modified_only (bool): export moidified objects only
            full_info (bool): export object with full info. Defaults to False
        """

        path = j.sals.fs.join_paths(wikipath, "src", "users")
        j.sals.fs.mkdirs(path)
        users_objects = self.list_all_users(full_info=full_info)

        users_mdpath = j.sals.fs.join_paths(path, "users.md")
        users_mdcontent = "# users\n\n"

        def write_md_for_user(user):
            user_md = user.as_md
            user_mdpath = j.sals.fs.join_paths(path, f"{user.clean_name}.md")
            if not (modified_only and j.sals.fs.exists(user_mdpath) and j.sals.fs.read_ascii(user_mdpath) == user_md):
                j.sals.fs.write_ascii(user_mdpath, user_md)

        for u in users_objects:
            users_mdcontent += f"- [{u.username}](./{u.clean_name}.md)\n"

        j.sals.fs.write_ascii(users_mdpath, users_mdcontent)

        greenlets = [gevent.spawn(write_md_for_user, guser_obj) for guser_obj in users_objects]
        gevent.joinall(greenlets)

    def export_as_md(self, wiki_path="/tmp/taigawiki", modified_only: bool = True, full_info=False):
        """export taiga instance into a wiki  showing users and circles
        HINT: Using full_info will take longer time

        Args:
            wiki_src_path (str, optional): wiki path. Defaults to "/tmp/taigawiki".
            modified_only (bool): write modified objects only. Defaults to True
            full_info (bool): export object with full info. Defaults to False
        """
        j.logger.info("Start Exporting Wiki ...")
        gs = []
        gs.append(gevent.spawn(self.export_circles_as_md, wiki_path, modified_only, full_info))
        gs.append(gevent.spawn(self.export_users_as_md, wiki_path, modified_only, full_info))
        gevent.joinall(gs)

        template_file = j.sals.fs.join_paths(Path(__file__).parent, "template.html")
        index_html_path = j.sals.fs.join_paths(wiki_path, "src", "index.html")
        readme_md_path = j.sals.fs.join_paths(wiki_path, "src", "README.md")
        sidebar_md_path = j.sals.fs.join_paths(wiki_path, "src", "_sidebar.md")
        content = dedent(
            f"""
            # Taiga overview

            - [circles](./circles/circles.md)
            - [users](./users/users.md)
        """
        )
        j.sals.fs.write_ascii(readme_md_path, content)
        j.sals.fs.write_ascii(sidebar_md_path, content)
        j.sals.fs.copy_file(template_file, index_html_path)
        j.logger.info(f"Exported at {wiki_path}")

    def export_as_md_periodically(
        self, wiki_path="/tmp/taigawiki", period: int = 300, modified_only: bool = True, full_info=False
    ):
        """export taiga instance into a wiki  showing users and circles periodically
        HINT: Using full_info will take longer time

        Args:
            wiki_path (str, optional): wiki path. Defaults to "/tmp/taigawiki".
            period (int): Time to wait between each export in "Seconds". Defaults to 300 (5 Min).
            modified_only (bool): write modified objects only.. Defaults to True.
            full_info (bool): export object with full info. Defaults to False

        """
        repeater = Event()
        while True:
            j.logger.info("Start Exporting ....")
            self.export_as_md(wiki_path, modified_only, full_info)
            j.logger.info(f"Exported at {wiki_path}")
            repeater.wait(period)

    def export_as_yaml(self, export_dir="/tmp/export_dir", full_info=False):
        """export taiga instance [Circle, Story, Issue, Task , User] into a yaml files
        HINT: Using full_info will take longer time

        Args:
            export_dir (str, optional): [description]. Defaults to "/tmp/export_dir".
            full_info (bool): export object with full info. Defaults to False
        """

        def _export_objects_to_dir(objects_dir, objects_fun, full_info):
            j.sals.fs.mkdirs(objects_dir)
            objects = objects_fun(full_info=full_info)
            for obj in objects:
                try:
                    outpath = j.sals.fs.join_paths(objects_dir, f"{obj.id}.yaml")
                    j.sals.fs.write_ascii(outpath, obj.as_yaml)

                except Exception as e:
                    import traceback

                    traceback.print_exc()
                    j.logger.error(e)
                    j.logger.error(f"{type(obj)}: {obj.id}")

        projects_path = j.sals.fs.join_paths(export_dir, "projects")
        stories_path = j.sals.fs.join_paths(export_dir, "stories")
        issues_path = j.sals.fs.join_paths(export_dir, "issues")
        tasks_path = j.sals.fs.join_paths(export_dir, "tasks")
        # Milestones is not one of our model objects
        # milestones_path = j.sals.fs.join_paths(export_dir, "milestones")
        users_path = j.sals.fs.join_paths(export_dir, "users")

        def on_err(*args, **kwargs):
            print("err, ", args, kwargs)

        j.logger.info("Start Export as YAML")

        gs = []
        gs.append(gevent.spawn(_export_objects_to_dir, projects_path, self.list_all_active_projects, full_info))
        gs.append(gevent.spawn(_export_objects_to_dir, stories_path, self.list_all_user_stories, full_info))
        gs.append(gevent.spawn(_export_objects_to_dir, issues_path, self.list_all_issues, full_info))
        # Milestones is not one of our model objects
        # gs.append(gevent.spawn(_export_objects_to_dir, milestones_path, self.list_all_milestones)
        gs.append(gevent.spawn(_export_objects_to_dir, users_path, self.list_all_users, full_info))
        gs.append(gevent.spawn(_export_objects_to_dir, tasks_path, self.list_all_tasks, full_info))
        gevent.joinall(gs)

        j.logger.info("Finish Export as YAML")

    def import_from_yaml(self, import_dir="/tmp/export_dir"):
        """Import Circle with all stories, issues and tasks from yaml files

        Args:
            import_dir (str): import directory path. Defaults to "/tmp/export_dir".
        """
        # Helper Functions
        def check_by_name(list_obj, name_to_find):
            for obj in list_obj:
                if obj.name == name_to_find:
                    return obj.id

            return list_obj[0].id

        def import_circle(self, yaml_obj):
            circle = None
            # Funnel Circle
            if yaml_obj["basic_info"]["name"].lower() == "funnel":
                circle = self.create_new_funnel_circle(
                    yaml_obj["basic_info"]["name"], yaml_obj["basic_info"]["description"],
                )
            # Team Circle
            elif yaml_obj["basic_info"]["name"].lower() == "team":
                circle = self.create_new_team_circle(
                    yaml_obj["basic_info"]["name"], yaml_obj["basic_info"]["description"],
                )
            # Project Circle
            elif yaml_obj["basic_info"]["name"].lower() == "project":
                circle = self.create_new_project_circle(
                    yaml_obj["basic_info"]["name"], yaml_obj["basic_info"]["description"],
                )
            # Any Other Circle
            else:
                circle = self._create_new_circle(yaml_obj["basic_info"]["name"], yaml_obj["basic_info"]["description"],)
                circle.is_backlog_activated = yaml_obj["modules"]["is_backlog_activated"]
                circle.is_issues_activated = yaml_obj["modules"]["is_issues_activated"]
                circle.is_kanban_activated = yaml_obj["modules"]["is_kanban_activated"]
                circle.is_wiki_activated = yaml_obj["modules"]["is_wiki_activated"]

            circle.is_private = yaml_obj["basic_info"]["is_private"]
            circle.videoconferences = yaml_obj["modules"]["videoconferences"]
            for issue_attr in yaml_obj["issues_attributes"]:
                circle.add_issue_attribute(issue_attr)
            for us_attr in yaml_obj["stories_attributes"]:
                circle.add_user_story_attribute(us_attr)
            return circle

        def import_story(circle_object, yaml_obj):
            status_id = check_by_name(circle_object.us_statuses, yaml_obj["status"]["name"])

            story = circle_object.add_user_story(
                yaml_obj["basic_info"].get("subject"),
                tags=yaml_obj["basic_info"].get("tags"),
                description=yaml_obj["basic_info"].get("description", ""),
                client_requirement=yaml_obj["requirements"].get("client_requirement"),
                team_requirement=yaml_obj["requirements"].get("team_requirement"),
                is_blocked=yaml_obj["additional_info"].get("is_blocked"),
                due_date=yaml_obj["date"].get("due_date"),
                status=status_id,
            )

            for field in yaml_obj.get("custom_fields", []):
                for attr in circle_object.list_user_story_attributes():
                    if attr.name == field["name"]:
                        story.set_attribute(attr.id, field["value"])
                        break
            return story

        def import_issue(circle_object, yaml_obj):
            priority_id = check_by_name(circle_object.priorities, yaml_obj["priority"]["name"])
            status_id = check_by_name(circle_object.issue_statuses, yaml_obj["status"]["name"])
            type_id = check_by_name(circle_object.issue_types, yaml_obj["type"]["name"])
            severity_id = check_by_name(circle_object.severities, yaml_obj["severity"]["name"])
            issue = circle_object.add_issue(
                yaml_obj["basic_info"]["subject"],
                priority_id,
                status_id,
                type_id,
                severity_id,
                description=yaml_obj["basic_info"].get("description"),
            )

            for field in yaml_obj["custom_fields"]:
                for attr in circle_object.list_issue_attributes():
                    if attr.name == field["name"]:
                        issue.set_attribute(attr.id, field["value"])
                        break
            return issue

        def import_tasks(circle_object, story_object, yaml_obj):
            status_id = check_by_name(circle_object.task_statuses, yaml_obj["status"]["name"])
            task = story_object.add_task(
                yaml_obj["basic_info"].get("subject"),
                status_id,
                description=yaml_obj["basic_info"].get("description", ""),
                tags=yaml_obj["basic_info"].get("tags"),
            )
            return task

        # Folders Path
        projects_path = j.sals.fs.join_paths(import_dir, "projects")
        stories_path = j.sals.fs.join_paths(import_dir, "stories")
        issues_path = j.sals.fs.join_paths(import_dir, "issues")
        tasks_path = j.sals.fs.join_paths(import_dir, "tasks")

        # List of Files inside project Folder
        projects = j.sals.fs.os.listdir(projects_path)

        for project_file in projects:
            if project_file.endswith(".yaml") or project_file.endswith(".yml"):
                with open(j.sals.fs.join_paths(projects_path, project_file)) as pf:
                    circle_yaml = yaml.full_load(pf)
                    circle_obj = import_circle(self, circle_yaml)
                    j.logger.info(f"<Circle {circle_obj.id} Created>")

                    for story in circle_yaml["stories"]:
                        with open(j.sals.fs.join_paths(stories_path, f"{story}.yaml")) as sf:
                            story_yaml = yaml.full_load(sf)
                            story_obj = import_story(circle_obj, story_yaml)
                            j.logger.info(f"<Story {story_obj.id} Created in Circle {circle_obj.id}>")

                            for task in story_yaml["tasks"]:
                                with open(j.sals.fs.join_paths(tasks_path, f"{task}.yaml")) as tf:
                                    task_yaml = yaml.full_load(tf)
                                    task_obj = import_tasks(circle_obj, story_obj, task_yaml)
                                    j.logger.info(f"<Task {task_obj.id} Created in Story {story_obj.id}>")
                                    task_obj.update()
                            story_obj.update()

                    for issue in circle_yaml["issues"]:
                        with open(j.sals.fs.join_paths(issues_path, f"{issue}.yaml")) as isf:
                            issue_yaml = yaml.full_load(isf)
                            issue_obj = import_issue(circle_obj, issue_yaml)
                            j.logger.info(f"<Issue {issue_obj.id} Created in Circle {circle_obj.id}>")
                            issue_obj.update()

                    circle_obj.update()
                    j.logger.info(f"<Circle {circle_obj.id} Imported with All Stories and Issues")
