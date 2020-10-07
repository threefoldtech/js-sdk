from jumpscale.loader import j
from unittest import TestCase
from time import time
from jumpscale.sals.nginx.nginx import LocationType
import requests
import os
from subprocess import Popen
import math
from jumpscale.sals.nginx.nginx import PORTS

HOST = "127.0.0.1"
NGINX_CONFIG_FILE = "nginx.conf"


def wait_connection_lost_test(url, timeout):
    start_time = time()
    while time() - start_time <= timeout:
        if not j.sals.nettools.wait_http_test(url, math.ceil(time() - start_time)):
            return True
    return False


def request_content(url, verify=False):
    return requests.get(url, verify=verify).content.decode()


class HTTPServer:
    def __init__(self):
        self.process = None

    def run(self, port=9090):
        devnull = open(os.devnull, "wb")
        self.process = Popen(["python", "-m", "http.server", str(port)], stdout=devnull, stderr=devnull)

    def stop(self):
        if self.process is None:
            raise RuntimeError("The server is not running.")
        self.process.terminate()
        self.process = None


class TestNginxSal(TestCase):
    def setUp(self):
        self.nginx_conf = j.sals.nginx.get("testing")
        self.config_base_dir = self.nginx_conf.cfg_dir
        self.config_file = self.nginx_conf.cfg_file
        self.logs_dir = self.nginx_conf._cfg_dir
        self.nginx_server = j.tools.nginx.get("testing_server", server_name="testing")

    def test01_basic(self):
        """ # Test case for server initialization with default config
        Test scenario:
        1. Start and then stop an Nginx server with default config.
        """

        http_link = f"http://{HOST}:8999"

        j.logger.info("Configuring the nginx server")
        self.nginx_conf.configure()
        j.logger.info("Starting the nginx server")
        self.nginx_server.start()
        j.logger.info("Checking the config is stored and the server is started")
        self.assertTrue(j.sals.fs.is_file(j.sals.fs.join_paths(self.config_base_dir, NGINX_CONFIG_FILE)))
        self.assertTrue(j.sals.nettools.wait_http_test(http_link, 5))
        self.assertTrue(request_content(http_link).find("Welcome to 3Bot") != -1)
        j.logger.info("Cleaning up the config and stoping the server")
        self.nginx_server.stop()
        self.nginx_conf.clean()

        j.logger.info("Checking the server is stopped")
        self.assertFalse(j.sals.fs.is_file(j.sals.fs.join_paths(self.config_base_dir, NGINX_CONFIG_FILE)))
        self.assertTrue(wait_connection_lost_test(http_link, 5))

    def test02_static_location(self):
        """ # Test case for serving a static location
        Test scenario:
        1. Start nginx.
        2. Add a location serving a static website with two pages.
        3. Check they're served.
        """
        static_website = self.nginx_conf.get_website("http_website")
        pwd = j.sals.fs.cwd()
        static_location = static_website.locations.get(
            "static",
            path_url="/hey",
            path_location=j.sals.fs.join_paths(pwd, "tests/sals/nginx/static"),
            location_type=LocationType.STATIC,
            is_auth=False,
            is_admin=False,
        )
        j.logger.info("Starting the nginx server")
        self.nginx_server.start()
        j.logger.info("Configuring the website")
        static_website.configure()
        j.logger.info("Configuring the location to serve the static website")
        static_location.configure()
        j.logger.info("Reloading the nginx server config")
        self.nginx_server.reload()

        hello_world_page = f"http://{HOST}/hey/"
        another_hello_world_page = f"http://{HOST}/hey/another.html"

        j.logger.info("Checking the two web pages are served correctly")
        self.assertTrue(request_content(hello_world_page).find("Hello") != -1)
        self.assertTrue(request_content(another_hello_world_page).find("Another") != -1)

    def test03_proxy_location(self):
        """ # Test case for serving a proxy location
        Test scenario:
        1. Initialize a python webserver serving directory listing.
        2. Add a proxy location for this server on path /listing.
        3. Check it's served.
        """
        proxy_website = self.nginx_conf.get_website("http_website")
        server = HTTPServer()
        j.logger.info("Initializing a minimal http server")
        server.run()
        proxy_location = proxy_website.locations.get(
            "proxy",
            path_url="/listing/",
            host=HOST,
            port=9090,
            location_type=LocationType.PROXY,
            is_auth=False,
            is_admin=False,
        )
        j.logger.info("Starting nginx server")
        self.nginx_server.start()
        j.logger.info("Configuring the website")
        proxy_website.configure()
        j.logger.info("Configuring the location to serve as a proxy for the http server")
        proxy_location.configure()
        j.logger.info("Reloading nginx server config")
        self.nginx_server.reload()

        proxy_url = f"http://{HOST}/listing/"
        j.logger.info("Checking the http is served")
        self.assertTrue(request_content(proxy_url).find("Directory listing for") != -1)
        j.logger.info("Stopping the http server")
        server.stop()

    def test04_custom_location(self):
        """ # Test case for serving a static location using custom config.
        Test scenario:
        1. Start nginx.
        2. Add a location serving a static website with two pages using custom config.
        3. Check it's served.
        """
        custom_website = self.nginx_conf.get_website("http_website")
        custom_location = custom_website.locations.get("custom", location_type=LocationType.CUSTOM)
        pwd = j.sals.fs.cwd()
        static_url = j.sals.fs.join_paths(pwd, "tests/sals/nginx/static/")
        custom_location.custom_config = f"""
        location /static {{
            set $req_host $host;
            if ($http_host) {{
                set $req_host $http_host;
            }}

            alias {static_url}/;
            index another.html;
        }}
        """
        j.logger.info("Starting nginx server")
        self.nginx_server.start()
        j.logger.info("Configuring the website")
        custom_website.configure()
        j.logger.info("Configuring the custom location to serve a static website")
        custom_location.configure()
        j.logger.info("Reloading nginx server config")
        self.nginx_server.reload()

        proxy_url = f"http://{HOST}/static/"
        j.logger.info("Checking the two website are served correctly")
        self.assertTrue(request_content(proxy_url).find("Another hello world") != -1)

    def test05_ssl_location(self):
        """ # Test case for serving a site over https.
        Test scenario:
        1. Same scenario as the proxy server served over https.
        """
        ssl_website = self.nginx_conf.get_website("https_website")
        ssl_website.ssl = True
        ssl_website.port = 443
        ssl_website.domain = "localhost"
        j.logger.info("Starting a minimal http server")
        server = HTTPServer()
        server.run()
        proxy_location = ssl_website.locations.get(
            "proxy", path_url="/", host=HOST, port=9090, location_type=LocationType.PROXY, is_auth=False, is_admin=False
        )
        j.logger.info("Starting nginx server")
        self.nginx_server.start()
        j.logger.info("Configuring a website serving over https")
        ssl_website.configure()
        j.logger.info("Configuring the location to serve as a proxy for the http server")
        proxy_location.configure()
        j.logger.info("Reloading nginx server config")
        self.nginx_server.reload()

        proxy_url = f"https://localhost/"
        j.logger.info("Checking the website is served correctly")
        self.assertTrue(request_content(proxy_url).find("Directory listing for") != -1)
        j.logger.info("Stopping the http server")
        server.stop()

    def test06_local_server(self):
        """ # Test case for serving a site over https using on a local port.
        Test scenario:
        1. Same scenario as the https scenario served over local https port.
        """
        j.logger.info("Finding a free local port")
        PORTS.init_default_ports(local=True)
        port = PORTS.HTTPS
        static_website = self.nginx_conf.get_website("http_website")
        static_website.ssl = True
        static_website.port = port
        static_website.domain = "localhost"
        pwd = j.sals.fs.cwd()
        static_location = static_website.locations.get(
            "static",
            path_url="/hey",
            path_location=j.sals.fs.join_paths(pwd, "tests/sals/nginx/static"),
            location_type=LocationType.STATIC,
            is_auth=False,
            is_admin=False,
        )
        j.logger.info("Starting the nginx server")
        self.nginx_server.start()
        j.logger.info("Configuring the website")
        static_website.configure()
        j.logger.info("Configuring the location to serve the static website")
        static_location.configure()
        j.logger.info("Reloading the nginx server config")
        self.nginx_server.reload()

        hello_world_http_page = f"https://localhost:{port}/hey/"
        hello_world_https_page = f"https://localhost:{port}/hey/"
        j.logger.info("Checking the two web pages are served correctly")
        self.assertTrue(request_content(hello_world_http_page).find("Hello") != -1)
        self.assertTrue(request_content(hello_world_https_page).find("Hello") != -1)

        PORTS.HTTP = 80
        PORTS.HTTPS = 443

    def tearDown(self):
        if self.nginx_server.is_running():
            self.nginx_server.stop()
        self.nginx_conf.clean()
