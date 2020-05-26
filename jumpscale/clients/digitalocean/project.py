from digitalocean import Droplet
from digitalocean.baseapi import BaseAPI, Error, GET, POST, DELETE, PUT


class ProjectManagement(BaseAPI):
    """Project management

    Attributes accepted at creation time:

    Args:
        name (str): project name
        description (str): project size
        purpose (str): purpose of the project
        environemnt (str): environment of the project's resources

    Attributes returned by API:
        * id (int): project id
        * owner_uuid (str): uuid of the project owner
        * owner_id (str): id of the project owner
        * name (str): project name
        * description (str): project description
        * purpose (str): project purpose
        * environment (str): environment of the project's resources
        * is_default (bool): If true, all resources will be added to this project if no project is specified.
        * created_at (str): creation date in format u'2014-11-06T10:42:09Z'
        * updated_at (str): update date in format u'2014-11-06T10:42:09Z'

    """

    def __init__(self, *args, **kwargs):
        # Defining default values
        self.id = None
        self.name = None
        self.owner_uuid = None
        self.owner_id = None
        self.description = None
        self.purpose = None
        self.environment = None
        self.is_default = False
        self.updated_at = None
        self.created_at = None

        # This will load also the values passed
        super(ProjectManagement, self).__init__(*args, **kwargs)

    @classmethod
    def get_object(cls, api_token, project_id):
        """Class method that will return a Project object by ID.

        Args:
            api_token (str): token
            project_id (int): project id
        """
        project = cls(token=api_token, id=project_id)
        project.load()
        return project

    @classmethod
    def list(cls, client):

        data = client.get_data("projects")

        projects = list()
        for jsoned in data["projects"]:
            project = cls(**jsoned)
            project.token = client.token

            projects.append(project)

        return projects

    def load(self):
        """
        Fetch data about project - use this instead of get_data()
        """
        projects = self.get_data("projects/%s" % self.id)
        project = projects["project"]

        for attr in project.keys():
            setattr(self, attr, project[attr])

        return self

    def _update_data(self, project):
        self.id = project["id"]
        self.owner_uuid = project["owner_uuid"]
        self.owner_id = project["owner_id"]
        self.name = project["name"]
        self.description = project["description"]
        self.purpose = project["purpose"]
        self.environment = project["environment"]
        self.is_default = project["is_default"]
        self.created_at = project["created_at"]
        self.updated_at = project["updated_at"]

    def create(self, *args, **kwargs):
        """
        Create the project with object properties.

        Note: Every argument and parameter given to this method will be
        assigned to the object.
        """
        for attr in kwargs.keys():
            setattr(self, attr, kwargs[attr])

        data = {
            "name": self.name,
            "description": self.description,
            "purpose": self.purpose,
            "environment": self.environment,
        }

        data = self.get_data("projects", type=POST, params=data)
        self._update_data(data["project"])

    def update(self, *args, **kwargs):
        """
        Update the project with object properties.

        Note: Every argument and parameter given to this method will be
        assigned to the object.
        """
        for attr in kwargs.keys():
            setattr(self, attr, kwargs[attr])

        data = {
            "name": self.name,
            "description": self.description,
            "purpose": self.purpose,
            "environment": self.environment,
            "is_default": self.is_default,
        }

        data = self.get_data("projects/%s" % self.id, type=PUT, params=data)
        self._update_data(data["project"])

    def delete(self):
        """
        Delete the project.
        To be deleted, a project must not have any resources assigned to it. Any existing resources must first be reassigned or destroyed.
        """
        self.get_data("projects/%s" % self.id, type=DELETE)

    def list_resources(self):
        """
        List all resources in the project
        """
        return self.get_data("projects/%s/resources" % self.id)["resources"]

    def list_droplets(self):
        """
        List all droplets in the project
        """
        resources = self.list_resources()
        droplets = []
        for resource in resources:
            if not resource["urn"].startswith("do:droplet:"):
                continue
            droplet_id = resource["urn"].replace("do:droplet:", "")
            droplet = Droplet.get_object(api_token=self.token, droplet_id=droplet_id)
            droplets.append(droplet)

        return droplets

    def assign_resources(self, resources):
        """Assign resources to the project.

        :param resources: A list of uniform resource names (URNs) to be added to a project.
        :type resources: [str]
        """
        self.get_data("projects/%s/resources" % self.id, type=POST, params={"resources": resources})

    def __str__(self):
        return "<Project: %s %s>" % (self.id, self.name)
