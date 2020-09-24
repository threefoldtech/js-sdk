import string
import sys
from unittest import TestCase
from uuid import uuid4
import os
from time import sleep

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

    def test03_kubernetes(self):
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
