"""This module is used to manage your digital ocean account, create droplet,list all the droplets, destroy droplets, create project, list all the projects and delete project
# prerequisites
## Sshkey client and loaded with you public key
'''python
ssh = j.clients.sshkey.get(name= "test")
ssh.private_key_path = "/home/rafy/.ssh/id_rsa"
ssh.load_from_file_system()
'''
## Create Digital Ocean client and set your token and load your sshkey
```python
dg = j.clients.digitalocean.get("testDG")
dg.token = ""
```
## Set sshclient you have created
``` python
dg.set_default_sshkey(ssh)
```
## Use Digital Ocean client

### Create and deploy Project to Digital Ocean

#### Create Project (name must not contian spaces or start with number)
``` python
 project = dg.projects.new("test_DG_client")
```
#### Set the name you want to deploy with on Digital Ocean
``` python
project.set_digital_ocean_name("test project DO client")
```
#### Deploy the project (you have to specific the purpose)
``` python
project.deploy(purpose="testing digital ocean client")
```
#### Deploy the project as default one so the new droplets will be automatically added to your default project
``` python
project.deploy(purpose="testing digital ocean client",is_default=True) 
```
#### Delete the project from Digital Ocean
``` python
project.delete_remote()
```

### Create and deploy Droplet to Digital Ocean

#### Create Droplet (name must not contian spaces or start with number)
``` python
droplet = dg.droplets.new("test_droplet_dg")
```
#### Set the name you want to deploy with on Digital Ocean
``` python
droplet.set_digital_ocean_name("droplet-test-DO")
```
#### Deploy the Droplet
The droplet will be deployed to you your default project
```python
droplet.deploy()
```
You can specify the project that you want the deploy the droplet to 
```python
droplet.deploy(project_name="test project DO client")
```
#### Delete the Droplet from Digital Ocean
```python
droplet.delete_remote()
```

### Get digital ocean regions
```python
dg.regions
```

### Get digital ocean images
```python
dg.images
```

In the below examples, I have supposed that you followed the above steps
and you got digital ocean client with the name (dg)
"""

from jumpscale.loader import j
from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.core.base import StoredFactory
from .project import ProjectManagement
import digitalocean


class ProjectFactory(StoredFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def list_remote(self):
        """
        Returns list of projects on Digital Ocean

        e.g
            dg.projects.list_remote()  -> list of projects

        Returns
            list(projects): list of projects on digital ocean

        """
        return ProjectManagement.list(self.parent_instance.client)

    def check_project_exist_remote(self, name):
        """
        Check a project with specific name exits on Digital Ocean

        e.g
            dg.projects.check_project_exist_remote("codescalers")  -> True
            dg.projects.check_project_exist_remote("dsrfjsdfjl")  -> False

        Args
            name (str): name of the project

        Returns
            bool : True if the project exits and False if the project does not exist on digital ocean
        """
        for project in self.list_remote():
            if project.name == name:
                return True
        return False

    def get_project_exist_remote(self, name):
        """
        Get a project with specifc name from  Digital Ocean.

        e.g
            dg.projects.get_project_exist_remote("codescalers")  -> project

        Args
            name (str): name of the project

        Returns
            Project : a project from digital ocean with the name specified
        """
        for project in self.list_remote():
            if project.name == name:
                return project
        raise j.exceptions.Input("could not find project with name:%s on your Digital Ocean account" % name)


class Project(Client):
    do_name = fields.String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_digital_ocean_name(self, name):
        """Set a name for your project to be used on Digital Ocean
        e.g
            project.set_digital_ocean_name("test project DO client")

        Args:
            name (str): name to be used on digital ocean
        """
        self.do_name = name

    def get_digital_ocean_name(self):
        """Get a name for the project which is used on digital ocean
        e.g
            project.get_digital_ocean_name()  ->  "test project DO client"

        Returns:
            str: name for the project which is used on digital ocean
        """
        return self.do_name

    def deploy(self, purpose, description="", environment="", is_default=False):
        """Create a digital ocean project
        e.g
            project.deploy(purpose="testing digital ocean client")  -> project
        Args:
            purpose(str): purpose of the project (not optional)
            description(str): description of the project, defaults to ""
            environment(str): environment of project's resources, defaults to ""
            is_default(bool): make this the default project for your user

        Returns:
            project: The project object that has been created
        """

        if self.parent.projects.check_project_exist_remote(self.do_name):
            raise j.exceptions.Value("A project with the same name already exists")

        project = ProjectManagement(
            token=self.parent.projects.parent_instance.token,
            name=self.do_name,
            purpose=purpose,
            description=description,
            environment=environment,
            is_default=is_default,
        )
        project.create()

        if is_default:
            project.update(is_default=True)

        return project

    def delete_remote(self):
        """Delete the project from Digital Ocean (A project can't be deleted unless it has no resources.)

        e.g
            project.delete_remote()
        """
        project = self.parent.projects.get_project_exist_remote(self.do_name)
        project.delete()


class DropletFactory(StoredFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def list_remote(self, project_name=None):
        """
        List all remote droplet or list droplets for a project if it is specified

        e.g
            dg.droplets.list_remote()  -> list of droplets
            dg.droplets.list_remote("codescalers")  -> list of droplets on codescalers project

        Args:
            project_name (str) : name of project on digital ocean (optional)

        Returns
            list (Droplet) : list of droplets on digital ocean


        """
        if project_name:
            project = self.parent_instance.projects.get_project_exist_remote(project_name)
            return project.list_droplets()

        return self.parent_instance.client.get_all_droplets()

    def check_droplet_exist_remote(self, name):
        """
        Check droplet exists on digital ocean

        e.g
            dg.droplets.check_droplet_exist_remote("3git")  -> True
            dg.droplets.check_droplet_exist_remote("sdfgdfed")  -> False

        Args:
            name (str) : name of droplet

        Returns
            bool : True if the droplet exist or False if the droplet does not exist
        """
        for droplet in self.list_remote():
            if droplet.name.lower() == name.lower():
                return True
        return False

    def get_droplet_exist_remote(self, name):
        """
        Get Droplet exists from Digital Ocean

        e.g
            dg.droplets.get_droplet_exist_remote("3git")

        Args:
            name (str) : name of droplet

        Returns
            droplet : droplet with the name specified

        """
        for droplet in self.list_remote():
            if droplet.name.lower() == name.lower():
                return droplet
        raise j.exceptions.Input("could not find droplet with name:%s on your Digital Ocean account" % name)

    def shutdown_all(self, project_name=None):
        """
        Shutdown all the droplets or droplets in specific project

        e.g
            dg.droplets.shutdown_all("codescalers")
            dg.droplets.shutdown_all()

        Args:
            name (str) : name of the project

        """
        for droplet in self.list_remote(project_name):
            droplet.shutdown()

    def delete_all(self, ignore=None, interactive=True, project_name=None):
        """
        Delete all the droplets or delete all the droplets in specific project

        e.g
            dg.droplets.delete_all(project_name = "codescalers")
            dg.droplets.delete_all()

        Args:
            project_name (str) : name of the project
            ignore (list): list of ignored droplets to prevent their deletion
            interactive (bool): if True the deletion will be interactive and
                                confirm if you want to delete but if False it
                                will delete directly
        """
        if not ignore:
            ignore = []

        def test(ignore, name):
            if name.startswith("TF-"):
                return False
            for item in ignore:
                if name.lower().find(item.lower()) != -1:
                    return False
            return True

        todo = []
        for droplet in self.list_remote(project_name):
            if test(ignore, droplet.name):
                todo.append(droplet)
        if todo != []:
            todotxt = ",".join([i.name for i in todo])
            if not interactive or j.tools.console.ask_yes_no("ok to delete:%s" % todotxt):
                for droplet in todo:
                    droplet.destroy()


class Droplet(Client):
    do_name = fields.String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_digital_ocean_name(self, name):
        """Set a name for your Droplet to be used on Digital Ocean

        e.g
            droplet.set_digital_ocean_name("test-name")

        Args:
            name (str): name to be used on digital ocean
        """
        self.do_name = name

    def get_digital_ocean_name(self):
        """Get a name for the Droplet which is used on digital ocean

        e.g
            droplet.get_digital_ocean_name()  ->  "test-name"

        Returns
            str: name for the droplet which is used on digital ocean
        """
        return self.do_name

    def deploy(
        self,
        sshkey=None,
        region="Amsterdam 3",
        image="ubuntu 18.04",
        size_slug="s-1vcpu-2gb",
        delete=True,
        project_name=None,
    ):
        """
        Deploy your Droplet to Digital Ocean

        Args
            sshkey (string): sshkey name used on digital ocean (if not set it will use the default one which already loaded)
            region (string): region name to deploy to
            image (string): Image name to be used
            size_slug (string): size of the droplet  (s-1vcpu-2gb,s-6vcpu-16gb,gd-8vcpu-32gb)
            delete (bool): delete the droplet if it is already deployed on digital ocean
            project_name (string): project to add this droplet it. If not specified the default project will be used.

        """
        project = None
        if project_name:
            project = self.parent.projects.get_project_exist_remote(project_name)
            if not project:
                raise j.exceptions.Input("could not find project with name:%s" % project_name)

        # Get ssh
        if not sshkey:
            sshkey_do = self.parent.get_default_sshkey()
            if not sshkey_do:
                # means we did not find the sshkey on digital ocean yet, need to create
                sshkey = self.parent.sshkey

                key = digitalocean.SSHKey(
                    token=self.parent.projects.parent_instance.token, name=sshkey.name, public_key=sshkey.public_key
                )
                key.create()
                sshkey_do = self.parent.get_default_sshkey()
            assert sshkey_do
            sshkey = sshkey_do.name

        if self.parent.droplets.check_droplet_exist_remote(self.do_name):
            dr0 = self.parent.droplets.get_droplet_exist_remote(self.do_name)
            if delete:
                dr0.destroy()
            else:
                sshcl = j.clients.sshclient.get(name="do_%s" % self.do_name, host=dr0.ip_address, sshkey=sshkey)
                return dr0, sshcl

        sshkey = self.parent.droplets.parent_instance.get_sshkey(sshkey)
        region = self.parent.droplets.parent_instance.get_region(region)
        imagedo = self.parent.droplets.parent_instance.get_image(image)

        img_slug_or_id = imagedo.slug if imagedo.slug else imagedo.id

        droplet = digitalocean.Droplet(
            token=self.parent.droplets.parent_instance.token,
            name=self.do_name,
            region=region.slug,
            image=img_slug_or_id,
            size_slug=size_slug,
            ssh_keys=[sshkey],
            backups=False,
        )
        droplet.create()

        if project:
            project.assign_resources(["do:droplet:%s" % droplet.id])

    def delete_remote(self):
        """Delete Droplet from digital ocean

        e.g
            droplet.delete_remote()

        """
        droplet = self.parent.droplets.get_droplet_exist_remote(self.do_name)
        droplet.destroy()


class DigitalOcean(Client):
    name = fields.String()
    token = fields.Secret()
    projects = fields.Factory(Project, factory_type=ProjectFactory)
    droplets = fields.Factory(Droplet, factory_type=DropletFactory)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client = None

    @property
    def client(self):
        """Return a new client if it is not set or it will return the already existed one

        e.g
            dg.client  -> <Manager>
        Returns
            Manager: client form digital ocean manager
        """

        if not self._client:
            self._client = digitalocean.Manager(token=self.token)
        return self._client

    # Images
    @property
    def images(self):
        """Return a list of digital ocean availabe images

        e.g
            dg.images  -> [<Image: 31354013 CentOS 6.9 x32>,
                                         <Image: 34902021 CentOS 6.9 x64>,...]

        Returns
            List : list of images on digital ocean available
        """
        return self.client.get_distro_images()

    @property
    def myimages(self):
        """Return a list of digital ocean images, you have created

        e.g
            dg.myimages  -> [<Image: 48614453 Unknown Zero_OS>,
                                        <Image: 50898718 Ubuntu JumpScale>,...]

        Returns
            List : list of images on digital ocean, you have created
        """
        return self.client.get_images(private=True)

    @property
    def account_images(self):
        """Return a list of digital ocean images and the images you have created

        e.g
            dg.account_images  -> [<Image: 31354013 CentOS 6.9 x32>,
                                             <Image: 34902021 CentOS 6.9 x64>,...]

        Returns
            List : list of images on digital ocean images and the images you have created
        """

        return self.images + self.myimages

    def get_image(self, name):
        """Return an image

        e.g
            dg.get_image(name="CentOS")  -> <Image: 31354013 CentOS 6.9 x32>

        Args
            name (str): name of the  required image
        Returns
            Image : list of images on digital ocean images and the images you have created
        """
        for item in self.account_images:
            if item.description:
                name_do1 = item.description.lower()
            else:
                name_do1 = ""
            name_do2 = item.distribution + " " + item.name
            print(f" - {name_do1}--{name_do2}")
            if name_do1.lower().find(name.lower()) != -1 or name_do2.lower().find(name.lower()) != -1:
                return item
        raise j.exceptions.Base("did not find image:%s" % name)

    def get_image_names(self, name=""):
        """ Return all the image  or images with a specified name
         e.g
            dg.get_image_names()  -> ['centos 6.9 x32 20180130', 'centos 6.9 x64 20180602',...]
            dg.get_image_names("centos") -> ['centos 6.9 x32 20180130', 'centos 6.9 x64 20180602']

        Args
            name (str): name of the  required image
        Returns
            Image : list of images
        """
        res = []
        name = name.lower()
        for item in self.images:
            if item.description:
                name_do = item.description.lower()
            else:
                name_do = item.distribution + " " + item.name
            if name_do.find(name) != -1:
                res.append(name_do)
        return res

    # Size

    @property
    def sizes(self):
        """Return a list sizes available on digital ocean

        e.g
            dg.sizes -> [s-1vcpu-1gb, 512mb, s-1vcpu-2gb, 1gb, s-3vcpu-1gb,.....]

        Returns
            List : list of sizes
        """
        return self.client.get_all_sizes()

    # Regions

    @property
    def regions(self):
        """Return a list regions available on digital ocean

        e.g
            dg.regions  -> [<Region: nyc1 New York 1>, <Region: sgp1 Singapore 1>,...]

        Returns
            List : list of regions
        """
        return self.client.get_all_regions()

    @property
    def region_names(self):
        """Returns Digital Ocean regions

        e.g
            dg.region_names  -> ['nyc1', 'sgp1', 'lon1', 'nyc3', 'ams3', 'fra1', 'tor1', 'sfo2', 'blr1']

        Returns
            list : list of digital ocean regions
        """
        return [i.slug for i in self.regions]

    def get_region(self, name):
        """
        Returns specific region

        e.g
            dg.get_region(name = 'nyc1')  -> <Region: nyc1 New York 1>

        Args
            name (str) : name of the required region
        Returns
            Region : the region with the name specified
        """
        for item in self.regions:
            if name == item.slug:
                return item
            if name == item.name:
                return item
        raise j.exceptions.Base("did not find region:%s" % name)

    # SSHkeys
    @property
    def sshkeys(self):
        """
        Return list of sshkeys on digital ocean

        e.g
            dg.sshkeys  -> [<SSHKey: 25882170 3bot_container_sandbox>,
                             <SSHKey: 27130645 Geert-root>,...]

        Returns
            list : list of sshkeys
        """

        return self.client.get_all_sshkeys()

    def get_default_sshkey(self):
        """
        Return sshkey you have added to your Digital Ocean client

        e.g
            dg.get_default_sshkey()  ->  <SSHKey: 25589987 rafy@rafy-Inspiron-3576>

        Returns
            list : list of sshkeys
        """
        pubkeyonly = self.sshkey.public_key
        for item in self.sshkeys:
            if item.public_key.find(pubkeyonly) != -1:
                return item
        return None

    def set_default_sshkey(self, default_sshkey):
        """
        Set sshkey you  Digital Ocean client

        e.g
            dg.set_default_sshkey(ssh)  ->  <SSHKey: 25589987 rafy@rafy-Inspiron-3576>

        Args
            default_sshkey (SSHKeyClient) : sshkey client you have created
        """
        self.sshkey = default_sshkey

    def get_sshkey(self, name):
        """
        get sshkey from  Digital Ocean

        e.g
            dg.get_sshkey("rafy@rafy-Inspiron-3576")   ->  <SSHKey: 25589987 rafy@rafy-Inspiron-3576>

        Args
            name (string) : sshkey name

        Returns
            SSHKey : return the specified sshkey
        """
        for item in self.sshkeys:
            if name == item.name:
                return item
        raise j.exceptions.Base("did not find key:%s" % name)

    def __str__(self):
        return "digital ocean client:%s" % self.name

    __repr__ = __str__
