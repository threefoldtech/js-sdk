"""This client is used to interact with Taiga API.
## Initialization

Using username and  password:
> client = j.clients.taiga.new('test', host="https://staging.circles.threefold.me/", username='7mada', password='123456')

OR using a token
> client = j.clients.taiga.new('test', host="https://staging.circles.threefold.me/", token='extra secret token string')

## Listing

### Listing issues

To get the issues of the user with id 123:
> client.list_all_issues(123)
To get the issues of all users:
> client.list_all_issues(123)

### Listing projects

To list all projects:
> client.list_all_projects()

### Listing milestones

To list all projects:
> client.list_all_milestones()

### Listing user stories

To list the user stories of the user with id 123:
> client.list_all_user_stories(123)
To list the user stories of all users:
> client.list_all_user_stories()

## Exporting

### Exporting issues
To export all issues details to the file /tmp/issues.md:
> client.export_all_issues_details('/tmp/issues.md')
it accepts the parameter with_description upon which is decided whether to print the description with the issues or not

### Exporting issues per project
To export all issues details grouped by the project to the file /tmp/issues.md:
> client.export_issues_per_project('/tmp/issues.md')
It accepts with_details to tell whether to print only the issue title or its full details

### Exporting issues for a user
To export all issues details for the username 7mada to the file /tmp/issues.md:
> client.export_issues_per_user(username='7mada', '/tmp/issues.md')
Accepts with_description

### Exporting user stories
To export all user stories to the file /tmp/stories.md:
> client.export_all_user_stories(username='7mada', '/tmp/stories.md')

## Fetching data

### Fetching user circles
> client.fetch_user_circles('7mada')

### Fetching project issues
> client.fetch_circles_issues(123) # project id

### Fetching user stories
> client.get_user_stories('7mada')

### Fetching user tasks
> client.get_user_tasks('7mada')

### Fetch issue description
> client.get_issue_description(567) # issue id

## Operations

### Move a story to a porject
> client.move_story_to_cirlce(789, 123) # story id, project id

"""
import dateutil
from taiga import TaigaAPI
from taiga.exceptions import TaigaRestException
from jumpscale.loader import j
from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from functools import lru_cache
from collections import defaultdict
import gevent


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

    @lru_cache(maxsize=128)
    def _get_project(self, project_id):
        return self.api.projects.get(project_id)

    @lru_cache(maxsize=128)
    def _get_milestone(self, milestone_id):
        if milestone_id:
            return self.api.milestones.get(milestone_id)

    @lru_cache(maxsize=128)
    def _get_priority(self, priority_id):
        return self.api.priorities.get(priority_id)

    @lru_cache(maxsize=128)
    def _get_assignee(self, assignee_id):
        if assignee_id:
            return self.api.users.get(assignee_id)

    @lru_cache(maxsize=128)
    def _get_issue_status(self, status_id):
        return self.api.issue_statuses.get(status_id)

    @lru_cache(maxsize=128)
    def _get_user_stories_status(self, status_id):
        return self.api.user_story_statuses.get(status_id)

    @lru_cache(maxsize=128)
    def _get_task_status(self, status_id):
        return self.api.task_statuses.get(status_id)

    @lru_cache(maxsize=128)
    def _get_user_id(self, username):
        user = self.api.users.list(username=username)
        if user:
            user = user[0]
            return user.id
        else:
            raise j.exceptions.Input("Couldn't find user with username: {}".format(username))

    def get_user_circles(self, username):
        """Get circles owner by user

        Args:
            username (str): Name of the user
        """
        user_id = self._get_user_id(username)
        circles = self.api.projects.list(member=user_id)
        user_circles = []
        for circle in circles:
            if circle.owner["id"] == user_id:
                user_circles.append(circle)
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
            user_story.project = self._get_project(user_story.project)
            user_story.milestone = self._get_milestone(user_story.milestone)
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
            user_task.project = self._get_project(user_task.project)
            user_task.milestone = self._get_milestone(user_task.milestone)
            user_task.status = self._get_task_status(user_task.status)
            user_tasks.append(user_task)

        return user_tasks

    def move_story_to_cirlce(self, story_id, project_id):
        """Moves a story to another circle/project

        Args:
            story_id (int): User story id
            project_id (int): circle/project id

        Raises:
            j.exceptions.NotFound: No user story with speicifed id found
            j.exceptions.NotFound: No project with speicifed id found
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
            raise j.exceptions.NotFound("Couldn't find user story with id: {}".format(story_id))

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
            raise j.exceptions.NotFound("No project with id: {} found".format(project_id))
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
            raise j.exceptions.Runtime("Failed to migrate story error was: {}".format(str(e)))

        self.api.user_stories.delete(story_id)
        return migrate_story.id

    def list_all_issues(self, user_id=""):
        """
        List all issues for specific user if you didn't pass user_id will list all the issues

        Args:
            user_id (int): id of the user.

        Returns:
            List: List of taiga.models.models.Issue.
        """
        return self.api.issues.list(assigned_to=user_id)

    def list_all_projects(self):
        """
        List all projects

        Returns:
            List: List of taiga.models.models.Project.
        """
        return self.api.projects.list()

    def list_all_milestones(self):
        """
        List all milestones

        Returns:
            List: List of taiga.models.models.Milestone.
        """
        return self.api.milestones.list()

    def list_all_user_stories(self, user_id=""):
        """
        List all user stories for specific user if you didn't pass user_id will list all the available user stories

        Args:
            user_id (int): id of the user.

        Returns:
            List: List of taiga.models.models.UserStory.
        """
        return self.api.user_stories.list(assigned_to=user_id)

    def __render_issues_with_details(self, text="Issues", issues=None, with_description=False):
        """Get issues details and append them to text to be written in markdown files

        Args:
            text (str): the text that the method will append to it.
            issues (List): list of all issues that we will get the subject from .

        Returns:
            str: string contains the issues details to be used in markdown.
        """
        for issue in issues:
            text += f"- **Subject:** {issue.get('subject','unknown')} \n"
            text += f"  - **Created Date:** {issue.get('created_date','unknown')} \n"
            text += f"  - **Due Date:** {issue.get('due_date','unknown')} \n"
            text += f"  - **Owner Name:** {issue.get('owner_name','unknown')} \n"
            text += f"  - **Owner Email:** {issue.get('owner_mail','unknown')} \n"
            # text += f"  - **Project:** {issue.get('project','unknown')} \n"
            if with_description:
                text += f"  - **Description:** \n```\n{issue.get('description','unknown')}\n``` \n"
        return text

    def __render_issues_with_subjects(self, text="", issues=None):
        """Render issues with subject only to be written to markdown file

        Args:
            text (str): this is text that we will append to it the issus subjects
            issues (list): list of issues

        Returns:
            text(str): the rendered text to be written to markdown file

        """
        for issue in issues:
            text += f"- {issue.subject} \n"
        return text

    def _get_single_issue_required_data(self, issue, with_description=False):
        single_project_template = dict()
        single_project_template["subject"] = issue.subject
        single_project_template["created_date"] = issue.created_date
        single_project_template["due_date"] = issue.due_date
        single_project_template["owner_name"] = issue.owner_extra_info.get("full_name_display", "unknown")
        single_project_template["owner_mail"] = issue.owner_extra_info.get("email", "unknown")
        single_project_template["project"] = issue.project_extra_info.get("name", "unknown")
        if with_description:
            single_project_template["description"] = self.get_issue_description(issue.id)
        return single_project_template

    def __get_issues_required_data(self, issues, with_description=False):
        """Get the required data from issues to be used later in export(render)

        Returns:
            List: List of issues required details to be used in export(render).
        """
        greenlets = [gevent.spawn(self._get_single_issue_required_data, issue, with_description) for issue in issues]
        gevent.joinall(greenlets)
        all_issues_templates = [greenlet.value for greenlet in greenlets if greenlet.successful()]
        return all_issues_templates

    def export_all_issues_details(self, path="/tmp/issues_details.md", with_description=False):
        """Export all the issues subjects in a markdown file

        Args:
            path (str): The path of exported markdown file.

        """
        text = f"""
### Issues \n
"""
        issues = self.list_all_issues()
        all_issues_templates = self.__get_issues_required_data(issues, with_description)

        text = self.__render_issues_with_details(
            text=text, issues=all_issues_templates, with_description=with_description
        )

        j.sals.fs.write_file(path=path, data=text)

    def __get_single_project_required_data(self, project):
        single_project_template = dict()
        single_project_template["name"] = project.name
        single_project_template["created_date"] = project.created_date
        single_project_template["owner"] = project.owner.get("full_name_display")
        single_project_template["issues"] = project.list_issues()
        return single_project_template

    def __get_project_required_data(self, projects):
        """Get the required data from the projects
        Args:
            projects(list): list of projects

        Returns:
            all_projects_template (dic): dict of the data required from project object

        """
        greenlets = [gevent.spawn(self.__get_single_project_required_data, project) for project in projects]
        gevent.joinall(greenlets)
        all_projects_template = [
            greenlet.value for greenlet in greenlets if greenlet.successful()
        ]  # Filtering out the failed ones
        return all_projects_template

    def __render_projects(self, text="", projects=None, with_details=False):
        """Do all the render for project details that will written in markdown files.

        Args:
            text(str): the text will be used to append data to it.
            projects (list): list of projects will be used in render
            with_details (bool): flag used to get the issue details in case of true.

        Returns:
            text (str): the rendered text that will be writted to markdown file.
        """
        for project in projects:
            text += f"##### {project.get('name')} \n"
            issues = project.get("issues")

            if with_details:
                all_issues_templates = self.__get_issues_required_data(issues, with_description=True)
                text = self.__render_issues_with_details(text=text, issues=all_issues_templates, with_description=True)
            else:
                text = self.__render_issues_with_subjects(text=text, issues=issues)

        return text

    def map_render_issues_per_project(self, with_details):
        """Map the desired data from issues per project and render them to be used in markdown files.

        Args:
            with_details (bool): flag used to get the issue details in case of true.
        """
        projects = self.list_all_projects()
        all_projects_template = self.__get_project_required_data(projects)
        grouped_projects = self.__group_data(data=all_projects_template, grouping_attribute="owner")

        for owner, projects_per_owner in grouped_projects.items():
            self.text += f"## Owner: {owner} \n"
            # Sort the issues per group
            sorted_list = sorted(projects_per_owner, key=lambda x: x.get("created_date"), reverse=True)
            self.text = self.__render_projects(text=self.text, projects=sorted_list, with_details=with_details)

    def export_issues_per_project(self, path="/tmp/issues_per_project.md", with_details=False):
        """Export issues per project in a markdown file

        Args:
            path (str): The path of exported markdown file.

        """
        self.text = """
### Issues  Per Project \n
"""

        self.map_render_issues_per_project(with_details)
        j.sals.fs.write_file(path=path, data=self.text)

    def map_render_issues_per_user(self, user_id, with_description):
        """Map the desired data from issues per user and render them to be used in markdown files.

        Args:
            user_id (int): the id of the used that we will use to get his issues
            with_description (bool): flag used to get the issue description in case of true.
        """
        issues = self.list_all_issues(user_id=user_id)
        all_issues_templates = self.__get_issues_required_data(issues, with_description)
        grouped_issues = self.__group_data(data=all_issues_templates, grouping_attribute="project")

        for group, issues_per_group in grouped_issues.items():
            self.text += f"##### Project: {group} \n"
            # Sort the issues per group
            sorted_list = sorted(issues_per_group, key=lambda x: x.get("created_date"), reverse=True)
            self.text = self.__render_issues_with_details(
                text=self.text, issues=sorted_list, with_description=with_description
            )

    def export_issues_per_user(self, user_name=None, path="/tmp/issues_per_user.md", with_description=False):
        """Export all the issues per specific user in a markdown file, if no user given
        the method export issues for the current logged in user

        Args:
            path (str): The path of exported markdown file.
            user_name (str): The name of the user we want to get his issues.

        """
        if user_name:
            selected_user_name = user_name
        else:
            selected_user_name = self.username
        user_id = self._get_user_id(selected_user_name)
        self.text = f"""
### {selected_user_name} Issues \n
"""
        self.map_render_issues_per_user(user_id, with_description)

        j.sals.fs.write_file(path=path, data=self.text)

    def __group_data(self, data, grouping_attribute="project"):
        """Get similar objects together with same specific attribute.

        Args:
            data(list): list of data to be grouped
            grouping_attribute (str): the property used to group the data together

        Returns:
            grouped_data(defaultdict) : dict of list containing the data which are similar grouped together
        """
        grouped_data = defaultdict(list)
        for obj in data:
            grouped_data[obj.get(grouping_attribute)].append(obj)
        return grouped_data

    def __get_stories_required_data(self):
        """Get the required data from user stories to be used later in export(render)

        Returns:
            List: List of stories required details to be used in export(render).
        """
        all_stories_template = list()
        users_stories = self.list_all_user_stories()
        for story in users_stories:
            single_story_template = dict()
            single_story_template["subject"] = story.subject
            if story.assigned_to_extra_info:
                single_story_template["assigned"] = story.assigned_to_extra_info.get("full_name_display", "unassigned")
                single_story_template["is_active"] = story.assigned_to_extra_info.get("is_active", "unknown")
            tasks = list()
            for task in story.list_tasks():
                tasks.append(task.subject)
            single_story_template["tasks"] = tasks
            all_stories_template.append(single_story_template)
        return all_stories_template

    def export_all_user_stories(self, path="/tmp/all_stories.md"):
        """Export all the user stories in a markdown file

        Args:
            path (str): The path of exported markdown file.

        """
        text = f"""
### All User Stories \n
"""
        all_stories_template = self.__get_stories_required_data()

        for story in all_stories_template:
            text += f"#### {story.get('subject')} \n"
            text += f"- **Assigned to:** {story.get('assigned','unassigned')} \n"
            text += f"- **Is Active:** {story.get('is_active','unknown')} \n"
            text += f"- **Tasks** \n"
            for task_subject in story.get("tasks"):
                text += f"  - {task_subject} \n"

        j.sals.fs.write_file(path=path, data=text)

    def get_issue_description(self, issue_id):
        """Get issue description
        Args:
            issue_id: the id of the desired issue

        Returns:
            str: issue description
        """
        return self.api.issues.get(issue_id).description
