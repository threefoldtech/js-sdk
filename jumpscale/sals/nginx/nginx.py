"""
#  Get nginx sal instance as an abstract parent for the websites and locations and for the nginx conf

nginx = j.sals.nginx.get("instance")

#  Add a webiste to the configuration

website = nginx.websites.new("website")

# Configure instance

website.port =  #  Port to listen to will use 80 by default or 443 if ssl is true

webiste.ssl = True  #  If true will generate and configure the SSL certificates

website.domain =  #  domain of the webiste

website.letsencryptemail =  #  Email to receive let's encrypt notifications

# Add locations to the webiste

loc = website.locations.new("location")

loc.path_url =  #  location path
loc.is_auth =  #  IF True will authenticate when accessing this location
loc.force_https =  #  If True won't allow http access
loc.path_location = #  alias for the location
loc.index = #  index of the location
loc.ipaddr_dest = #  Destination address for proxy pass
loc.port_dest = #  Destination port for proxy pass
loc.path_dest = #  Destination path for proxy pass
loc.location_type =  # static,spa,proxy type of location config
loc.scheme = #  https or https

#  Configuring the website and all its locations and generating the certificates

website.configure()
"""

from jumpscale.god import j
from jumpscale.core.base import Base, fields
from .location import Location
from .utils import render_config_template, DIR_PATH


class Website(Base):

    port = fields.Integer(default=80)
    ssl = fields.Boolean()
    domain = fields.String()
    path = fields.String()
    locations = fields.Factory(Location)
    letsencryptemail = fields.String()

    @property
    def path_cfg_dir(self):
        return f"{self.parent.path_cfg_dir}/servers"

    @property
    def path_cfg(self):
        return f"{self.path_cfg_dir}/{self.instance_name}.http.conf"

    @property
    def path_web(self):
        return self.parent.path_web

    def generate_certificates(self):
        """Generate ssl certificate if ssl is enabled
        """
        if self.ssl:
            j.sals.process.execute(
                f"certbot --nginx -d {self.domain} --non-interactive --agree-tos -m {self.letsencryptemail} --nginx-server-root {self.parent.path_cfg_dir}"
            )

    def configure(self, generate_certificates=True):
        """Writes configuration of the website and its locations

        Args:
            generate_certificates (bool, optional): Will generate certificates if true. Defaults to True.
        """

        j.sals.fs.mkdir(self.path_cfg_dir)
        config = render_config_template("website", base_dir=j.core.dirs.BASEDIR, website=self)
        j.sals.fs.write_file(self.path_cfg, config)

        for location_name in self.locations.list_all():
            location = self.locations.get(location_name)
            location.configure()

        if generate_certificates:
            self.generate_certificates()


class NginxConfig(Base):
    websites = fields.Factory(Website)

    def __init__(self):
        super().__init__()
        self._cmd = None
        self._path_web = None
        self._path_cfg_dir = None
        self._logs_dir = None

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
            self._logs_dir = j.sals.fs.join_paths(j.core.dirs.LOGDIR, "nginx", self.instance_name)
            j.sals.fs.mkdirs(self._logs_dir)
        return self._logs_dir

    def configure(self):
        """configures main nginx conf
        """
        # clean old websites config
        self.cleanup()
        configtext = j.tools.jinja2.render_template(
            template_path=j.sals.fs.join_paths(DIR_PATH, "templates", "nginx.conf"), logs_dir=self.logs_dir,
        )
        j.sals.fs.write_file(self.path_cfg, configtext)

        j.sals.fs.copy_tree(f"{DIR_PATH}/resources/", self.path_cfg_dir)

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

    def cleanup(self):
        j.sals.fs.rmtree(f"{self.path_cfg_dir}/servers")
