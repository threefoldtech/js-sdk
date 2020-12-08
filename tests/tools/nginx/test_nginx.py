from unittest import TestCase
from jumpscale.loader import j
import gevent


class TestNginx(TestCase):
    def _get_instance(self):
        self.instance_name = j.data.random_names.random_name()
        nginx_instance = j.tools.nginx.new(self.instance_name)
        return nginx_instance

    def _get_port(self, proc):
        conn = proc.connections()[0]
        return conn.laddr[1]

    def test001_nginx_start_stop(self):
        """Test case for starting NGINX server and stop it.

        **Test Scenario**

        - Start nginx server .
        - Check if it's running.
        - Stop nginx server server .
        - Check if it's running.
        """
        nginx_instance = self._get_instance()
        nginx_instance.save()
        nginx_instance.start()
        j.logger.info("NGINX server started")

        self.assertTrue(nginx_instance.is_running())

        nginx_instance.stop()
        for _ in range(10):
            if j.sals.nettools.tcp_connection_test("127.0.0.1", 80, 2):
                gevent.sleep(0.2)
            else:
                break
        j.logger.info("NGINX server stopped")
        self.assertFalse(nginx_instance.is_running())

    def test002_nginx_restart(self):
        """Test case for starting NGINX server and stop it.

        **Test Scenario**

        - Start nginx server .
        - Check if it's running.
        - Restart nginx server server.
        - Check if it's running.
        """
        nginx_instance = self._get_instance()
        nginx_instance.save()
        nginx_instance.start()
        j.logger.info("NGINX server started")

        self.assertTrue(nginx_instance.is_running())

        nginx_instance.restart()
        j.logger.info("NGINX server restarted")
        self.assertTrue(nginx_instance.is_running())

    def tearDown(self):
        nginx_instance = j.tools.nginx.find(self.instance_name)
        nginx_instance.stop()
        j.tools.nginx.delete(self.instance_name)
