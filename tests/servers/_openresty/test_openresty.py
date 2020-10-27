import unittest

from jumpscale.loader import j


class TestOpenResty(unittest.TestCase):
    def setUp(self):
        self.instance_name = j.data.random_names.random_name()
        self.server = j.servers.openresty.new(self.instance_name)

    def test001_write_config(self):

        self.assertEqual(self.server.status.value, "init")
        self.server.configure()

        server_config = j.sals.fs.read_file(self.server.path_cfg)
        self.assertIn(f"error_log {self.server.logs_dir}", server_config)

        website_name = j.data.random_names.random_name()
        website = self.server.websites.new(website_name)
        website.domain = "www.testdomain.com"

        loc_name = j.data.random_names.random_name()
        location = website.locations.new(loc_name)
        location.location_type = "proxy"
        location.ipaddr_dest = "0.0.0.0"
        location.path_dest = "/"
        location.path_url = "/calendar/"
        location.port_dest = 8851
        location.scheme = "http"

        website.configure()

        website_config = j.sals.fs.read_file(website.path_cfg)
        self.assertIn(f"?{website.domain}$;", website_config)
        self.assertIn(f"listen {website.port};", website_config)
        self.assertIn(f"include {website.path_cfg_dir}/{website.instance_name}_locations/*.conf;", website_config)

        loc_config = j.sals.fs.read_file(location.path_cfg)

        self.assertIn(f"location { location.path_url }", loc_config)
        self.assertIn(
            f"proxy_pass {location.scheme}://{location.ipaddr_dest}:{location.port_dest}{location.path_dest};",
            loc_config,
        )

    def tearDown(self):
        self.server.cleanup()
        j.servers.openresty.delete(self.instance_name)
