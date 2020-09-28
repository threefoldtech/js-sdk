import string
import sys
from unittest import TestCase
from uuid import uuid4
import os
from time import sleep
from time import time

sdk_location = __file__.split("tests")[0]
solution_automation_location = f"{sdk_location}solutions_automation"
sys.path.append(solution_automation_location)
import pytest
from jumpscale.loader import j
from solutions_automation import deployer


@pytest.mark.integration
class AutomatedChatflows(TestCase):
    def random_string(self):
        return j.data.idgenerator.nfromchoices(10, string.ascii_lowercase)

    def info(self, msg):
        j.logger.info(msg)

    @classmethod
    def setUpClass(cls):

        """ Create Network"""
        cls.network_name = j.data.idgenerator.nfromchoices(10, string.ascii_lowercase)
        network = deployer.create_network(solution_name=cls.network_name)
        _, wireguard, _ = j.sals.process.execute("sudo wg")
        if "wg-12" in wireguard:
            j.sals.process.execute("sudo wg-quick down /tmp/wg-12.conf")

        j.sals.process.execute(f'echo "{network.wgconf}" > /tmp/wg-12.conf')
        j.sals.process.execute("sudo wg-quick up /tmp/wg-12.conf")

        """ prepare ssh """
        if not j.sals.fs.exists("/tmp/.ssh"):
            j.core.executors.run_local('mkdir /tmp/.ssh && ssh-keygen -t rsa -f /tmp/.ssh/id_rsa -q -N "" ')
        ssh_cl = j.clients.sshkey.get("network_script")
        ssh_cl.private_key_path = "/tmp/.ssh/id_rsa"
        ssh_cl.load_from_file_system()
        ssh_cl.save()

    @classmethod
    def tearDownClass(cls):
        # should stop threebot server.
        j.sals.process.execute("sudo wg-quick down /tmp/wg-12.conf")

    def tearDown(self):
        # j.sals.reservation_chatflow.solutions.cancel_solution(self.workloads)
        pass

    def test01_ubuntu(self):
        """Test case for create ubuntu.

        **Test Scenario**
        #. create ubuntu
        #. connect to ubuntu
        #. check that ubuntu is accessed
        """

        self.info("create ubuntu.")
        name = self.random_string()
        ubuntu = deployer.deploy_ubuntu(solution_name=name, network=self.network_name, ssh="/tmp/.ssh/id_rsa.pub")

        self.info("connect to ubuntu")
        localclient = j.clients.sshclient.get("network_script")
        localclient.sshkey = "network_script"
        localclient.host = ubuntu.ip_address
        localclient.save()

        self.info("check that ubuntu is accessed")
        sleep(30)
        _, res, _ = localclient.sshclient.run("hostname")

        self.assertIn("successfully", ubuntu.success())
        self.assertIn("zos", res)

    def test02_kubernetes(self):
        """Test case for create kubernetes.

        **Test Scenario**
        #. create kubernetes
        #. check connection to master
        """
        self.info("create kubernetes")
        name = self.random_string()
        secret = self.random_string()
        kubernetes = deployer.deploy_kubernetes(
            solution_name=name, secret=secret, network=self.network_name, ssh="/tmp/.ssh/id_rsa.pub",
        )

        localclient = j.clients.sshclient.get("network_script")
        localclient.sshkey = "network_script"
        localclient.host = f"{kubernetes.ip_addresses[0]}"
        localclient.save()

        sleep(30)
        _, res, _ = localclient.sshclient.run("hostname")
        self.assertIn("successfully", kubernetes.success())
        self.assertIn("k3os", res)

    def test03_create_pool(self):
        """Test case for create pool.

        **Test Scenario**
        #. create pool
        #. check that create pool is successful
        #. check that cu and su as reserved
        """
        self.info("create pool")
        name = self.random_string()
        wallet_name = os.environ.get("WALLET_NAME")
        pool = deployer.create_pool(solution_name=name, wallet_name=wallet_name,)

        self.info("check that create pool is successful")
        self.assertIn("reservation_id", dir(pool.pool_data))
        self.assertEqual(pool.cu, 1)
        self.assertEqual(pool.su, 1)

    def test04_minio(self):
        """Test case for create minio.

        **Test Scenario**
        #. create minio
        #. check that create minio is successful"
        """
        self.info("create minio")
        name = self.random_string()
        username = self.random_string()
        password = self.random_string()
        minio = deployer.deploy_minio(
            solution_name=name,
            username=username,
            password=password,
            network=self.network_name,
            ssh="/tmp/.ssh/id_rsa.pub",
        )

        self.info("check that create minio is successful")
        request = j.tools.http.get(f"http://{minio.ip_addresses[0]}:9000", verify=False)
        self.assertEqual(request.status_code, 200)

    def test05_monitoring(self):
        """Test case for create monitoring.

        **Test Scenario**
        #. create monitoring
        #. check access prometheus UI
        #. check access grafana UI
        """
        self.info("create monitoring")
        name = self.random_string()
        monitoring = deployer.deploy_monitoring(solution_name=name, network=self.network_name,)

        self.info("check access prometheus UI")
        request = j.tools.http.get(f"http://{monitoring.ip_addresses[1]}:9090/graph", verify=False)
        self.assertEqual(request.status_code, 200)

        self.info("check access grafana UI")
        request = j.tools.http.get(f"http://{monitoring.ip_addresses[2]}:3000", verify=False)
        self.assertEqual(request.status_code, 200)

    def test06_generic_flist(self):
        """Test case for deploy generic flist.

        **Test Scenario**
        #. create flist
        #. check access flist
        """
        self.info("create generic flist")
        name = self.random_string()
        generic_flist = deployer.deploy_generic_flist(
            solution_name=name,
            flist="https://hub.grid.tf/ayoubm.3bot/dmahmouali-mattermost-latest.flist",
            network=self.network_name,
        )

        self.info("check access flist")
        request = j.tools.http.get(f"http://{generic_flist.ip_address}:7681", verify=False)
        self.assertEqual(request.status_code, 200)

    def test07_exposed_flist(self):
        """Test case for deploy generic flist.

        **Test Scenario**
        #. create exposed
        #. check access exposed
        """
        self.info("create exposed")
        exposed = deployer.deploy_exposed(
            type="flist", solution_to_expose="hlhujlh", sub_domain="hassan1", tls_port="7681", port="7681"
        )

        self.info("check access exposed")
        request = j.tools.http.get(f"http://{exposed.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test08_deploy_threebot(self):
        """Test case for deploy three bot

        **Test Scenario**
        #. create threebot
        #. check access threebot
        """

        self.info("create threebot")
        name = self.random_string()
        secret = self.random_string()
        threebot = deployer.deploy_threebot(
            solution_name=name, secret=secret, expiration=time() * 60 + 15, ssh="/tmp/.ssh/id_rsa.pub"
        )
        self.info("check access threebot")
        request = j.tools.http.get(f"http://{threebot.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test09_recover_threebot(self):
        """Test case for recover threebot

        **Test Scenario**
        #. recover threebot
        #. check access recoverd threebot
        """

        self.info("recover threebot")
        threebot = deployer.recover_threebot(
            solution_name="", recover_password="", ssh="/tmp/.ssh/id_rsa.pub", expiration=time() * 60 + 15,
        )

        self.info("check access recoverd threebot")
        request = j.tools.http.get(f"http://{threebot.domain}", verify=False)
        self.assertEqual(request.status_code, 200)

    def test010_extend_threebot(self):
        """Test case for extend threebot

        **Test Scenario**
        #. extend threebot
        #. check access threebot
        """

        self.info("extend threebot")
        threebot = deployer.extend_threebot(name="testthreebot", expiration=time() * 60 * 60 + 15,)

        self.info("check if extend threebot is successful")
        self.assertIn("", threebot.success())
