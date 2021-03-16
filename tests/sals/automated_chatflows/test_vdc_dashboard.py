import gevent
import pytest
from jumpscale.clients.explorer.models import K8s
from jumpscale.loader import j
from jumpscale.sals.vdc.size import VDC_SIZE
from solutions_automation.vdc import deployer
from tests.sals.vdc.vdc_base import VDCBase
from tests.sals.automated_chatflows.chatflows_base import ChatflowsBase
from parameterized import parameterized_class
from jumpscale.clients.stellar import TRANSACTION_FEES


@parameterized_class(("no_deployment"), [("single",), ("double",)])
@pytest.mark.integration
class VDCDashboard(VDCBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._import_wallet("demos_wallet")
        no_deployment = "single"
        cls.flavor = "platinum"

        cls.vdc_name = cls.random_name().lower()
        cls.password = cls.random_string()
        if cls.no_deployment == "single":
            cls.kube_config = cls.deploy_vdc(cls.vdc_name, cls.password)
        else:
            cls.kube_config = cls.deploy_vdc(cls.vdc_name, cls.password, hours=2)

        if not cls.kube_config:
            raise RuntimeError("VDC is not deployed")

        j.sals.fs.copy_file(
            f"{j.sals.fs.home()}/sandbox/cfg/vdc/kube/{cls.vdc.owner_tname}/{cls.vdc.vdc_name}.yaml",
            j.sals.fs.expanduser("~/.kube/config"),
        )
        cls.kube_manager = j.sals.kubernetes.Manager()

        cls.info("Check that resources are available and ready in 5 min maximum")
        cls.kube_monitor = cls.vdc.get_kubernetes_monitor()
        has_resource = False
        resources_expiry = j.data.time.now().timestamp + 300
        while j.data.time.now().timestamp < resources_expiry and not has_resource:
            res = cls.kube_monitor.fetch_resource_reservations()
            for node in res:
                if node.has_enough_resources(1000, 1024):
                    cls.info("Cluster resources are ready")
                    has_resource = True
                    break

        cls.info("Check that traefik is ready in 5 min maximum")
        is_traefik_ready = False
        traefik_expiry = j.data.time.now().timestamp + 300
        while j.data.time.now().timestamp < traefik_expiry and not is_traefik_ready:
            rc, system_pods, err = cls.kube_manager._execute(
                f"kubectl get pods --kubeconfig {cls.kube_manager.config_path} --namespace kube-system | grep traefik"
            )
            running = system_pods.count("Running") + system_pods.count("Completed")
            all = len(system_pods.splitlines())
            if running == all:
                cls.info("Traefik is ready")
                is_traefik_ready = True
                break

        assert is_traefik_ready == True, "Traefik not ready within 5 minutes"

        # Add tokens needed in case of extending the cluster automatically.
        kubernetes = K8s()
        kubernetes.size = VDC_SIZE.K8SNodeFlavor.MEDIUM.value
        # It will be deployed for an hour.
        price = j.tools.zos.consumption.cost(kubernetes, 60 * 60) + TRANSACTION_FEES  # transactions fees.
        cls.vdc.transfer_to_provisioning_wallet(round(price, 6), "test_wallet")

        # Timeout for any exposed solution to be reachable and certified.
        cls.timeout = 60
        # Accept Marketplace T&C for testing identity.
        ChatflowsBase.tname = cls.tname
        ChatflowsBase.accept_terms_conditions(type_="marketplace")

    @classmethod
    def tearDownClass(cls):
        wallet = j.clients.stellar.get("demos_wallet")
        cls.vdc.provision_wallet.merge_into_account(wallet.address)
        cls.vdc.prepaid_wallet.merge_into_account(wallet.address)
        j.sals.vdc.delete(cls.vdc.instance_name)
        super().tearDownClass()

    def setUp(self):
        self.solutions = []
        super().setUp()

    def tearDown(self):
        for sol in self.solutions:
            self.info(f"Delete {sol.release_name}")
            self.kube_manager.execute_native_cmd(f"kubectl delete ns {sol.chart_name}-{sol.release_name}")
        super().tearDown()

    def _set_vdc_identity(self):
        vdc_ident = j.core.identity.get(f"vdc_ident_{self.vdc.solution_uuid}")
        vdc_ident.set_default()

    def _get_and_wait_ssl(self, domain, expire_timeout=180):
        expiry = j.data.time.now().timestamp + expire_timeout
        is_certified = False
        request = None
        while j.data.time.now().timestamp < expiry:
            try:
                request = j.tools.http.get(domain, timeout=self.timeout)
                is_certified = True
                break
            except j.tools.http.exceptions.SSLError:
                self.info("Waiting to check ssl certificate....")
                gevent.sleep(10)

        if not is_certified:
            j.logger.warning(
                f"{domain} can't gain a ssl certificate, it maybe take longer than {expire_timeout/60} min to resolve it, check again later!"
            )
            request = j.tools.http.get(domain, timeout=self.timeout, verify=False)

        return request

    def _check_etcd_ready(self, solution):
        expiry = j.data.time.now().timestamp + 20
        put_hello = ""
        while j.data.time.now().timestamp < expiry:
            rc, put_hello, err = self.kube_manager._execute(
                f"kubectl --kubeconfig {self.kube_manager.config_path} --namespace {solution.chart_name}-{solution.release_name} exec -it {solution.release_name}-etcd-0 -- etcdctl put message Hello"
            )
            if put_hello:
                break
            gevent.sleep(2)
        self.assertEqual(put_hello.count("OK"), 1)

    def test01_wiki(self):
        """Test case for deploying a Wiki.

        **Test Scenario**

        - Deploy VDC
        - Deploy a Wiki.
        - Deploy another Wiki in double test.
        - Check that the Wiki is reachable and certified.
        - Check that deploying another Wiki deployed successfully in double test.
        """
        self.info("Deploy a Wiki.")
        name = self.random_name().lower()
        repo = "https://github.com/threefoldfoundation/wiki_example"
        branch = "main"
        wiki = deployer.deploy_wiki(release_name=name, url=repo, branch=branch)
        self.solutions.append(wiki)

        if self.no_deployment == "double":
            self.info("Deploy another Wiki")
            name_second = self.random_name().lower()
            wiki_second = deployer.deploy_wiki(release_name=name_second, url=repo, branch=branch)
            self.solutions.append(wiki_second)

        self.info("Check that the Wiki is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{wiki.domain}")
        self.assertEqual(request.status_code, 200)

        if self.no_deployment == "double":
            self.info("Check that second Wiki deployed successfully.")
            request_second = j.tools.http.get(url=f"https://{wiki_second.domain}", timeout=self.timeout, verify=False)
            self.assertEqual(request_second.status_code, 200)

    def test02_blog(self):
        """Test case for deploying a Blog.

        **Test Scenario**

        - Deploy VDC
        - Deploy a Blog.
        - Deploy another Blog in double test.
        - Check that the Blog is reachable and certified.
        - Check that deploying another Blog deployed successfully in double test.
        """
        self.info("Deploy Blog.")
        name = self.random_name().lower()
        repo = "https://github.com/threefoldfoundation/blog_example"
        branch = "main"
        blog = deployer.deploy_blog(release_name=name, url=repo, branch=branch)
        self.solutions.append(blog)

        if self.no_deployment == "double":
            self.info("Deploy another Blog.")
            name_second = self.random_name().lower()
            blog_second = deployer.deploy_blog(release_name=name_second, url=repo, branch=branch)
            self.solutions.append(blog_second)

        self.info("Check that the Blog is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{blog.domain}")
        self.assertEqual(request.status_code, 200)

        if self.no_deployment == "double":
            self.info("Check that second Blog deployed successfully.")
            request_second = j.tools.http.get(url=f"https://{blog_second.domain}", timeout=self.timeout, verify=False)
            self.assertEqual(request_second.status_code, 200)

    def test03_website(self):
        """Test case for deploying a Website.

        **Test Scenario**

        - Deploy VDC
        - Deploy a Website.
        - Deploy another Website in double test.
        - Check that the Website is reachable and certified.
        - Check that deploying another Website deployed successfully in double test.
        """
        self.info("Deploy a Website")
        name = self.random_name().lower()
        repo = "https://github.com/threefoldfoundation/website_example"
        branch = "master"
        website = deployer.deploy_website(release_name=name, url=repo, branch=branch)
        self.solutions.append(website)

        if self.no_deployment == "double":
            self.info("Deploy another Website.")
            name_second = self.random_name().lower()
            website_second = deployer.deploy_website(release_name=name_second, url=repo, branch=branch)
            self.solutions.append(website_second)

        self.info("Check that the Website is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{website.domain}")
        self.assertEqual(request.status_code, 200)

        if self.no_deployment == "double":
            self.info("Check that second Website deployed successfully.")
            request_second = j.tools.http.get(
                url=f"https://{website_second.domain}", timeout=self.timeout, verify=False
            )
            self.assertEqual(request_second.status_code, 200)

    def test04_cryptpad(self):
        """Test case for deploying Cryptpad.

        **Test Scenario**

        - Deploy VDC
        - Deploy Cryptpad.
        - Deploy another Cryptpad in double test.
        - Check that Cryptpad is reachable and certified.
        - Check that deploying another Cryptpad deployed successfully in double test.
        """
        self.info("Deploy Cryptpad.")
        name = self.random_name().lower()
        cryptpad = deployer.deploy_cryptpad(release_name=name)
        self.solutions.append(cryptpad)

        if self.no_deployment == "double":
            self.info("Deploy another Cryptpad.")
            name_second = self.random_name().lower()
            cryptpad_second = deployer.deploy_cryptpad(release_name=name_second)
            self.solutions.append(cryptpad_second)

        self.info("Check that Cryptpad is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{cryptpad.domain}")
        self.assertEqual(request.status_code, 200)

        if self.no_deployment == "double":
            self.info("Check that second Cryptpad deployed successfully.")
            request_second = j.tools.http.get(
                url=f"https://{cryptpad_second.domain}", timeout=self.timeout, verify=False
            )
            self.assertEqual(request_second.status_code, 200)

    def test05_gitea(self):
        """Test case for deploying Gitea.

        **Test Scenario**

        - Deploy VDC
        - Deploy Gitea.
        - Deploy another Gitea in double test.
        - Check that Gitea is reachable and certified.
        - Check that deploying another Gitea deployed successfully in double test.
        """
        self.info("Deploy Gitea")
        name = self.random_name().lower()
        gitea = deployer.deploy_gitea(release_name=name)
        self.solutions.append(gitea)

        if self.no_deployment == "double":
            self.info("Deploy another Gitea.")
            name_second = self.random_name().lower()
            gitea_second = deployer.deploy_gitea(release_name=name_second)
            self.solutions.append(gitea_second)

        self.info("Check that Gitea is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{gitea.domain}")
        self.assertEqual(request.status_code, 200)

        if self.no_deployment == "double":
            self.info("Check that second Gitea deployed successfully.")
            request_second = j.tools.http.get(url=f"https://{gitea_second.domain}", timeout=self.timeout, verify=False)
            self.assertEqual(request_second.status_code, 200)

    @pytest.mark.skip("https://github.com/threefoldtech/js-sdk/issues/2630")
    def test06_discourse(self):
        """Test case for deploying Discourse.

        **Test Scenario**

        - Deploy VDC
        - Deploy Discourse.
        - Deploy another Discourse in double test.
        - Check that Discourse is reachable and certified.
        - Check that deploying another Discourse deployed successfully in double test.
        """
        self.info("Deploy Discourse")
        name = self.random_name().lower()
        admin_username = self.random_name().lower()
        admin_password = self.random_name().lower()
        smtp_host = j.data.fake.email()
        smtp_port = "587"
        smtp_username = self.random_name().lower()
        smtp_password = self.random_name().lower()
        discourse = deployer.deploy_discourse(
            release_name=name,
            admin_username=admin_username,
            admin_password=admin_password,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_username=smtp_username,
            smtp_password=smtp_password,
        )
        self.solutions.append(discourse)

        if self.no_deployment == "double":
            self.info("Deploy another Discourse.")
            name_second = self.random_name().lower()
            discourse_second = deployer.deploy_discourse(
                release_name=name_second,
                admin_username=admin_username,
                admin_password=admin_password,
                smtp_host=smtp_host,
                smtp_port=smtp_port,
                smtp_username=smtp_username,
                smtp_password=smtp_password,
            )
            self.solutions.append(discourse_second)

        self.info("Check that Discourse is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{discourse.domain}")
        self.assertEqual(request.status_code, 200)

        if self.no_deployment == "double":
            self.info("Check that second Discourse deployed successfully.")
            request_second = j.tools.http.get(
                url=f"https://{discourse_second.domain}", timeout=self.timeout, verify=False
            )
            self.assertEqual(request_second.status_code, 200)

    def test07_ETCD(self):
        """Test case for deploying ETCD.

        **Test Scenario**

        - Deploy VDC
        - Deploy ETCD.
        - Deploy another ETCD in double test.
        - Check that ETCD add data correctly.
        - Check that deploying another ETCD solution deployed successfully in double test.
        """
        self.info("Deploy ETCD")
        name = self.random_name().lower()
        etcd = deployer.deploy_etcd(release_name=name)
        self.solutions.append(etcd)
        self.info("Check that deployed ETCD add data correctly.")
        self._check_etcd_ready(etcd)

        if self.no_deployment == "double":
            self.info("Deploy another ETCD")
            name_second = self.random_name().lower()
            etcd_second = deployer.deploy_etcd(release_name=name_second)
            self.solutions.append(etcd_second)
            self.info("Check that another deployed ETCD add data correctly.")
            self._check_etcd_ready(etcd_second)

    def test08_Kubeapps(self):
        """Test case for deploying Kubeapps.

        **Test Scenario**

        - Deploy VDC
        - Deploy Kubeapps.
        - Check that Kubeapps is reachable and certified.
        - Check that deploying another Kubeapps will raise error in double test.
        """
        self.info("Deploy Kubeapps")
        name = self.random_name().lower()
        kubeapps = deployer.deploy_kubeapps(release_name=name)
        self.solutions.append(kubeapps)

        self.info("Check that Kubeapps is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{kubeapps.domain}")
        self.assertEqual(request.status_code, 200)

        if self.no_deployment == "double":
            self.info("Check that second MonitoringStack raise error.")
            name_second = self.random_name().lower()
            with self.assertRaises(j.exceptions.Runtime):
                deployer.deploy_kubeapps(release_name=name_second)

    def test09_Peertube(self):
        """Test case for deploying Peertube.

        **Test Scenario**

        - Deploy VDC
        - Deploy Peertube.
        - Deploy another Peertube in double test.
        - Check that Peertube is reachable and certified.
        - Check that deploying another Peertube deployed successfully in double test.
        """
        self.info("Deploy Peertube")
        name = self.random_name().lower()
        peertube = deployer.deploy_peertube(release_name=name)
        self.solutions.append(peertube)

        if self.no_deployment == "double":
            self.info("Deploy another Peertube.")
            name_second = self.random_name().lower()
            peertube_second = deployer.deploy_peertube(release_name=name_second)
            self.solutions.append(peertube_second)

        self.info("Check that Peertube is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{peertube.domain}")
        self.assertEqual(request.status_code, 200)

        if self.no_deployment == "double":
            self.info("Check that second Peertube deployed successfully.")
            request_second = j.tools.http.get(
                url=f"https://{peertube_second.domain}", timeout=self.timeout, verify=False
            )
            self.assertEqual(request_second.status_code, 200)

    @pytest.mark.skip("https://github.com/threefoldtech/js-sdk/issues/2630")
    def test10_Taiga(self):
        """Test case for deploying Taiga.

        **Test Scenario**

        - Deploy VDC
        - Deploy Taiga.
        - Deploy another Taiga in double test.
        - Check that Taiga is reachable and certified.
        - Check that deploying another taiga solution deployed successfully in double test.
        """

        self.info("Deploy Taiga")
        name = self.random_name().lower()
        taiga = deployer.deploy_taiga(release_name=name)
        self.solutions.append(taiga)

        if self.no_deployment == "double":
            self.info("Deploy another Taiga.")
            name_second = self.random_name().lower()
            taiga_second = deployer.deploy_taiga(release_name=name_second)
            self.solutions.append(taiga_second)

        self.info("Check that Taiga is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{taiga.domain}")
        self.assertEqual(request.status_code, 200)

        if self.no_deployment == "double":
            self.info("Check that second Taiga deployed successfully.")
            request_second = j.tools.http.get(url=f"https://{taiga_second.domain}", timeout=self.timeout, verify=False)
            self.assertEqual(request_second.status_code, 200)

    def test11_Mattermost(self):
        """Test case for deploying Mattermost.

        **Test Scenario**

        - Deploy VDC
        - Deploy Mattermost.
        - Deploy another Mattermost in double test.
        - Check that Mattermost is reachable and certified.
        - Check that deploying another Mattermost deployed successfully in double test.
        """
        self.info("Deploy Mattermost")
        name = self.random_name().lower()
        mysql_username = self.random_name().lower()
        mysql_password = self.random_name().lower()
        mysql_root_password = self.random_name().lower()
        mattermost = deployer.deploy_mattermost(
            release_name=name,
            mysql_username=mysql_username,
            mysql_password=mysql_password,
            mysql_root_password=mysql_root_password,
        )
        self.solutions.append(mattermost)

        if self.no_deployment == "double":
            self.info("Deploy another Mattermost.")
            name_second = self.random_name().lower()
            mattermost_second = deployer.deploy_mattermost(
                release_name=name_second,
                mysql_username=mysql_username,
                mysql_password=mysql_password,
                mysql_root_password=mysql_root_password,
            )
            self.solutions.append(mattermost_second)

        self.info("Check that Mattermost is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{mattermost.domain}")
        self.assertEqual(request.status_code, 200)

        if self.no_deployment == "double":
            self.info("Check that second Mattermost deployed successfully.")
            request_second = j.tools.http.get(
                url=f"https://{mattermost_second.domain}", timeout=self.timeout, verify=False
            )
            self.assertEqual(request_second.status_code, 200)

    def test12_ZeroCI(self):
        """Test case for deploying ZeroCI.

        **Test Scenario**

        - Deploy VDC
        - Deploy ZeroCI.
        - Deploy another ZeroCI in double test.
        - Check that ZeroCI is reachable and certified.
        - Check that deploying another ZeroCI deployed successfully in double test.
        """
        self.info("Deploy ZeroCI")
        name = self.random_name().lower()
        zeroci = deployer.deploy_zeroci(release_name=name)
        self.solutions.append(zeroci)

        if self.no_deployment == "double":
            self.info("Deploy another ZeroCI.")
            name_second = self.random_name().lower()
            zeroci_second = deployer.deploy_zeroci(release_name=name_second)
            self.solutions.append(zeroci_second)

        self.info("Check that ZeroCI is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{zeroci.domain}")
        self.assertEqual(request.status_code, 200)

        if self.no_deployment == "double":
            self.info("Check that second ZeroCI deployed successfully.")
            request_second = j.tools.http.get(url=f"https://{zeroci_second.domain}", timeout=self.timeout, verify=False)
            self.assertEqual(request_second.status_code, 200)

    def test13_MonitoringStack(self):
        """Test case for deploying MonitoringStack.

        **Test Scenario**

        - Deploy VDC
        - Deploy MonitoringStack.
        - Check that MonitoringStack is reachable and certified.
        - Check that deploying another MonitoringStack will raise error in double test.
        """
        self.info("Deploy MonitoringStack")
        name = self.random_name().lower()
        monitoring = deployer.deploy_monitoring(release_name=name)
        self.solutions.append(monitoring)

        self.info("Check that MonitoringStack is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{monitoring.domain}")
        self.assertEqual(request.status_code, 200)

        if self.no_deployment == "double":
            self.info("Check that second MonitoringStack raise error.")
            name_second = self.random_name().lower()
            with self.assertRaises(j.exceptions.Runtime):
                deployer.deploy_monitoring(release_name=name_second)

    def test14_Digibyte(self):
        """Test case for deploying Digibyte.

        **Test Scenario**

        - Deploy VDC
        - Deploy Digibyte.
        - Check that Digibyte is reachable and certified.
        - Deploy another Digibyte in double test.
        - Check that deploying another Digibyte will raise error in double test.
        """
        self.info("Deploy Digibyte")
        name = self.random_name().lower()
        rpc_username = self.random_name().lower()
        rpc_password = self.random_name().lower()
        digibyte = deployer.deploy_digibyte(release_name=name, rpc_username=rpc_username, rpc_password=rpc_password,)
        self.solutions.append(digibyte)

        self.info("Check that Digibyte is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{digibyte.domain}")
        self.assertEqual(request.status_code, 200)

        if self.no_deployment == "double":
            self.info("Check that second Digibyte raise error.")
            name_second = self.random_name().lower()
            with self.assertRaises(j.exceptions.Runtime):
                deployer.deploy_digibyte(
                    release_name=name_second, rpc_username=rpc_username, rpc_password=rpc_password,
                )

    def test15_ExtendKubernetes(self):
        """Test case for extending Kubernetes cluster.

        **Test Scenario**

        - Deploy VDC.
        - Get the number of nodes before extending.
        - Extend Kubernetes cluster.
        - Get the number of nodes after extending.
        - Check that node has been added.
        """

        self.info("Set vdc indentity")
        self._set_vdc_identity()

        if self.no_deployment == "double":
            self.skipTest("No need to test it in double deployments")

        self.info("Get Number of Nodes before extend")
        self.vdc.load_info()
        number_of_nodes_before = len(self.vdc.kubernetes)
        before_extend = self.kube_manager.execute_native_cmd("kubectl get nodes")
        self.info("Extend Kubernetes")
        size = "MEDIUM"
        extend_node = deployer.extend_kubernetes(size=size)

        self.info("Check that node added")
        self.vdc.load_info()
        number_of_nodes_after = len(self.vdc.kubernetes)
        self.assertEqual(number_of_nodes_after, number_of_nodes_before + 1)

        self.info("Check that node added and ready")
        # Set timeout for 2 min
        is_ready = False
        expiry = j.data.time.now().timestamp + 120
        while j.data.time.now().timestamp < expiry:
            after_extend = self.kube_manager.execute_native_cmd("kubectl get nodes")
            if after_extend.count("Ready") == before_extend.count("Ready") + 1:
                is_ready = True
                break
            gevent.sleep(5)
        self.assertTrue(is_ready, "Added node not ready for 2 mins")
