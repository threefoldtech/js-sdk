from jumpscale.loader import j

import imp
import os
import sys
import toml
import shutil
from urllib.parse import urlparse
from gevent.pywsgi import WSGIServer
from jumpscale.core.base import Base, fields
from jumpscale.sals.nginx.nginx import PORTS


GEDIS = "gedis"
GEDIS_HTTP = "gedis_http"
GEDIS_HTTP_HOST = "127.0.0.1"
GEDIS_HTTP_PORT = 8000
CHATFLOW_SERVER_HOST = "127.0.0.1"
CHATFLOW_SERVER_PORT = 8552
DEFAULT_PACKAGES = {
    "auth": os.path.dirname(j.packages.auth.__file__),
    "chatflows": os.path.dirname(j.packages.chatflows.__file__),
    "admin": os.path.dirname(j.packages.admin.__file__),
    "admin_old": os.path.dirname(j.packages.admin_old.__file__),
    "weblibs": os.path.dirname(j.packages.weblibs.__file__),
    "tfgrid_solutions": os.path.dirname(j.packages.tfgrid_solutions.__file__),
}
DOWNLOADED_PACKAGES_PATH = j.sals.fs.join_paths(j.core.dirs.VARDIR, "downloaded_packages")


class NginxPackageConfig:
    def __init__(self, package):
        self.package = package
        self.nginx = j.sals.nginx.get("main")

    @property
    def default_config(self):
        default_server = {
            "name": "default",
            "ports": self.package.config.get("ports"),
            "locations": [],
            "domain": self.package.default_domain,
            "letsencryptemail": self.package.default_email,
        }

        for static_dir in self.package.static_dirs:
            default_server["locations"].append(
                {
                    "type": "static",
                    "name": static_dir.get("name"),
                    "spa": static_dir.get("spa"),
                    "index": static_dir.get("index"),
                    "path_url": j.sals.fs.join_paths(self.package.base_url, static_dir.get("path_url").lstrip("/")),
                    "path_location": self.package.resolve_staticdir_location(static_dir),
                    "is_auth": static_dir.get("is_auth", False),
                    "is_admin": static_dir.get("is_admin", False),
                }
            )

        for bottle_server in self.package.bottle_servers:
            default_server["locations"].append(
                {
                    "type": "proxy",
                    "name": bottle_server.get("name"),
                    "host": bottle_server.get("host"),
                    "port": bottle_server.get("port"),
                    "path_url": j.sals.fs.join_paths(self.package.base_url, bottle_server.get("path_url").lstrip("/")),
                    "path_dest": bottle_server.get("path_dest"),
                    "websocket": bottle_server.get("websocket"),
                    "is_auth": bottle_server.get("is_auth", False),
                    "is_admin": bottle_server.get("is_admin", False),
                }
            )

        if self.package.actors_dir:
            default_server["locations"].append(
                {
                    "type": "proxy",
                    "name": "actors",
                    "host": GEDIS_HTTP_HOST,
                    "port": GEDIS_HTTP_PORT,
                    "path_url": j.sals.fs.join_paths(self.package.base_url, "actors"),
                    "path_dest": self.package.base_url,
                }
            )

        if self.package.chats_dir:
            default_server["locations"].append(
                {
                    "type": "proxy",
                    "name": "chats",
                    "host": CHATFLOW_SERVER_HOST,
                    "port": CHATFLOW_SERVER_PORT,
                    "path_url": j.sals.fs.join_paths(self.package.base_url, "chats"),
                    "path_dest": self.package.base_url + "/chats",  # TODO: temperoary fix for auth package
                }
            )

        return [default_server]

    def apply(self):
        default_ports = [PORTS.HTTP, PORTS.HTTPS]
        servers = self.default_config + self.package.config.get("servers", [])
        for server in servers:
            ports = server.get("ports", default_ports) or default_ports
            for port in ports:
                server_name = server.get("name")
                if server_name != "default":
                    server_name = f"{self.package.name}_{server_name}"

                website = self.nginx.get_website(server_name, port=port)
                website.ssl = server.get("ssl", port == PORTS.HTTPS)
                website.includes = server.get("includes", [])
                website.domain = server.get("domain", self.default_config[0].get("domain"))
                website.letsencryptemail = server.get(
                    "letsencryptemail", self.default_config[0].get("letsencryptemail")
                )

                for location in server.get("locations", []):
                    loc = None

                    location_name = location.get("name")
                    location_name = f"{self.package.name}_{location_name}"
                    location_type = location.get("type", "static")

                    if location_type == "static":
                        loc = website.get_static_location(location_name)
                        loc.spa = location.get("spa", False)
                        loc.index = location.get("index")
                        loc.path_location = location.get("path_location")

                    elif location_type == "proxy":
                        loc = website.get_proxy_location(location_name)
                        loc.scheme = location.get("scheme", "http")
                        loc.host = location.get("host")
                        loc.port = location.get("port", PORTS.HTTP)
                        loc.path_dest = location.get("path_dest", "")
                        loc.websocket = location.get("websocket", False)
                    
                    elif location_type == "custom":
                        loc = website.get_custom_location(location_name)
                        loc.custom_config = location.get("custom_config")

                    if loc:
                        path_url = location.get("path_url", "/")
                        if not path_url.endswith("/"):
                            path_url += "/"

                        loc.path_url = path_url
                        loc.force_https = location.get("force_https")
                        loc.is_auth = location.get("is_auth", False)
                        loc.is_admin = location.get("is_admin", False)

                website.save()
                website.configure()
                self.nginx.save()


class StripPathMiddleware(object):
    """
    a middle ware for bottle apps to strip slashes
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, e, h):
        e["PATH_INFO"] = e["PATH_INFO"].rstrip("/")
        return self.app(e, h)


class Package:
    def __init__(self, path, default_domain, default_email):
        self.path = path
        self.config = self.load_config()
        self.name = self.config["name"]
        self.nginx_config = NginxPackageConfig(self)
        self._module = None
        self.default_domain = default_domain
        self.default_email = default_email

    def load_config(self):
        return toml.load(j.sals.fs.join_paths(self.path, "package.toml"))

    @property
    def module(self):
        if self._module is None:
            package_file_path = j.sals.fs.join_paths(self.path, "package.py")
            if j.sals.fs.exists(package_file_path):
                module = imp.load_source(self.name, package_file_path)
                if not hasattr(module, self.name):
                    raise j.exceptions.Halt(f"missing class ({self.name}) in the package file")

                self._module = getattr(module, self.name)()
        return self._module

    @property
    def base_url(self):
        return j.sals.fs.join_paths("/", self.name)

    @property
    def actors_dir(self):
        actors_dir = j.sals.fs.join_paths(self.path, self.config.get("actors_dir", "actors"))
        if j.sals.fs.exists(actors_dir):
            return actors_dir

    @property
    def chats_dir(self):
        chats_dir = j.sals.fs.join_paths(self.path, self.config.get("chats_dir", "chats"))
        if j.sals.fs.exists(chats_dir):
            return chats_dir

    @property
    def static_dirs(self):
        return self.config.get("static_dirs", [])

    @property
    def bottle_servers(self):
        return self.config.get("bottle_servers", [])

    @property
    def actors(self):
        for file_path in j.sals.fs.walk_files(self.actors_dir, recursive=False):
            file_name = j.sals.fs.basename(file_path)
            if file_name.endswith(".py"):
                actor_name = f"{self.name}_{file_name[:-3]}"
                yield dict(name=actor_name, path=file_path)

    def resolve_staticdir_location(self, static_dir):
        """Resolves path for static location in case we need it
        absoulute or not

        static_dir.absolute_path true it will return the path directly
        if false will be relative to the path

        Args:
            static_dir (str): package.toml static dirs category

        Returns:
            str: package path
        """
        path_location = static_dir.get("path_location")
        absolute_path = static_dir.get("absolute_path", False)
        if absolute_path:
            return j.sals.fs.expanduser(path_location)
        return j.sals.fs.expanduser(j.sals.fs.join_paths(self.path, path_location))

    def get_bottle_server(self, file_path, host, port):
        module = imp.load_source(file_path[:-3], file_path)
        return WSGIServer((host, port), StripPathMiddleware(module.app))

    def install(self):
        if self.module and hasattr(self.module, "install"):
            self.module.install()

    def uninstall(self):
        if self.module and hasattr(self.module, "uninstall"):
            self.module.uninstall()

    def start(self):
        if self.module and hasattr(self.module, "start"):
            self.module.start()

    def stop(self):
        if self.module and hasattr(self.module, "stop"):
            self.module.stop()

    def restart(self):
        if self.module:
            self.module.stop()
            self.module.start()


class PackageManager(Base):
    packages = fields.Typed(dict, default=DEFAULT_PACKAGES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._threebot = None

    @property
    def threebot(self):
        if self._threebot is None:
            self._threebot = j.servers.threebot.get()
        return self._threebot

    def get(self, package_name):
        package_path = self.packages.get(package_name)
        if package_path:
            return Package(path=package_path, default_domain=self.threebot.domain, default_email=self.threebot.email)

    def get_packages(self):
        packages = []
        for package_name, package_path in self.packages.items():
            packages.append(
                {
                    "name": package_name,
                    "path": package_path,
                    "system_package": package_name in DEFAULT_PACKAGES.keys()
                }
            ) 
        return packages

    def list_all(self):
        return self.packages.keys()

    def add(self, path: str = None, giturl: str = None):
        # TODO: Check if package already exists

        if not any([path, giturl]) or all([path, giturl]):
            raise j.exceptions.Value("either path or giturl is required")

        if giturl:
            url = urlparse(giturl)
            url_parts = url.path.lstrip("/").split("/", 4)

            if len(url_parts) != 5:
                raise j.exceptions.Value("invalid path")

            org, repo, _, branch, package_path = url_parts
            repo_dir = f"{org}_{repo}_{branch}"
            repo_path = j.sals.fs.join_paths(DOWNLOADED_PACKAGES_PATH, repo_dir)
            repo_url = f"{url.scheme}://{url.hostname}/{org}/{repo}"

            # delete repo dir if exists
            j.sals.fs.rmtree(repo_path)

            j.tools.git.clone_repo(url=repo_url, dest=repo_path, branch_or_tag=branch)
            path = j.sals.fs.join_paths(repo_path, repo, package_path)

        package = Package(path=path, default_domain=self.threebot.domain, default_email=self.threebot.email)
        self.packages[package.name] = package.path

        # execute package install method
        package.install()

        # install package if threebot is started
        if self.threebot.started:
            self.install(package)
            self.threebot.nginx.reload()

        self.save()

        # Return updated package info to actor (now we have path only)
        return {"name": package.name, "path": package.path}

    def delete(self, package_name):
        if package_name in DEFAULT_PACKAGES:
            raise j.exceptions.Value("cannot delete default packages")

        package = self.get(package_name)
        if not package:
            raise j.exceptions.NotFound(f"{package_name} package not found")

        # remove bottle servers
        for bottle_server in package.bottle_servers:
            self.threebot.rack.remove(f"{package.name}_{bottle_server['name']}")

        if self.threebot.started:
            # unregister gedis actors
            if package.actors_dir:
                for actor in package.actors:
                    self.threebot.gedis._system_actor.unregister_actor(actor["name"])

            # unload chats
            if package.chats_dir:
                self.threebot.chatbot.unload(package.chats_dir)

            # reload nginx
            self.threebot.nginx.reload()

        # execute package uninstall method
        package.uninstall()

        self.packages.pop(package_name)
        self.save()

    def install(self, package):
        """install and apply package configrations

        Args:
            package ([package object]): get package object using [self.get(package_name)]

        Returns:
            [dict]: [package info]
        """
        sys.path.append(package.path + "/../")  # TODO to be changed
        package.install()
        for static_dir in package.static_dirs:
            path = package.resolve_staticdir_location(static_dir)
            if not j.sals.fs.exists(path):
                raise j.exceptions.NotFound(f"Cannot find static dir {path}")

        # add bottle servers
        for bottle_server in package.bottle_servers:
            path = j.sals.fs.join_paths(package.path, bottle_server["file_path"])
            if not j.sals.fs.exists(path):
                raise j.exceptions.NotFound(f"Cannot find bottle server path {path}")

            bottle_app = package.get_bottle_server(path, bottle_server["host"], bottle_server["port"])
            self.threebot.rack.add(f"{package.name}_{bottle_server['name']}", bottle_app)

        # register gedis actors
        if package.actors_dir:
            for actor in package.actors:
                self.threebot.gedis._system_actor.register_actor(actor["name"], actor["path"])

        # add chatflows actors
        if package.chats_dir:
            self.threebot.chatbot.load(package.chats_dir)

        # start servers
        self.threebot.rack.start()

        # apply nginx configuration
        package.nginx_config.apply()

        # execute package start method
        package.start()

    def _install_all(self):
        """Install and apply all the packages configurations
        This method shall not be called directly from the shell, 
        it must be called only from the code on the running Gedis server
        """
        for package in self.list_all():
            if package not in DEFAULT_PACKAGES:
                j.logger.info(f"Configuring package {package}")
                self.install(self.get(package))


class ThreebotServer(Base):
    _package_manager = fields.Factory(PackageManager)
    domain = fields.String()
    email = fields.String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rack = None
        self._gedis = None
        self._db = None
        self._gedis_http = None
        self._chatbot = None
        self._packages = None
        self._started = False
        self._nginx = None
        self._redis = None
        self.rack.add(GEDIS, self.gedis)
        self.rack.add(GEDIS_HTTP, self.gedis_http.gevent_server)

    def is_running(self):
        nginx_running = self.nginx.is_running()
        redis_running = self.redis.cmd.is_running()
        gedis_running = j.sals.nettools.wait_connection_test("127.0.0.1", 16000, timeout=1)
        return nginx_running and redis_running and gedis_running

    @property
    def started(self):
        return self._started

    @property
    def nginx(self):
        if self._nginx is None:
            self._nginx = j.tools.nginx.get("default")
        return self._nginx

    @property
    def redis(self):
        if self._redis is None:
            self._redis = j.tools.redis.get("default")
        return self._redis

    @property
    def db(self):
        if self._db is None:
            self._db = j.core.db
        return self._db

    @property
    def rack(self):
        if self._rack is None:
            self._rack = j.servers.rack
        return self._rack

    @property
    def gedis(self):
        if self._gedis is None:
            self._gedis = j.servers.gedis.get("threebot")
        return self._gedis

    @property
    def gedis_http(self):
        if self._gedis_http is None:
            self._gedis_http = j.servers.gedis_http.get("threebot")
        return self._gedis_http

    @property
    def chatbot(self):
        if self._chatbot is None:
            self._chatbot = self.gedis._loaded_actors.get("chatflows_chatbot")
        return self._chatbot

    @property
    def packages(self):
        if self._packages is None:
            self._packages = self._package_manager.get(self.instance_name)
        return self._packages

    def check_dependencies(self):
        install_msg = "Visit https://github.com/threefoldtech/js-sdk/blob/development/docs/wiki/quick_start.md for installation guide"

        if not self.nginx.installed:
            raise j.exceptions.NotFound(f"nginx is not installed.\n{install_msg}")

        ret = shutil.which("certbot")
        if not ret:
            raise j.exceptions.NotFound(f"certbot is not installed.\n{install_msg}")

        rc, out, err = j.sals.process.execute("certbot plugins")
        if "* nginx" not in out:
            raise j.exceptions.NotFound(f"python-certbot-nginx is not installed.\n{install_msg}")

        if not self.redis.installed:
            raise j.exceptions.NotFound(f"redis is not installed.\n{install_msg}")

        ret = shutil.which("tmux")
        if not ret:
            raise j.exceptions.NotFound(f"tmux is not installed.\n{install_msg}")

        ret = shutil.which("git")
        if not ret:
            raise j.exceptions.NotFound(f"git is not installed.\n{install_msg}")

    def start(self, wait: bool = False):
        # start default servers in the rack

        # mark app as started
        if self.is_running():
            return

        self.check_dependencies()

        self.redis.start()
        self.nginx.start()
        self.rack.start()
        j.application.start(f"threebot_{self.instance_name}")

        # add default packages
        for package_name in DEFAULT_PACKAGES:
            j.logger.info(f"Configuring package {package_name}")
            try:
                package = self.packages.get(package_name)
                self.packages.install(package)
            except Exception as e:
                self.stop()
                raise j.core.exceptions.Runtime(f"Error happened during getting or installing {package.name} package, the detailed error is {str(e)}")


        # install all package
        self.packages._install_all()
        j.logger.info("Reloading nginx")
        self.nginx.reload()

        # mark server as started
        self._started = True
        j.logger.info("Starting rack")
        self.rack.start(wait=wait)  # to keep the server running

    def stop(self):
        self.rack.stop()
        self.nginx.stop()
        self.redis.stop()
        self._started = False
        # mark app as stopped
        j.application.stop()
