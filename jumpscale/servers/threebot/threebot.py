from jumpscale.god import j

import imp
import json

from gevent.pywsgi import WSGIServer
from jumpscale.core.base import Base, fields


GEDIS = "gedis"
GEDIS_HTTP = "gedis_http"
GEDIS_HTTP_HOST = "127.0.0.1"
GEDIS_HTTP_PORT = 8000
CHATFLOW_SERVER_HOST = "127.0.0.1"
CHATFLOW_SERVER_PORT = 8552

DEFAULT_PACKAGES = {
    "chatflows": "/sandbox/code/github/js-next/js-ng/jumpscale/packages/chatflows"
}


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

        if self.package.chats_dir:
            default_server["locations"].append({
                "type": "proxy",
                "name": "chats",
                "host": CHATFLOW_SERVER_HOST,
                "port": CHATFLOW_SERVER_PORT,
                "path_url": j.sals.fs.join_paths(self.package.base_url, "chats"),
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
                        loc.index = location.get("index")
                        loc.path_location = location.get("path_location")
  
                    elif location_type == "proxy":
                        loc = website.get_proxy_location(location_name)
                        loc.scheme = location.get("scheme", "http")
                        loc.host = location.get("host")
                        loc.port = location.get("port")
                        loc.path_dest = location.get("path_dest", "")
                        loc.websocket = location.get("websocket", False)
                    
                    if loc:
                        path_url = location.get("path_url", "/")
                        if not path_url.endswith("/"):
                            path_url += "/"
                        
                        loc.path_url = path_url
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
            file_name =  j.sals.fs.basename(file_path)
            if file_name.endswith(".py"):
                actor_name = f"{self.name}_{file_name[:-3]}"
                yield dict(name=actor_name, path=file_path)

    def get_bottle_server(self, file_path, host, port):
        module = imp.load_source(file_path[:-3], file_path)
        return WSGIServer((host, port), module.app)
   

class PackageManager:
    def __init__(self, threebot):
        self._threebot = threebot
        self._packages = {}

    def get(self, package_name):
        return self._packages.get(package_name)

    def list_all(self):
        return self._packages.keys()

    def add(self, path):
        package = Package(path=path)
        self._packages[package.name] = package

        if self._threebot.started:
            self.apply(package)
        
        return package

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
            for actor in package.actors:
                self._threebot.gedis._system_actor.register_actor(actor["name"], actor["path"])

        # add chatflows actors
        if package.chats_dir:
            self._threebot.chatbot.load(package.chats_dir)

        # start servers
        self._threebot.rack.start()

        # apply nginx configuration
        package.nginx_config.apply()


    def apply_all(self):
        for package in self.list_all():
            if package not in DEFAULT_PACKAGES:
                self.apply(self.get(package))


class ThreebotServer(Base):
    def __init__(self):
        super().__init__()
        self._rack = None
        self._gedis = None
        self._db = None
        self._gedis_http = None
        self._chatbot = None
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

    @property
    def chatbot(self):
        if self._chatbot is None:
            self._chatbot = self.gedis._loaded_actors.get('chatflows_chatbot')
        return self._chatbot

    def list_chatflows(self):
        return list(self.chatflows.keys())

    def start(self):
        # start all server in the rack
        self.rack.start()
        
        # add default packages
        for package_name, package_path in DEFAULT_PACKAGES.items():
            if not self.packages.get(package_name):
                package = self.packages.add(package_path)
                self.packages.apply(package)
        
        # apply all package
        self.packages.apply_all()

        # mark server as started
        self.started = True

    def stop(self):
        self.rack.stop()
        self.started = False
