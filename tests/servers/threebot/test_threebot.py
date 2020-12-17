from os import environ
from random import randint

from gevent import sleep
from jumpscale.loader import j
from tests.base_tests import BaseTests


class Test3BotServer(BaseTests):
    tname = environ.get("TNAME")
    email = environ.get("EMAIL")
    words = environ.get("WORDS")
    explorer_url = "https://explorer.testnet.grid.tf/api/v1"
    MYID_NAME = "identity_{}".format(randint(1, 1000))

    @classmethod
    def setUpClass(cls):
        if not all([cls.tname, cls.email, cls.words]):
            raise Exception("Please add (TNAME, EMAIL, WORDS) of your 3bot identity as environment variables")
        cls.me = None
        if j.core.identity.list_all() and hasattr(j.core.identity, "me"):
            cls.me = j.core.identity.me
        myid = j.core.identity.new(
            cls.MYID_NAME, tname=cls.tname, email=cls.email, words=cls.words, explorer_url=cls.explorer_url
        )
        myid.register()
        myid.set_default()
        myid.save()

    def tearDown(self):
        j.servers.threebot.default.stop()

    @classmethod
    def tearDownClass(cls):
        j.core.identity.delete(cls.MYID_NAME)
        if cls.me:
            cls.me.set_default()

    def wait_for_server_to_stop(self, host, port, timeout):
        for _ in range(timeout):
            if j.sals.nettools.tcp_connection_test(host, port, 1):
                sleep(1)
            else:
                return True
        return False

    def check_threebot_main_running_servers(self):
        self.info("Make sure that server started successfully by check nginx_main, redis_default and gedis work.")
        self.info("*** nginx server ***")
        self.assertTrue(j.sals.process.get_pids("nginx"), "Nginx didn't start correctly")
        self.info(" * Check that nginx server connection works successfully and right port.")
        self.assertTrue(j.sals.nettools.tcp_connection_test("localhost", 80, 5))
        self.assertTrue(j.sals.nettools.tcp_connection_test("localhost", 443, 5))

        self.info("*** redis server ***")
        self.assertTrue(j.sals.process.get_pids("redis"), "redis didn't start correctly")
        self.info(" * Check that redis server connection  works successfully and right port.")
        self.assertTrue(j.sals.nettools.tcp_connection_test("localhost", 6379, 5))

        self.info("*** gedis server ***")
        self.info(" * Check that gedis server connection  works successfully and right port.")
        self.assertTrue(j.sals.nettools.tcp_connection_test("localhost", 16000, 5))
        self.assertTrue(j.sals.nettools.tcp_connection_test("localhost", 8000, 5))

    def check_threebot_main_running_servers_stopped_correctly(self):
        self.info("Check servers stopped successfully.")
        self.info("Make sure that server stopped successfully by check nginx_main, redis_default and gedis don't work.")
        self.assertTrue(self.wait_for_server_to_stop("localhost", 80, 5), "Nginx still running")
        self.assertTrue(self.wait_for_server_to_stop("localhost", 443, 5), "Nginx still running")
        self.assertTrue(self.wait_for_server_to_stop("localhost", 16000, 5), "gedis still running")
        self.assertTrue(self.wait_for_server_to_stop("localhost", 8000, 5), "gedis still running")

    def test01_start_threebot(self):
        """Test start threebot server.

        **Test Scenario**

        - Start threebot server.
        - Check it works correctly.
        """
        self.info("Start threebot server")
        j.servers.threebot.start_default()

        self.info("Check it works correctly")
        self.check_threebot_main_running_servers()

    def test02_stop_threebot(self):
        """Test stop threebot server.

        **Test Scenario**

        - Start threebot server.
        - Check it works correctly.
        - Stop threebot server.
        - Check it stopped correctly.
        """
        self.info("Start threebot server")
        j.servers.threebot.start_default()

        self.info("Check it works correctly")
        self.check_threebot_main_running_servers()

        self.info("Stop threebot server")
        j.servers.threebot.default.stop()

        self.info("Check it stopped correctly")
        self.check_threebot_main_running_servers_stopped_correctly()

    def test03_is_running(self):
        """Test is_running method.

        **Test Scenario**

        - Start threebot server.
        - Check it works correctly.
        - Use is_running, The output should be True.
        - Stop threebot server.
        - Check it stopped correctly.
        - Use is_running, The output should be False.
        """
        self.info("Start threebot server")
        j.servers.threebot.start_default()

        self.info("Check it works correctly")
        self.check_threebot_main_running_servers()

        self.info("Use is_running, The output should be True")
        self.assertTrue(j.servers.threebot.default.is_running())

        self.info("Stop threebot server")
        j.servers.threebot.default.stop()

        self.info("Check it stopped correctly")
        self.check_threebot_main_running_servers_stopped_correctly()

        self.info("Use is_running, The output should be False")
        self.assertFalse(j.servers.threebot.default.is_running())

    def test04_check_default_package_list(self):
        """Test default package list with threebot server.

        **Test Scenario**

        - Start threebot server.
        - Check the package list that should be started by default with threebot server.
        ['auth', 'chatflows', 'admin', 'weblibs', 'tfgrid_solutions', 'backup']
        """
        self.info("Start threebot server")
        j.servers.threebot.start_default()

        self.info("Check the package list that should be started by default with threebot server")
        default_packages_list = ["auth", "chatflows", "admin", "weblibs", "tfgrid_solutions", "backup"]
        packages_list = j.servers.threebot.default.packages.list_all()
        self.assertTrue(set(default_packages_list).issubset(packages_list), "not all default packages exist")

    def test05_package_add_and_delete(self):
        """Test case for adding and deleting package in threebot server

        **Test Scenario**

        - Add a package.
        - Check that the package has been added.
        - Try to add wrong package, and make sure that the error has been raised.
        - Delete a package.
        - Check that the package is deleted correctly.
        - Try to delete non exists package, and make sure that the error has been raised.
        """
        self.info("Add a package")
        from jumpscale.packages import marketplace

        path = j.sals.fs.dirname(marketplace.__file__)

        marketplace = j.servers.threebot.default.packages.add(path)
        marketplace_dir = {"marketplace": {"name": "marketplace", "path": path, "giturl": None, "kwargs": {},}}
        self.assertEqual(marketplace, marketplace_dir)

        self.info("Check that the package has been added")
        packages_list = j.servers.threebot.default.packages.list_all()
        self.assertIn("marketplace", packages_list)

        self.info("Try to add wrong package, and check that there is an error")
        with self.assertRaises(Exception) as error:
            j.servers.threebot.default.packages.add("test_wrong_package")
            self.assertIn("No such file or directory : 'test_wrong_package/package.toml'", error.exception.args[0])

        self.info("Delete a package")
        j.servers.threebot.default.packages.delete("marketplace")

        self.info("Check that the package is deleted correctly")
        packages_list = j.servers.threebot.default.packages.list_all()
        self.assertNotIn("marketplace", packages_list)

        self.info("Try to delete non exists package, and make sure that the error has been raised")
        with self.assertRaises(Exception) as error:
            j.servers.threebot.default.packages.delete("test_wrong_package")
            self.assertIn("test_wrong_package package not found", error.exception.args[0])
