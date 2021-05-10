import math
from time import time

from jumpscale.loader import j
from jumpscale.sals.nginx.nginx import PORTS, LocationType
from tests.base_tests import BaseTests

HOST = "127.0.0.1"
NGINX_CONFIG_FILE = "nginx.conf"
DIR_PATH = j.sals.fs.dirname(j.sals.fs.realpath(__file__))


def wait_connection_lost_test(url, timeout):
    start_time = time()
    while time() - start_time <= timeout:
        if not j.sals.nettools.wait_http_test(url, math.ceil(time() - start_time)):
            return True
    return False


def request_content(url, verify=False):
    return j.tools.http.get(url, verify=verify).content.decode()


class HTTPServer:
    def __init__(self):
        self.instance = None
        self.instance_name = j.data.random_names.random_name()

    def run(self, port=9090):
        self.instance = j.tools.startupcmd.new(self.instance_name)
        self.instance.start_cmd = f"python3 -m http.server {port}"
        self.instance.start()
        self.instance.save()

    def stop(self):
        if self.instance is None:
            return
        self.instance.stop()
        j.tools.startupcmd.delete(self.instance_name)
        self.instance = None


class TestNginxSal(BaseTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        j.sals.process.kill_process_by_name("nginx")

    def setUp(self):
        super().setUp()
        self.nginx_conf = j.sals.nginx.get("testing")
        self.config_base_dir = self.nginx_conf.cfg_dir
        self.config_file = self.nginx_conf.cfg_file
        self.logs_dir = self.nginx_conf._cfg_dir
        self.nginx_server = j.tools.nginx.get("testing_server", server_name="testing")
        self.server = HTTPServer()

    def test01_basic(self):
        """Test case for server initialization with default config.

        **Test Scenario**

        - Start the nginx server.
        - Check the config is stored and the server is started.
        - Clean up the config and stop the server.
        - Check the server is stopped.
        """

        http_link = f"http://{HOST}:8999"

        self.info("Configuring the nginx server")
        self.nginx_conf.configure()
        self.info("Starting the nginx server")
        self.nginx_server.start()
        self.info("Checking the config is stored and the server is started")
        self.assertTrue(j.sals.fs.is_file(j.sals.fs.join_paths(self.config_base_dir, NGINX_CONFIG_FILE)))
        self.assertTrue(j.sals.nettools.wait_http_test(http_link, 5))
        self.assertIn("Welcome to 3Bot", request_content(http_link))
        self.info("Cleaning up the config and stoping the server")
        self.nginx_server.stop()
        self.nginx_conf.clean()

        self.info("Checking the server is stopped")
        self.assertFalse(j.sals.fs.is_file(j.sals.fs.join_paths(self.config_base_dir, NGINX_CONFIG_FILE)))
        self.assertTrue(wait_connection_lost_test(http_link, 5))

    def test02_static_location(self):
        """Test case for serving a static location.

        **Test Scenario**

        - Start nginx server.
        - Configure a static website with two pages.
        - Check they're served.
        """
        static_website = self.nginx_conf.get_website("http_website")
        endpoint = self.random_name()
        static_location = static_website.locations.get(
            "static",
            path_url=f"/{endpoint}",
            path_location=j.sals.fs.join_paths(DIR_PATH, "static"),
            location_type=LocationType.STATIC,
            is_auth=False,
            is_admin=False,
        )
        self.info("Starting the nginx server")
        self.nginx_server.start()
        self.info("Configuring the website")
        static_website.configure()
        self.info("Configuring the location to serve the static website")
        static_location.configure()
        self.info("Reloading the nginx server config")
        self.nginx_server.reload()

        hello_world_page = f"http://{HOST}/{endpoint}/"
        another_hello_world_page = f"http://{HOST}/{endpoint}/another.html"

        self.info("Checking the two web pages are served correctly")
        self.assertIn("Hello", request_content(hello_world_page))
        self.assertIn("Another", request_content(another_hello_world_page))

    def test03_proxy_location(self):
        """Test case for serving a proxy location.

        **Test Scenario**

        - Initialize a python webserver serving directory listing.
        - Start nginx server.
        - Configur the website to act as a proxy to the python server.
        - Check the http is served.
        """
        proxy_website = self.nginx_conf.get_website("http_website")

        self.info("Initializing a minimal http server")
        http_port = j.data.idgenerator.random_int(8000, 9000)
        self.server.run(http_port)
        endpoint = self.random_name()
        proxy_location = proxy_website.locations.get(
            "proxy",
            path_url=f"/{endpoint}/",
            host=HOST,
            port=http_port,
            location_type=LocationType.PROXY,
            is_auth=False,
            is_admin=False,
        )
        self.info("Starting nginx server")
        self.nginx_server.start()
        self.info("Configuring the website")
        proxy_website.configure()
        self.info("Configuring the location to serve as a proxy for the http server")
        proxy_location.configure()
        self.info("Reloading nginx server config")
        self.nginx_server.reload()

        proxy_url = f"http://{HOST}/{endpoint}/"
        self.info("Checking the http is served")
        self.assertIn("Directory listing for", request_content(proxy_url))

    def test04_custom_location(self):
        """Test case for serving a static location using custom config.

        **Test Scenario**

        - Start nginx.
        - Add a location serving a static website with two pages using custom config.
        - Check it's served.
        """
        custom_website = self.nginx_conf.get_website("http_website")
        custom_location = custom_website.locations.get("custom", location_type=LocationType.CUSTOM)
        static_url = j.sals.fs.join_paths(DIR_PATH, "static")
        endpoint = self.random_name()
        custom_location.custom_config = f"""
        location /{endpoint} {{
            set $req_host $host;
            if ($http_host) {{
                set $req_host $http_host;
            }}

            alias {static_url}/;
            index another.html;
        }}
        """
        self.info("Starting nginx server")
        self.nginx_server.start()
        self.info("Configuring the website")
        custom_website.configure()
        self.info("Configuring the custom location to serve a static website")
        custom_location.configure()
        self.info("Reloading nginx server config")
        self.nginx_server.reload()

        proxy_url = f"http://{HOST}/{endpoint}/"
        self.info("Checking the two website are served correctly")
        self.assertIn("Another hello world", request_content(proxy_url))

    def test05_ssl_location(self):
        """Test case for serving a site over https.

        **Test Scenario**

        - Same scenario as the proxy server served over https.
        """
        ssl_website = self.nginx_conf.get_website("https_website")
        ssl_website.ssl = True
        ssl_website.port = 443
        ssl_website.domain = "localhost"
        self.info("Starting a minimal http server")
        http_port = j.data.idgenerator.random_int(8000, 9000)
        self.server.run(http_port)
        proxy_location = ssl_website.locations.get(
            "proxy",
            path_url="/",
            host=HOST,
            port=http_port,
            location_type=LocationType.PROXY,
            is_auth=False,
            is_admin=False,
        )
        self.info("Starting nginx server")
        self.nginx_server.start()
        self.info("Configuring a website serving over https")
        ssl_website.configure()
        self.info("Configuring the location to serve as a proxy for the http server")
        proxy_location.configure()
        self.info("Reloading nginx server config")
        self.nginx_server.reload()

        proxy_url = f"https://localhost/"
        self.info("Checking the website is served correctly")
        self.assertIn("Directory listing for", request_content(proxy_url))
        self.info("Stopping the http server")

    def test06_local_server(self):
        """Test case for serving a site over https using on a local port.

        **Test Scenario**

        - Same scenario as the https scenario served over local https port.
        """
        self.info("Finding a free local port")
        PORTS.init_default_ports(local=True)
        port = PORTS.HTTPS
        endpoint = self.random_name()
        static_website = self.nginx_conf.get_website("http_website")
        static_website.ssl = True
        static_website.port = port
        static_website.domain = "localhost"
        static_location = static_website.locations.get(
            "static",
            path_url=f"/{endpoint}",
            path_location=j.sals.fs.join_paths(DIR_PATH, "static"),
            location_type=LocationType.STATIC,
            is_auth=False,
            is_admin=False,
        )
        self.info("Starting the nginx server")
        self.nginx_server.start()
        self.info("Configuring the website")
        static_website.configure()
        self.info("Configuring the location to serve the static website")
        static_location.configure()
        self.info("Reloading the nginx server config")
        self.nginx_server.reload()

        hello_world_http_page = f"https://localhost:{port}/{endpoint}/"
        hello_world_https_page = f"https://localhost:{port}/{endpoint}/"
        self.info("Checking the two web pages are served correctly")
        self.assertIn("Hello", request_content(hello_world_http_page))
        self.assertIn("Hello", request_content(hello_world_https_page))

        PORTS.HTTP = 80
        PORTS.HTTPS = 443

    def tearDown(self):
        if self.nginx_server.is_running():
            self.nginx_server.stop()
        self.nginx_conf.clean()
        self.server.stop()
        super().tearDown()
