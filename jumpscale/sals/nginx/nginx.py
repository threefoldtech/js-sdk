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

from enum import Enum

from jumpscale.core.base import Base, fields
from jumpscale.loader import j

from .utils import DIR_PATH, render_config_template


class PORTS:
    HTTP = 80
    HTTPS = 443

    @classmethod
    def init_default_ports(cls, local=False):
        if local:
            for port in range(8080, 8180):
                if not j.sals.process.is_port_listening(port):
                    cls.HTTP = port
                    break
            else:
                j.exception.Runtime("Could not find free port to listen on")
            for port in range(8443, 8500):
                if not j.sals.process.is_port_listening(port):
                    cls.HTTPS = port
                    break
            else:
                j.exception.Runtime("Could not find free port to listen on")


class ProxyBuffering(Enum):
    UNSET = ""
    ON = "on"
    OFF = "off"


class LocationType(Enum):
    STATIC = "static"
    PROXY = "proxy"
    CUSTOM = "custom"


class Location(Base):
    path_url = fields.String(default="/")
    force_https = fields.Boolean(default=False)
    path_location = fields.String(default="/")
    index = fields.String(default="index.html")

    scheme = fields.String(default="http")
    host = fields.String(default="127.0.0.1")
    port = fields.Integer()
    path_dest = fields.String(default="/")
    spa = fields.Boolean(default=False)
    websocket = fields.Boolean(default=False)
    location_type = fields.Enum(LocationType)
    is_auth = fields.Boolean(default=False)
    is_admin = fields.Boolean(default=False)
    custom_config = fields.String(default=None)
    proxy_buffering = fields.Enum(ProxyBuffering)
    proxy_buffers = fields.String()
    proxy_buffer_size = fields.String()

    @property
    def cfg_dir(self):
        return j.sals.fs.join_paths(self.parent.cfg_dir, "locations")

    @property
    def cfg_file(self):
        return j.sals.fs.join_paths(self.cfg_dir, f"{self.instance_name}.conf")

    def get_config(self):
        return render_config_template(
            "location",
            base_dir=j.core.dirs.BASEDIR,
            location=self,
            threebot_connect=j.core.config.get_config().get("threebot_connect", True),
            https_port=PORTS.HTTPS
        )

    def configure(self):
        j.sals.fs.mkdir(self.cfg_dir)
        j.sals.fs.write_file(self.cfg_file, self.get_config())


class Website(Base):
    domain = fields.String()
    ssl = fields.Boolean()
    port = fields.Integer(default=PORTS.HTTP)
    locations = fields.Factory(Location)
    includes = fields.List(fields.String())
    letsencryptemail = fields.String()
    selfsigned = fields.Boolean(default=True)

    @property
    def cfg_dir(self):
        return j.sals.fs.join_paths(self.parent.cfg_dir, self.instance_name)

    @property
    def cfg_file(self):
        return j.sals.fs.join_paths(self.cfg_dir, "server.conf")

    @property
    def include_paths(self):
        paths = []
        for include in self.includes:
            ## TODO validate location name and include
            website_name, location_name = include.split(".", 1)
            website = self.parent.websites.find(website_name)
            if not website:
                continue

            paths.append(j.sals.fs.join_paths(website.cfg_dir, "locations", location_name))
        return paths

    def get_locations(self):
        for location in self.locations.list_all():
            yield self.locations.get(location)

    def get_proxy_location(self, name):
        location = self.locations.get(name)
        location.location_type = LocationType.PROXY
        return location

    def get_custom_location(self, name):
        location = self.locations.get(name)
        location.location_type = LocationType.CUSTOM
        return location

    def get_static_location(self, name):
        location = self.locations.get(name)
        location.location_type = LocationType.STATIC
        return location

    def get_config(self):
        return render_config_template("website", base_dir=j.core.dirs.BASEDIR, website=self)

    def generate_certificates(self):
        if self.domain:
            rc, out, err = j.sals.process.execute(
                f"certbot --nginx -d {self.domain} "
                f"--non-interactive --agree-tos -m {self.letsencryptemail} "
                f"--nginx-server-root {self.parent.cfg_dir} "
                f"--logs-dir {j.core.dirs.LOGDIR}/certbot "
                f"--config-dir {j.core.dirs.CFGDIR}/certbot "
                f"--work-dir {j.core.dirs.VARDIR}/certbot "
            )
            if rc > 0:
                j.logger.error(f"Generating certificate failed {out}\n{err}")

    def generate_self_signed_certificates(self):
        keypempath = f"{self.parent.cfg_dir}/key.pem"
        certpempath = f"{self.parent.cfg_dir}/cert.pem"
        if j.sals.process.is_installed("mkcert"):
            res = j.sals.process.execute(
                f"mkcert -key-file {keypempath} -cert-file {certpempath} localhost *.localhost 127.0.0.1 ::1"
            )
            if res[0] != 0:
                raise j.exceptions.JSException(f"Failed to generate self-signed certificate (using mkcert).{res}")

        else:
            if j.sals.fs.exists(f"{keypempath}") and j.sals.fs.exists(f"{certpempath}"):
                return
            res = j.sals.process.execute(
                f"openssl req -nodes -x509 -newkey rsa:4096 -keyout {keypempath} -out {certpempath} -days 365 -subj '/CN=localhost'"
            )
            if res[0] != 0:
                raise j.exceptions.JSException(f"Failed to generate self-signed certificate (using openssl).{res}")

    def configure(self, generate_certificates=True):
        j.sals.fs.mkdir(self.cfg_dir)
        needed_dirs = ("body", "client-body", "fastcgi", "proxy", "scgi", "uwsgi")
        for d in needed_dirs:
            j.sals.fs.mkdir(j.sals.fs.join_paths(self.cfg_dir, d))
        for location in self.get_locations():
            location.configure()

        j.sals.fs.write_file(self.cfg_file, self.get_config())

        if generate_certificates and self.ssl:
            self.generate_self_signed_certificates()
            self.generate_certificates()

    def clean(self):
        j.sals.fs.rmtree(self.cfg_dir)


class NginxConfig(Base):
    websites = fields.Factory(Website)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cmd = None
        self._path_web = None
        self._cfg_dir = None
        self._logs_dir = None

    @property
    def cfg_dir(self):
        if not self._cfg_dir:
            self._cfg_dir = j.sals.fs.join_paths(j.core.dirs.CFGDIR, "nginx", self.instance_name)
            j.sals.fs.mkdirs(self._cfg_dir)
        return self._cfg_dir

    @property
    def cfg_file(self):
        return j.sals.fs.join_paths(self.cfg_dir, "nginx.conf")

    @property
    def logs_dir(self):
        if not self._logs_dir:
            self._logs_dir = j.sals.fs.join_paths(j.core.dirs.LOGDIR, "nginx", self.instance_name)
            j.sals.fs.mkdirs(self._logs_dir)
        return self._logs_dir

    def configure(self):
        """configures main nginx conf
        """
        self.clean()
        j.sals.fs.mkdir(self.cfg_dir)
        user = j.sals.unix.get_current_pwd()
        group = j.sals.unix.get_current_grp()
        def_index_dir = j.sals.fs.join_paths(DIR_PATH, "static")

        configtext = j.tools.jinja2.render_template(
            template_path=j.sals.fs.join_paths(DIR_PATH, "templates", "nginx.conf"),
            logs_dir=self.logs_dir,
            cfg_dir=self.cfg_dir,
            user=user,
            group=group,
            def_index_dir=def_index_dir,
        )

        j.sals.fs.write_file(self.cfg_file, configtext)
        j.sals.fs.copy_tree(f"{DIR_PATH}/resources/", self.cfg_dir)

    def get_website(self, name: str, port: int = 0):
        port = port or PORTS.HTTP
        website_name = f"{name}_{port}"
        website = self.websites.find(website_name)
        if website:
            return website

        website = self.websites.get(website_name)
        website.port = port
        website.ssl = port in [443, 8443]
        return website

    def clean(self):
        j.sals.fs.rmtree(f"{self.cfg_dir}")
