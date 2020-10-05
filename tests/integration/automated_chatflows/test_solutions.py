import string
import sys
from unittest import TestCase
from uuid import uuid4
import os
from gevent import sleep
from time import time
import base_test as base
from redis import Redis

sdk_location = __file__.split("tests")[0]
solution_automation_location = f"{sdk_location}solutions_automation"
sys.path.append(solution_automation_location)
import pytest
from jumpscale.loader import j
from solutions_automation import deployer


@pytest.mark.integration
class AutomatedChatflows(TestCase):
    @classmethod
    def setUpClass(cls):

        """ Create Network"""
        cls.network_name = base.random_string()
        cls.wg_name = base.random_string()
        network = deployer.create_network(solution_name=cls.network_name)

        _, wireguard, _ = j.sals.process.execute("sudo wg")
        if cls.wg_name in wireguard:
            j.sals.process.execute(f"sudo wg-quick down /tmp/{cls.wg_name}.conf")

        j.sals.fs.write_file(f"/tmp/{cls.wg_name}.conf", network.wgconf)
        # j.sals.process.execute(f'echo "{network.wgconf}" > /tmp/"{cls.wg_name}".conf')
        j.sals.process.execute(f"sudo wg-quick up /tmp/{cls.wg_name}.conf")

        # prepare ssh
        cls.ssh_client_name = base.random_string()
        if not j.sals.fs.exists("/tmp/.ssh"):
            j.core.executors.run_local('mkdir /tmp/.ssh && ssh-keygen -t rsa -f /tmp/.ssh/id_rsa -q -N "" ')
        cls.ssh_cl = j.clients.sshkey.get(cls.ssh_client_name)
        cls.ssh_cl.private_key_path = "/tmp/.ssh/id_rsa"
        cls.ssh_cl.load_from_file_system()
        cls.ssh_cl.save()
        cls.solution_uuid = ""

    @classmethod
    def tearDownClass(cls):
        # should stop threebot server.
        j.sals.process.execute(f"sudo wg-quick down /tmp/{self.wg_name}.conf")
        j.sals.fs.rmtree(path=f"/tmp/{self.wg_name}.conf")
        j.sals.fs.rmtree(path=f"/tmp/.ssh")

    def tearDown(self):
        if self.solution_uuid:
            j.sals.reservation_chatflow.solutions.cancel_solution_by_uuid(self.solution_uuid)

        j.clients.sshkey.delete(self.ssh_client_name)
        j.clients.sshclient.delete(self.ssh_client_name)

    def wait_for_server_to_access(self, host, port, timeout):
        for _ in range(timeout):
            if j.sals.nettools.tcp_connection_test(host, port, 1):
                sleep(1)
            else:
                return True
        return False

    def test01_ubuntu(self):
        """Test case for create ubuntu.

        **Test Scenario**
        #. create ubuntu
        #. connect to ubuntu
        #. check that ubuntu is accessed
        """

        base.info("create ubuntu.")
        name = base.random_string()
        ubuntu = deployer.deploy_ubuntu(
            solution_name=name, network=self.network_name, ssh=f"{self.ssh_cl.private_key_path}.pub"
        )
        self.solution_uuid = ubuntu.solution_id

        base.info("connect to ubuntu")
        localclient = j.clients.sshclient.get(self.ssh_client_name)
        localclient.sshkey = self.ssh_client_name
        localclient.host = ubuntu.ip_address
        localclient.save()
        self.solution_uuid = ubuntu.solution_id

        base.info("check that ubuntu is accessed")
        self.assertTrue(
            self.wait_for_server_to_access(host=ubuntu.ip_address, port="", timeout=30),
            " Ubuntu is not reached after 30 second",
        )
        _, res, _ = localclient.sshclient.run("cat /etc/os-release")
        self.assertIn("successfully", ubuntu.success())
        self.assertIn('VERSION_ID="18.04"', res)

    def test02_kubernetes(self):
        """Test case for create kubernetes.

        **Test Scenario**
        #. create kubernetes
        #. check connection to master
        """
        base.info("create kubernetes")
        name = base.random_string()
        secret = base.random_string()
        kubernetes = deployer.deploy_kubernetes(
            solution_name=name, secret=secret, network=self.network_name, ssh=f"{self.ssh_cl.private_key_path}.pub",
        )
        self.solution_uuid = kubernetes.solution_id

        localclient = j.clients.sshclient.get(self.ssh_client_name)
        localclient.sshkey = self.ssh_client_name
        localclient.host = f"{kubernetes.ip_addresses[0]}"
        localclient.user = "rancher"
        localclient.save()
        self.assertTrue(
            self.wait_for_server_to_access(host=kubernetes.ip_addresses[0], port="", timeout=30),
            "master is not reached after 30 second",
        )
        _, res, _ = localclient.sshclient.run("kubectl get nodes")
        self.assertIn("successfully", kubernetes.success())
        self.assertIn(15, len(res.split()))

    def test03_create_pool(self):
        """Test case for create pool.

        **Test Scenario**
        #. create pool
        #. check that create pool is successful
        #. check that cu and su as reserved
        """
        base.info("create pool")
        name = base.random_string()
        wallet_name = os.environ.get("WALLET_NAME")
        pool = deployer.create_pool(solution_name=name, wallet_name=wallet_name,)

        base.info("check that create pool is successful")
        reservation_id = pool.pool_data.reservation_id
        pool_data = j.sals.zos.pools.get(reservation_id)

        self.assertEqual(pool_data.cus, 86400.0)
        self.assertEqual(pool_data.sus, 86400.0)

    def test04_minio(self):
        """Test case for create minio.

        **Test Scenario**
        #. create minio
        #. check that create minio is successful"
        """
        base.info("create minio")
        name = base.random_string()
        username = base.random_string()
        password = base.random_string()
        minio = deployer.deploy_minio(
            solution_name=name,
            username=username,
            password=password,
            network=self.network_name,
            ssh=f"{self.ssh_cl.private_key_path}.pub",
        )
        self.solution_uuid = minio.solution_id

        base.info("check that create minio is successful")
        self.assertTrue(
            self.wait_for_server_to_access(host=minio.ip_addresses[0], port=9000, timeout=30),
            "minio is not reached after 30 second",
        )
        request = j.tools.http.get(f"http://{minio.ip_addresses[0]}:9000", verify=False)
        self.assertEqual(request.status_code, 200)

    def test05_monitoring(self):
        """Test case for create monitoring.

        **Test Scenario**
        #. create monitoring
        #. check access prometheus UI
        #. check access grafana UI
        #. check access redis
        """
        base.info("create monitoring")
        name = base.random_string()
        monitoring = deployer.deploy_monitoring(solution_name=name, network=self.network_name,)
        self.solution_uuid = monitoring.solution_id

        base.info("check access prometheus UI")
        request = j.tools.http.get(f"http://{monitoring.ip_addresses[1]}:9090/graph", verify=False)
        self.assertEqual(request.status_code, 200)

        base.info("check access grafana UI")
        request = j.tools.http.get(f"http://{monitoring.ip_addresses[2]}:3000", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("login", request.content.decode())

        base.info("check access redis")
        self.assertTrue(
            self.wait_for_server_to_access(host=monitoring.ip_addresses[0], port="", timeout=30),
            "redis is not reached after 30 second",
        )
        redis = Redis(host=monitoring.ip_addresses[0])
        self.assertEqual(redis.ping(), True)

    def test06_generic_flist(self):
        """Test case for deploy generic flist.

        **Test Scenario**
        #. create flist
        #. check access flist
        """
        base.info("create generic flist")
        name = base.random_string()
        generic_flist = deployer.deploy_generic_flist(
            solution_name=name,
            flist="https://hub.grid.tf/ayoubm.3bot/dmahmouali-mattermost-latest.flist",
            network=self.network_name,
        )
        self.solution_uuid = generic_flist.solution_id

        base.info("check access flist")
        request = j.tools.http.get(f"http://{generic_flist.ip_address}:7681", verify=False)
        self.assertEqual(request.status_code, 200)

    def test07_exposed_flist(self):
        """Test case for exposed flist.

        **Test Scenario**
        #. create flist
        #. create exposed
        #. check access exposed
        """
        base.info("create generic flist")
        flist_name = base.random_string()
        deployer.deploy_generic_flist(
            solution_name=flist_name,
            flist="https://hub.grid.tf/ayoubm.3bot/dmahmouali-mattermost-latest.flist",
            network=self.network_name,
        )

        base.info("create exposed")
        sub_domain = base.random_string()
        exposed = deployer.deploy_exposed(
            type="flist", solution_to_expose=flist_name, sub_domain=sub_domain, tls_port="7681", port="7681"
        )
        self.solution_uuid = exposed.solution_id

        base.info("check access exposed")
        request = j.tools.http.get(f"http://{exposed.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test08_deploy_threebot(self):
        """Test case for deploy threebot

        **Test Scenario**
        #. create threebot
        #. check access threebot
        """
        base.info("create threebot")
        name = base.random_string()
        secret = base.random_string()
        threebot = deployer.deploy_threebot(
            solution_name=name, secret=secret, expiration=time() + 60 * 15, ssh=f"{self.ssh_cl.private_key_path}.pub"
        )
        self.solution_uuid = threebot.solution_id

        base.info("check access threebot")
        request = j.tools.http.get(f"http://{threebot.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test09_recover_threebot(self):
        """Test case for recover threebot

        **Test Scenario**
        #. create threebot
        #. recover threebot
        #. check access recoverd threebot
        """

        base.info("create threebot")
        name = base.random_string()
        secret = base.random_string()
        threebot = deployer.deploy_threebot(
            solution_name=name, secret=secret, expiration=time() + 60 * 15, ssh=f"{self.ssh_cl.private_key_path}.pub"
        )
        base.info("recover threebot")
        threebot = deployer.recover_threebot(
            solution_name=name,
            recover_password=secret,
            ssh=f"{self.ssh_cl.private_key_path}.pub",
            expiration=time() + 60 * 15,
        )
        self.solution_uuid = threebot.solution_id

        base.info("check access recoverd threebot")
        request = j.tools.http.get(f"http://{threebot.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test010_extend_threebot(self):
        """Test case for extend threebot

        **Test Scenario**
        #. create pool
        #. extend threebot
        #. check expiration
        """
        base.info("create pool")
        name = base.random_string()
        wallet_name = os.environ.get("WALLET_NAME")
        deployer.create_pool(
            solution_name=name, wallet_name=wallet_name,
        )

        base.info("extend threebot")
        threebot = deployer.extend_threebot(name=name, expiration=time() + 60 * 15,)
        self.solution_uuid = threebot.solution_id

        base.info("check expiration")
        self.assertEqual(time() + 60 * 15, threebot.expiration)
