import dateutil
from taiga import TaigaAPI
from taiga.exceptions import TaigaRestException
from jumpscale.loader import j
from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from functools import lru_cache
from collections import defaultdict


class TaigaClient(Client):
    host = fields.String(default="https://projects.threefold.me")

    def credential_updated(self, value):
        self._api = None

    username = fields.String(on_update=credential_updated)
    password = fields.Secret(on_update=credential_updated)
    token = fields.Secret(on_update=credential_updated)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api = None

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
        for issue in issues:
            text += f"- {issue.subject} \n"
        return text

    def __get_issues_required_data(self, issues, with_description=False):
        """Get the required data from issues to be used later in export(render)

        Returns:
            List: List of issues required details to be used in export(render).
        """
        all_issues_templates = list()
        for issue in issues:
            single_project_template = dict()
            single_project_template["subject"] = issue.subject
            single_project_template["created_date"] = issue.created_date
            single_project_template["due_date"] = issue.due_date
            single_project_template["owner_name"] = issue.owner_extra_info.get("full_name_display", "unknown")
            single_project_template["owner_mail"] = issue.owner_extra_info.get("email", "unknown")
            single_project_template["project"] = issue.project_extra_info.get("name", "unknown")
            if with_description:
                single_project_template["description"] = self.get_issue_description(issue.id)
            all_issues_templates.append(single_project_template)
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

    def __get_project_required_data(self, projects):
        all_projects_template = list()
        for project in projects:
            single_project_template = dict()
            single_project_template["name"] = project.name
            single_project_template["created_date"] = project.created_date
            single_project_template["owner"] = project.owner.get("full_name_display")
            single_project_template["issues"] = project.list_issues()
            all_projects_template.append(single_project_template)
        return all_projects_template

    def __render_projects(self, text="", projects=None, with_details=False):
        for project in projects:
            text += f"##### {project.get('name')} \n"
            # Check on details flag
            issues = project.get("issues")

            if with_details:
                all_issues_templates = self.__get_issues_required_data(issues, with_description=True)
                text = self.__render_issues_with_details(text=text, issues=all_issues_templates, with_description=True)
            else:
                text = self.__render_issues_with_subjects(text=text, issues=issues)

        return text

    def export_issues_per_project(self, path="/tmp/issues_per_project.md", with_details=False):
        """Export issues per project in a markdown file
        
        Args:
            path (str): The path of exported markdown file.
            
        """
        projects = self.list_all_projects()
        text = """
### Issues  Per Project \n
"""
        # batch_size = 50
        # count = 0

        # TODO remove the 20 after applying genevent
        all_projects_template = self.__get_project_required_data(projects[:20])
        grouped_projects = self.__group_data(data=all_projects_template, grouping_attribute="owner")

        for owner, projects_per_owner in grouped_projects.items():
            text += f"## Owner: {owner} \n"
            # Sort the issues per group
            sorted_list = sorted(projects_per_owner, key=lambda x: x.get("created_date"), reverse=True)
            text = self.__render_projects(text=text, projects=sorted_list, with_details=with_details)

        j.sals.fs.write_file(path=path, data=text)

    def export_issues_per_user(self, user_name=None, path="/tmp/issues_per_user.md", with_description=False):
        """Export all the issues per specif user in a markdown file, if no user given
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
        text = f"""
### {selected_user_name} Issues \n
"""
        issues = self.list_all_issues(user_id=user_id)
        all_issues_templates = self.__get_issues_required_data(issues, with_description)
        grouped_issues = self.__group_data(data=all_issues_templates, grouping_attribute="project")

        for group, issues_per_group in grouped_issues.items():
            text += f"##### Project: {group} \n"
            # Sort the issues per group
            sorted_list = sorted(issues_per_group, key=lambda x: x.get("created_date"), reverse=True)
            text = self.__render_issues_with_details(text=text, issues=sorted_list, with_description=with_description)

        j.sals.fs.write_file(path=path, data=text)

    def __group_data(self, data, grouping_attribute="project"):
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
