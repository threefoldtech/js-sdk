import dateutil
from taiga import TaigaAPI
from taiga.exceptions import TaigaRestException
from jumpscale.loader import j
from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from functools import lru_cache


class TaigaClient(Client):
    host = fields.String(default="https://projects.threefold.me")
    username = fields.String()
    password = fields.Secret()
    token = fields.Secret()

    def __init__(self, **kwargs):
        super().__init__()
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
