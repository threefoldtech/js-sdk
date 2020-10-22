import os
from time import time

import pytest
from jumpscale.loader import j
from redis import Redis
from solutions_automation import deployer

from tests.sals.automated_chatflows.chatflows_base import ChatflowsBase


@pytest.mark.integration
class TFGridSolutionChatflows(ChatflowsBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Accept admin T&C for testing identity.
        cls.accept_terms_conditions(type_="admin")

        # Create Network
        cls.network_name = cls.random_name()
        cls.wg_conf_path = f"/tmp/{cls.random_name()}.conf"
        network = deployer.create_network(solution_name=cls.network_name)
        j.sals.fs.write_file(cls.wg_conf_path, network.wgconf)
        j.sals.process.execute(f"sudo wg-quick up {cls.wg_conf_path}")

        # Prepare ssh
        cls.ssh_client_name = cls.random_name()
        if not j.sals.fs.exists("/tmp/.ssh"):
            j.core.executors.run_local(
                'mkdir /tmp/.ssh && ssh-keygen -t rsa -f /tmp/.ssh/id_rsa -q -N "" '
            )  # TODO: Fix me use ssh generate method
        cls.ssh_cl = j.clients.sshkey.get(cls.ssh_client_name)
        cls.ssh_cl.private_key_path = "/tmp/.ssh/id_rsa"
        cls.ssh_cl.load_from_file_system()
        cls.ssh_cl.save()
        cls.solution_uuid = ""

    @classmethod
    def tearDownClass(cls):
        # should stop threebot server.
        j.sals.process.execute(f"sudo wg-quick down {cls.wg_conf_path}")
        j.sals.fs.rmtree(path=cls.wg_conf_path)
        j.sals.fs.rmtree(path="/tmp/.ssh")
        j.clients.sshkey.delete(cls.ssh_client_name)

        # delete network
        network_view = j.sals.reservation_chatflow.deployer.get_network_view(cls.network_name)
        wids = [w.id for w in network_view.network_workloads]
        j.sals.zos.get().workloads.decomission(workload_id=wids[0])

        # Remove userEntry for accepting T&C
        cls.user_factory.delete(cls.user_entry_name)
        super().tearDownClass()

    def tearDown(self):
        if self.solution_uuid:
            j.sals.reservation_chatflow.solutions.cancel_solution_by_uuid(self.solution_uuid)
        j.clients.sshclient.delete(self.ssh_client_name)
        super().tearDown()

    def test01_ubuntu(self):
        """Test case for create ubuntu.

        **Test Scenario**
        - create ubuntu
        - connect to ubuntu
        - check that ubuntu is accessed
        """
        self.info("create ubuntu.")
        name = self.random_name()
        ubuntu = deployer.deploy_ubuntu(solution_name=name, network=self.network_name, ssh=self.ssh_cl.public_key_path)
        self.solution_uuid = ubuntu.solution_id

        self.info("connect to ubuntu")
        localclient = j.clients.sshclient.get(self.ssh_client_name)
        localclient.sshkey = self.ssh_client_name
        localclient.host = ubuntu.ip_address
        localclient.save()
        self.solution_uuid = ubuntu.solution_id

        self.info("check that ubuntu is accessed")
        self.assertTrue(
            j.sals.nettools.tcp_connection_test(ubuntu.ip_address, port=22, timeout=40),
            "Ubuntu is not reached after 40 second",
        )
        _, res, _ = localclient.sshclient.run("cat /etc/os-release")
        self.assertIn('VERSION_ID="18.04"', res)

    def test02_kubernetes(self):
        """Test case for create kubernetes.

        **Test Scenario**
        - create kubernetes
        - check connection to master
        """
        self.info("create kubernetes")
        name = self.random_name()
        secret = self.random_name()
        workernodes = 1
        kubernetes = deployer.deploy_kubernetes(
            solution_name=name,
            secret=secret,
            network=self.network_name,
            workernodes=workernodes,
            ssh=self.ssh_cl.public_key_path,
        )
        self.solution_uuid = kubernetes.solution_id

        localclient = j.clients.sshclient.get(self.ssh_client_name)
        localclient.sshkey = self.ssh_client_name
        localclient.host = kubernetes.ip_addresses[0]
        localclient.user = "rancher"
        localclient.save()
        self.assertTrue(
            j.sals.nettools.tcp_connection_test(kubernetes.ip_addresses[0], port=22, timeout=40),
            "master is not reached after 40 second",
        )

        _, res, _ = localclient.sshclient.run("kubectl get nodes")
        res = res.splitlines()
        res = res[2:]  # Remove master node and header
        self.assertEqual(workernodes, len(res))

    def test03_minio(self):
        """Test case for create minio.

        **Test Scenario**
        - create minio
        - check that create minio is successful"
        """
        self.info("create minio")
        name = self.random_name()
        username = self.random_name()
        password = self.random_name()
        minio = deployer.deploy_minio(
            solution_name=name,
            username=username,
            password=password,
            network=self.network_name,
            ssh=self.ssh_cl.public_key_path,
        )
        self.solution_uuid = minio.solution_id

        self.info("check that create minio is successful")
        self.assertTrue(
            j.sals.nettools.tcp_connection_test(minio.ip_addresses[0], port=9000, timeout=40),
            "minio is not reached after 40 second",
        )
        request = j.tools.http.get(f"http://{minio.ip_addresses[0]}:9000", verify=False)
        self.assertEqual(request.status_code, 200)

    def test04_monitoring(self):
        """Test case for create monitoring.

        **Test Scenario**
        - create monitoring
        - check access prometheus UI
        - check access grafana UI
        - check access redis
        """
        self.info("create monitoring")
        name = self.random_name()
        monitoring = deployer.deploy_monitoring(solution_name=name, network=self.network_name,)
        self.solution_uuid = monitoring.solution_id

        self.info("check access prometheus UI")
        request = j.tools.http.get(f"http://{monitoring.ip_addresses[1]}:9090/graph", verify=False)
        self.assertEqual(request.status_code, 200)

        self.info("check access grafana UI")
        request = j.tools.http.get(f"http://{monitoring.ip_addresses[2]}:3000", verify=False)
        self.assertEqual(request.status_code, 200)
        self.assertIn("login", request.content.decode())

        self.info("check access redis")
        self.assertTrue(
            j.sals.nettools.tcp_connection_test(monitoring.ip_addresses[0], port=6379, timeout=40),
            "redis is not reached after 40 second",
        )
        redis = Redis(host=monitoring.ip_addresses[0])
        self.assertEqual(redis.ping(), True)

    def test05_generic_flist(self):
        """Test case for deploy generic flist.

        **Test Scenario**
        - create flist
        - check access flist
        """
        self.info("create generic flist")
        name = self.random_name()
        generic_flist = deployer.deploy_generic_flist(
            solution_name=name,
            flist="https://hub.grid.tf/ayoubm.3bot/dmahmouali-mattermost-latest.flist",
            network=self.network_name,
        )
        self.solution_uuid = generic_flist.solution_id

        self.info("check access flist")
        request = j.tools.http.get(f"http://{generic_flist.ip_address}:7681", verify=False)
        self.assertEqual(request.status_code, 200)

    def test06_exposed_flist(self):
        """Test case for exposed flist.

        **Test Scenario**
        - create flist
        - create exposed
        - check access exposed
        """
        self.info("create generic flist")
        flist_name = self.random_name()
        deployer.deploy_generic_flist(
            solution_name=flist_name,
            flist="https://hub.grid.tf/ayoubm.3bot/dmahmouali-mattermost-latest.flist",
            network=self.network_name,
        )

        self.info("create exposed")
        sub_domain = self.random_name()
        exposed = deployer.deploy_exposed(
            type="flist", solution_to_expose=flist_name, sub_domain=sub_domain, tls_port="7681", port="7681"
        )
        self.solution_uuid = exposed.solution_id

        self.info("check access exposed")
        request = j.tools.http.get(f"http://{exposed.domain}", verify=False)
        self.assertEqual(request.status_code, 200)
