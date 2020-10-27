from jumpscale.loader import j
from enum import Enum
from jumpscale.core.base import Base, fields
from .location import Location
from .utils import render_config_template, DIR_PATH


class Status(Enum):
    INIT = "init"
    INSTALLED = "installed"


class Website(Base):

    port = fields.Integer(default=80)
    ssl = fields.Boolean()
    domain = fields.String()
    path = fields.String()
    locations = fields.Factory(Location)

    @property
    def path_cfg_dir(self):
        return f"{self.parent.path_cfg_dir}/servers"

    @property
    def path_cfg(self):
        return f"{self.path_cfg_dir}/{self.instance_name}.http.conf"

    @property
    def path_web(self):
        return self.parent.path_web

    def configure(self):
        """Writes configuration of the website and its locations
        """

        j.sals.fs.mkdir(self.path_cfg_dir)
        config = render_config_template("website", base_dir=j.core.dirs.BASEDIR, website=self)
        j.sals.fs.write_file(self.path_cfg, config)

        for location_name in self.locations.list_all():
            location = self.locations.get(location_name)
            location.configure()


class OpenRestyServer(Base):
    status = fields.Enum(Status)
    websites = fields.Factory(Website)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cmd = None
        self._path_web = None
        self._path_cfg_dir = None
        self._logs_dir = None

        self.executor = "tmux"  # only tmux for now

    @property
    def path_web(self):
        if not self._path_web:
            self._path_web = j.sals.fs.join_paths(j.core.dirs.VARDIR, "web", self.instance_name)
            j.sals.fs.mkdirs(j.sals.fs.join_paths(self._path_web, "static"))
        return self._path_web

    @property
    def path_cfg_dir(self):
        if not self._path_cfg_dir:
            self._path_cfg_dir = j.sals.fs.join_paths(j.core.dirs.CFGDIR, "nginx", self.instance_name)
            j.sals.fs.mkdirs(self._path_cfg_dir)
        return self._path_cfg_dir

    @property
    def path_cfg(self):
        return j.sals.fs.join_paths(self.path_cfg_dir, "nginx.conf")

    @property
    def logs_dir(self):
        if not self._logs_dir:
            self._logs_dir = j.sals.fs.join_paths(j.core.dirs.LOGDIR, "openresty", self.instance_name)
            j.sals.fs.mkdirs(self._logs_dir)
        return self._logs_dir

    def configure(self):
        # clean old websites config
        self.cleanup()
        """configures main nginx conf
        """
        # self.install() This is commented for now until the repo and necessary deps are handled
        configtext = j.tools.jinja2.render_template(
            template_path=j.sals.fs.join_paths(DIR_PATH, "templates", "nginx.conf"), logs_dir=self.logs_dir,
        )
        j.sals.fs.write_file(self.path_cfg, configtext)

    def get_from_port(self, port, domain=None, ssl=None):
        """will try to get a website listening on port, if it doesn't exist it will create one

        Args:
            port (int): port to search for
            domain (str, optional): domain. Defaults to None.
            ssl (bool, optional): Will set ssl if True. Defaults to None.

        Returns:
            Website: A new or an old website instance with the needed port
        """
        website_name = f"{self.instance_name}_website_{port}"

        website = self.websites.find(website_name)
        if website:
            return website

        website = self.websites.get(website_name)
        ssl = ssl or port == 443  # Use ssl if port is 443 if ssl in not specified

        website.domain = domain
        website.port = port
        website.ssl = ssl

        return website

    def install(self, reset=False):
        """Install required deps for openresty

        Args:
            reset (bool, optional): If true will redo the installation. Defaults to False.
        """
        if reset or self.status == "init":
            # get weblib
            weblibs_path = j.tools.git.ensure_repo(
                "https://github.com/threefoldtech/js-weblibs"  # Place holder repo might be changed
            )

            # copy the templates to the right location
            j.sals.fs.copy_tree(f"{DIR_PATH}/web_resources/", self.path_cfg_dir)

            j.sals.fs.symlink(
                f"{weblibs_path}/static", f"{self.path_web}/static/weblibs", overwrite=True,
            )
            self.status = Status.INSTALLED

            self.save()

    @property
    def startup_cmd(self):
        pass

    def start(self, reset=False):
        pass

    def stop(self):
        pass

    def is_running(self):
        pass

    def reload(self):
        self.configure()
        j.sals.process.execute("lapis build", cwd=self.path_cfg_dir)

    def cleanup(self):
        j.sals.fs.rmtree(f"{self.path_cfg_dir}/servers")
