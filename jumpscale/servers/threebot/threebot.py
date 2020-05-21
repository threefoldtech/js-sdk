from jumpscale.god import j

import imp
import json

from gevent.pywsgi import WSGIServer
from jumpscale.core.base import Base, fields


GEDIS = "gedis"
GEDIS_HTTP = "gedis_http"
GEDIS_HTTP_HOST = "127.0.0.1"
GEDIS_HTTP_PORT = 8000


class PackageNginxConfig:
    def __init__(self, package):
        self.package = package
        self.nginx = j.sals.nginx.get("main")

    @property
    def default_config(self):
        default_server = {
            "name": "default",
            "ports": self.package.config.get("ports"),
            "locations": []
        }

        for static_dir in self.package.static_dirs:
            default_server["locations"].append({
                "type": "static",
                "name": static_dir.get("name"),
                "spa": static_dir.get("spa"),
                "index": static_dir.get("index"),
                "path_url": j.sals.fs.join_paths(self.package.base_url, static_dir.get("path_url").lstrip("/")),
                "path_location": j.sals.fs.join_paths(self.package.path, static_dir.get("path_location"))
            })

        for bottle_server in self.package.bottle_servers:
            default_server["locations"].append({
                "type": "proxy",
                "name": bottle_server.get("name"),
                "host": bottle_server.get("host"),
                "port": bottle_server.get("port"),
                "path_url": j.sals.fs.join_paths(self.package.base_url, bottle_server.get("path_url").lstrip("/")),
                "path_dest": bottle_server.get("path_dest"),
                "websocket": bottle_server.get("websocket")
            })

        if self.package.actors_dir:
            default_server["locations"].append({
                "type": "proxy",
                "name": "actors",
                "host": GEDIS_HTTP_HOST,
                "port": GEDIS_HTTP_PORT,
                "path_url": j.sals.fs.join_paths(self.package.base_url, "actors"),
                "path_dest": self.package.base_url,
            })

        return [default_server]
    
    def apply(self):
        servers = self.default_config + self.package.config.get("servers", [])
        for server in servers:
            for port in server.get("ports", [80]):

                server_name = server.get("name")
                if server_name != "default":
                    server_name = f"{self.package.name}_{server_name}"

                website = self.nginx.get_website(server_name, port=port)
                website.ssl = server.get("ssl", port == 443)
                website.domain = server.get("domain")
                website.letsencryptemail = server.get("letsencryptemail")

                for location in server.get("locations", []):
                    loc = None

                    location_name = location.get("name")
                    location_name = f"{self.package.name}_{location_name}"
                    location_type = location.get("type", "static")

                    if location_type == "static":
                        loc = website.get_static_location(location_name)
                        loc.spa = location.get("spa", False)
                        loc.index = location.get("index", "index.html")
                        loc.path_location = location.get("path_location")
  
                    elif location_type == "proxy":
                        loc = website.get_proxy_location(location_name)
                        loc.scheme = location.get("scheme", "http")
                        loc.host = location.get("host")
                        loc.port = location.get("port")
                        loc.path_dest = location.get("path_dest", "")
                        loc.websocket = location.get("websocket", False)
                    
                    if loc:
                        loc.path_url = location.get("path_url")
                        loc.force_https = location.get("force_https")

                website.save()
                website.configure()
                self.nginx.save()


class Package:
    def __init__(self, path):
        self.path = path
        self.config = self.load_config()
        self.name = self.config["name"]
        self.nginx_config = PackageNginxConfig(self)

    def load_config(self):
        with open(j.sals.fs.join_paths(self.path, 'package.json')) as f:
            return json.load(f)

    @property
    def base_url(self):
        return j.sals.fs.join_paths("/", self.name)

    @property
    def actors_dir(self):
        actors_dir = self.config.get("actors_dir", None)
        if not actors_dir:
            if j.sals.fs.join_paths(self.path, "actors"):
                actors_dir = "actors"
        return actors_dir

    @property
    def static_dirs(self):
        return self.config.get("static_dirs", [])

    @property
    def bottle_servers(self):
        return self.config.get("bottle_servers", [])

    def get_actors(self):
        actors = []
        for file_path in j.sals.fs.walk_files(self.path + '/' + self.actors_dir, recursive=False):
            file_name =  j.sals.fs.basename(file_path)
            if file_name.endswith(".py"):
                actor_name = f"{self.name}_{file_name[:-3]}"
                actors.append(dict(name=actor_name, path=file_path))
        return actors
    
    def get_bottle_server(self, path, host, port):
        module = imp.load_source(path[:-3], path)
        return WSGIServer((host, port), module.app)
   

class PackageManager:
    def __init__(self, threebot):
        self._threebot = threebot
        self._packages = {}

    def get(self, package_name):
        return self._packages.get(package_name)

    def list_all(self):
        return self._packages.values()

    def add(self, path):
        package = Package(path=path)
        self._packages[package.name] = package

        if self._threebot.started:
            self.apply(package)

    def apply(self, package):        
        for static_dir in package.static_dirs:
            path = j.sals.fs.join_paths(package.path, static_dir["path_location"])
            if not j.sals.fs.exists(path):
                raise j.exceptions.NotFound(f"Cannot find static dir {path}")

        # add bottle servers
        for bottle_server in package.bottle_servers:
            path = j.sals.fs.join_paths(package.path, bottle_server["file_path"])
            if not j.sals.fs.exists(path):
                raise j.exceptions.NotFound(f"Cannot find bottle server path {path}")
                
            bottle_app = package.get_bottle_server(path, bottle_server["host"], bottle_server["port"])
            self._threebot.rack.add(f"{package.name}_{bottle_server['name']}", bottle_app)

        # register gedis actors
        if package.actors_dir:
            path = j.sals.fs.join_paths(package.path, package.actors_dir)
            if not j.sals.fs.exists(path):
                raise j.exceptions.NotFound(f"Cannot find actors dir {path}")

            for actor in package.get_actors():
                self._threebot.gedis._system_actor.register_actor(actor["name"], actor["path"])

        # start servers
        self._threebot.rack.start()

        # apply nginx configuration
        package.nginx_config.apply()

    def apply_all(self):
        for package in self.list_all():
            self.apply(package)

    # def delete(self, package_name):
    #     package = self._packages.get(package_name)
    #     if not package:
    #         raise j.exceptions.NotFound("package not found")
        
    #     # stop bottle server
    #     if package.has_bottle_app:
    #         self._threebot.rack.stop(package.name)
        
    #     # unregister gedis actors
    #     if package.has_actors:
    #         for actor in package.get_actors():
    #             self._threebot.gedis._system_actor.unregister_actor(actor["name"])
        
    #     # remove nginx configuration
    #     # package.website.clean()


class ThreebotServer(Base):
    def __init__(self):
        super().__init__()
        self._rack = None
        self._gedis = None
        self._db = None
        self._gedis_http = None
        self.started = False
        self.rack.add(GEDIS, self.gedis)
        self.rack.add(GEDIS_HTTP, self.gedis_http.gevent_server)
        self.packages = PackageManager(threebot=self)

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

    def start(self):
        self.rack.start()
        self.packages.apply_all()
        self.started = True

    def stop(self):
        self.rack.stop()
        self.started = False
