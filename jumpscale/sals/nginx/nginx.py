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
from jumpscale.core.exceptions import Input
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
    package_name = fields.String()
    is_package_authorized = fields.Boolean(default=False)
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
            https_port=PORTS.HTTPS,
        )

    def configure(self):
        j.sals.fs.mkdir(self.cfg_dir)
        j.sals.fs.write_file(self.cfg_file, self.get_config())


class AcmeServer(Enum):
    LETSENCRYPT = "letsencrypt"
    ZEROSSL = "zerossl"
    CUSTOM = "custom"


class Certbot(Base):
    DEFAULT_NAME = "certbot"
    DEFAULT_LOGS_DIR = j.sals.fs.join_paths(j.core.dirs.LOGDIR, DEFAULT_NAME)
    DEFAULT_CONFIG_DIR = j.sals.fs.join_paths(j.core.dirs.CFGDIR, DEFAULT_NAME)
    DEFAULT_WORK_DIR = j.sals.fs.join_paths(j.core.dirs.VARDIR, DEFAULT_NAME)

    # the following options match the certbot command arguments
    domain = fields.String(required=True)
    non_interactive = fields.Boolean(default=True)
    agree_tos = fields.Boolean(default=True)
    logs_dir = fields.String(default=DEFAULT_LOGS_DIR)
    config_dir = fields.String(default=DEFAULT_CONFIG_DIR)
    work_dir = fields.String(default=DEFAULT_WORK_DIR)

    email = fields.Email()
    server = fields.URL()
    eab_kid = fields.String()
    eab_hmac_key = fields.String()

    # for existing certificates
    key_path = fields.String()
    cert_path = fields.String()
    fullchain_path = fields.String()

    @property
    def run_cmd(self):
        args = [self.DEFAULT_NAME]

        for name, value in self.to_dict().items():
            if name.endswith("_"):
                continue

            if value:
                # append only if the field has a value
                name = name.replace("_", "-")
                args.append(f"--{name}")

                # append the value itself only if it's a boolean value
                # boolean options are set by adding name only
                if not isinstance(value, bool):
                    args.append(value)

        return args

    @property
    def install_cmd(self):
        # replace "certbot" with "certbot install"
        cmd = self.run_cmd
        cmd.insert(1, "install")
        return cmd


class NginxCertbot(Certbot):
    nginx_server_root = fields.String(required=True)
    nginx = fields.Boolean(default=True)


class LetsencryptCertbot(NginxCertbot):
    """
    default installation is for let's encrypt (manual plugin), no need for other options

    currently, we support only email
    """

    # change required value to True here
    email = fields.Email(required=True)


class ZerosslCertbot(NginxCertbot):
    SERVER_URL = "https://acme.zerossl.com/v2/DV90"
    KEY_CREDENTIALS_URL = "https://api.zerossl.com/acme/eab-credentials"
    EMAIL_CREDENTIALS_URL = "https://api.zerossl.com/acme/eab-credentials-email"

    api_key_ = fields.Secret()
    server = fields.URL(default=SERVER_URL)

    @property
    def run_cmd(self):
        # get eab_kid and eab_hmac_key based on email or api_key_
        if not self.email and not self.api_key_:
            raise Input("email or api_key_ must be provided")

        # set them to get the full run-cmd with correct arguments
        if self.api_key_:
            resp = j.tools.http.post(self.KEY_CREDENTIALS_URL, params={"access_key": self.api_key_})
        else:
            resp = j.tools.http.post(self.EMAIL_CREDENTIALS_URL, data={"email": self.email})

        resp.raise_for_status()
        data = resp.json()

        self.eab_kid = data["eab_kid"]
        self.eab_hmac_key = data["eab_hmac_key"]

        return super().run_cmd


class CustomCertbot(NginxCertbot):
    # change email and server required value to True here
    email = fields.Email(required=True)
    server = fields.URL(required=True)


class Website(Base):
    domain = fields.String()
    ssl = fields.Boolean()
    port = fields.Integer(default=PORTS.HTTP)
    locations = fields.Factory(Location, stored=False)
    includes = fields.List(fields.String())

    selfsigned = fields.Boolean(default=True)

    # keep it as letsencryptemail for compatibility
    letsencryptemail = fields.String()
    acme_server_type = fields.Enum(AcmeServer)
    acme_server_url = fields.URL()
    # in case of using existing key/certificate
    key_path = fields.String()
    cert_path = fields.String()
    fullchain_path = fields.String()

    @property
    def certbot(self):
        kwargs = dict(
            domain=self.domain,
            email=self.letsencryptemail,
            server=self.acme_server_url,
            nginx_server_root=self.parent.cfg_dir,
            key_path=self.key_path,
            cert_path=self.cert_path,
            fullchain_path=self.fullchain_path,
        )

        if self.acme_server_type == AcmeServer.LETSENCRYPT:
            certbot_type = LetsencryptCertbot
        elif self.acme_server_type == AcmeServer.ZEROSSL:
            certbot_type = ZerosslCertbot
        else:
            certbot_type = CustomCertbot

        return certbot_type(**kwargs)

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

    def generate_certificates(self, retries=6):
        if self.domain:
            if self.key_path and self.cert_path and self.fullchain_path:
                # only use install command if an existing key and certificate were set
                cmd = self.certbot.install_cmd
            else:
                cmd = self.certbot.run_cmd

            for _ in range(retries):
                rc, out, err = j.sals.process.execute(cmd)
                if rc > 0:
                    j.logger.error(f"Generating certificate failed {out}\n{err}")
                else:
                    break

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
        if self.ssl:
            self.generate_self_signed_certificates()
        if generate_certificates and self.ssl:
            self.generate_certificates()

    def clean(self):
        j.sals.fs.rmtree(self.cfg_dir)


class NginxConfig(Base):
    websites = fields.Factory(Website, stored=False)
    cert = fields.Boolean(default=True)

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
        """configures main nginx conf"""
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
