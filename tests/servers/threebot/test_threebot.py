from os import environ
from gevent import monkey
from random import randint
from jumpscale.loader import j
from tests.base_tests import BaseTests

monkey.patch_all(subprocess=False)


class Test3BotServer(BaseTests):
    tname = environ.get("tname")
    email = environ.get("email")
    words = environ.get("words")
    explorer_url = environ.get("explorer_url")
    MYID_NAME = "identity_{}".format(randint(1, 1000))

    @classmethod
    def setUpClass(cls):
        myid = j.core.identity.new(cls.MYID_NAME, tname=cls.tname, email=cls.email, words=cls.words,
                                   explorer_url=cls.explorer_url)
        myid.register()
        j.core.identity.set_default(cls.MYID_NAME)
        myid.save()

    def tearDown(self):
        j.servers.threebot.default.stop()

    @classmethod
    def tearDownClass(cls):
        j.core.identity.delete(cls.MYID_NAME)

    def check_threebot_main_running_servers(self):
        self.info("Make sure that server started successfully by check nginx_main, redis_default and gedis work.")
        self.info("*** nginx server ***")
        _, nginx_output, error = j.sals.process.execute(" ps -aux | grep -v grep | grep nginx_main")
        self.assertTrue(nginx_output)
        self.info(" * Check that nginx server connection works successfully and right port.")
        self.assertTrue(j.sals.nettools.tcp_connection_test("localhost", 80, 2))
        self.assertTrue(j.sals.nettools.tcp_connection_test("localhost", 443, 2))

        self.info("*** redis server ***")
        _, redis_output, error = j.sals.process.execute(" ps -aux | grep -v grep | grep redis")
        self.assertTrue(redis_output)
        self.info(" * Check that redis server connection  works successfully and right port.")
        self.assertTrue(j.sals.nettools.tcp_connection_test("localhost", 6379, 2))

        self.info("*** gedis server ***")
        self.info(" * Check that gedis server connection  works successfully and right port.")
        self.assertTrue(j.sals.nettools.tcp_connection_test("localhost", 16000, 2))

    def check_threebot_main_running_servers_stopped_correctly(self):
        self.info("Check servers stopped successfully.")
        self.info("Make sure that server stopped successfully by check nginx_main, redis_default and gedis don't work.")
        self.assertFalse(j.sals.nettools.tcp_connection_test("localhost", 80, 3), "Nginx still running")
        self.assertFalse(j.sals.nettools.tcp_connection_test("localhost", 443, 3), "Nginx still running")
        self.assertFalse(j.sals.nettools.tcp_connection_test("localhost", 16000, 3), "gedis still running")

    def test01_start_threebot(self):
        """
        Test start threebot server.

        **Test scenario**
        #. Start threebot server.
        #. Check it works correctly.
        """

        self.info("Start threebot server")
        j.servers.threebot.start_default()

        self.info("Check it works correctly")
        self.check_threebot_main_running_servers()

    def test02_stop_threebot(self):
        """
        Test stop threebot server.

        **Test scenario**
        #. Start threebot server.
        #. Check it works correctly.
        #. Stop threebot server.
        #. Check it stopped correctly.
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
        """
        Test is_running method.
        **Test scenario**
        #. Start threebot server.
        #. Check it works correctly.
        #. Use is_running, The output should be True.
        #. Stop threebot server.
        #. Check it stopped correctly.
        #. Use is_running, The output should be False.
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
