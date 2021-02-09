import gevent
import pytest
from jumpscale.loader import j
from solutions_automation.vdc import deployer
from tests.sals.vdc.vdc_base import VDCBase
from tests.sals.automated_chatflows.chatflows_base import ChatflowsBase


@pytest.mark.integration
class VDCDashboard(VDCBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.flavor = "platinum"
        cls.kube_config = cls.deploy_vdc()
        cls.kube_manager = j.sals.kubernetes.Manager(
            f"{j.sals.fs.home()}/sandbox/cfg/vdc/kube/{cls.vdc.owner_tname}/{cls.vdc.vdc_name}.yaml"
        )
        j.sals.fs.copy_file(
            f"{j.sals.fs.home()}/sandbox/cfg/vdc/kube/{cls.vdc.owner_tname}/{cls.vdc.vdc_name}.yaml",
            j.sals.fs.expanduser("~/.kube/config"),
        )
        if not cls.kube_config:
            raise RuntimeError("VDC is not deployed")
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
        self.solution = None
        super().setUp()

    def tearDown(self):
        if self.solution:
            self.info(f"Delete {self.solution.release_name}")
            self.solution.k8s_client.delete_deployed_release(self.solution.release_name)
        super().tearDown()

    @classmethod
    def _import_wallet(cls):
        super()._import_wallet()
        wallet = j.clients.stellar.get("demos_wallet")
        wallet.secret = cls.wallet_secret
        wallet.network = "STD"
        wallet.save()
        return wallet

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

        self.assertTrue(is_certified, f"{domain} can't gain a ssl certificate")
        return request

    def test01_wiki(self):
        """Test case for deploying a wiki.

        **Test Scenario**

        - Deploy VDC
        - Deploy a wiki.
        - Check that the Wiki is reachable and certified.
        """
        self.info("Deploy a wiki.")
        name = self.random_name().lower()
        repo = "https://github.com/threefoldfoundation/wiki_example"
        branch = "main"
        wiki = deployer.deploy_wiki(release_name=name, url=repo, branch=branch)
        self.solution = wiki

        self.info("Check that the wiki is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{wiki.domain}")
        self.assertEqual(request.status_code, 200)

    def test02_blog(self):
        """Test case for deploying a blog.

        **Test Scenario**

        - Deploy VDC
        - Deploy a Blog.
        - Check that the Blog is reachable and certified.
        """
        self.info("Deploy blog.")
        name = self.random_name().lower()
        repo = "https://github.com/threefoldfoundation/blog_example"
        branch = "main"
        blog = deployer.deploy_blog(release_name=name, url=repo, branch=branch)
        self.solution = blog

        self.info("Check that the blog is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{blog.domain}")
        self.assertEqual(request.status_code, 200)

    def test03_website(self):
        """Test case for deploying a website.

        **Test Scenario**

        - Deploy VDC
        - Deploy a website.
        - Check that the Website is reachable and certified.
        """
        self.info("Deploy a website")
        name = self.random_name().lower()
        repo = "https://github.com/threefoldfoundation/website_example"
        branch = "main"
        website = deployer.deploy_website(release_name=name, url=repo, branch=branch)
        self.solution = website

        self.info("Check that the website is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{website.domain}")
        self.assertEqual(request.status_code, 200)

    def test04_cryptpad(self):
        """Test case for deploying Cryptpad.

        **Test Scenario**

        - Deploy VDC
        - Deploy Cryptpad.
        - Check that Cryptpad is reachable and certified.
        """
        self.info("Deploy Cryptpad")
        name = self.random_name().lower()
        cryptpad = deployer.deploy_cryptpad(release_name=name)
        self.solution = cryptpad

        self.info("Check that Cryptpad is reachable and certified")
        request = self._get_and_wait_ssl(domain=f"https://{cryptpad.domain}")
        self.assertEqual(request.status_code, 200)

    def test05_gitea(self):
        """Test case for deploying Gitea.

        **Test Scenario**

        - Deploy VDC
        - Deploy Gitea.
        - Check that Gitea is reachable and certified.
        """
        self.info("Deploy Gitea")
        name = self.random_name().lower()
        gitea = deployer.deploy_gitea(release_name=name)
        self.solution = gitea

        self.info("Check that Gitea is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{gitea.domain}")
        self.assertEqual(request.status_code, 200)

    def test06_discourse(self):
        """Test case for deploying Discourse.

        **Test Scenario**

        - Deploy VDC
        - Deploy Discourse.
        - Check that Discourse is reachable and certified.
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
        self.solution = discourse
        self.info("Check that Discourse is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{discourse.domain}")
        self.assertEqual(request.status_code, 200)

    def test07_ETCD(self):
        """Test case for deploying ETCD.

        **Test Scenario**

        - Deploy VDC
        - Deploy ETCD.
        - Check that ETCD add data correctly.
        """
        self.info("Deploy ETCD")
        name = self.random_name().lower()
        etcd = deployer.deploy_etcd(release_name=name)
        self.solution = etcd

        self.info("Check that ETCD add data correctly.")
        expiry = j.data.time.now().timestamp + 20
        put_hello = ""
        while j.data.time.now().timestamp < expiry:
            rc, put_hello, err = j.sals.kubernetes.Manager._execute(
                f"kubectl --kubeconfig {self.kube_manager.config_path} exec -it {name}-etcd-0 -- etcdctl put message Hello"
            )
            if put_hello:
                break
            gevent.sleep(2)
        self.assertEqual(put_hello.count("OK"), 1)

    def test08_Kubeapps(self):
        """Test case for deploying Kubeapps.

        **Test Scenario**

        - Deploy VDC
        - Deploy Kubeapps.
        - Check that Kubeapps is reachable and certified.
        """
        self.info("Deploy Kubeapps")
        name = self.random_name().lower()
        kubeapps = deployer.deploy_kubeapps(release_name=name)
        self.solution_uuid = kubeapps.solution_id
        self.solution = kubeapps

        self.info("Check that Kubeapps is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{kubeapps.domain}")
        self.assertEqual(request.status_code, 200)

    def test09_Peertube(self):
        """Test case for deploying Peertube.

        **Test Scenario**

        - Deploy VDC
        - Deploy Peertube.
        - Check that Peertube is reachable and certified.
        """
        self.info("Deploy Peertube")
        name = self.random_name().lower()
        peertube = deployer.deploy_peertube(release_name=name)
        self.solution = peertube

        self.info("Check that Peertube is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{peertube.domain}")
        self.assertEqual(request.status_code, 200)

    def test10_Taiga(self):
        """Test case for deploying Taiga.

        **Test Scenario**

        - Deploy VDC
        - Deploy Taiga.
        - Check that Taiga is reachable and certified.
        """
        self.info("Deploy Taiga")
        name = self.random_name().lower()
        taiga = deployer.deploy_taiga(release_name=name)
        self.solution = taiga

        self.info("Check that Taiga is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{taiga.domain}")
        self.assertEqual(request.status_code, 200)

    def test11_Mattermost(self):
        """Test case for deploying Mattermost.

        **Test Scenario**

        - Deploy VDC
        - Deploy Mattermost.
        - Check that Mattermost is reachable and certified.
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
        self.solution = mattermost

        self.info("Check that Mattermost is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{mattermost.domain}")
        self.assertEqual(request.status_code, 200)

    def test12_ZeroCI(self):
        """Test case for deploying ZeroCI.

        **Test Scenario**

        - Deploy VDC
        - Deploy ZeroCI.
        - Check that ZeroCI is reachable and certified.
        """
        self.info("Deploy ZeroCI")
        name = self.random_name().lower()
        zeroci = deployer.deploy_zeroci(release_name=name)
        self.solution = zeroci

        self.info("Check that ZeroCI is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{zeroci.domain}")
        self.assertEqual(request.status_code, 200)

    def test13_MonitoringStack(self):
        """Test case for deploying MonitoringStack.

        **Test Scenario**

        - Deploy VDC
        - Deploy MonitoringStack.
        - Check that MonitoringStack is reachable and certified.
        """
        self.info("Deploy MonitoringStack")
        name = self.random_name().lower()
        monitoring = deployer.deploy_monitoring(release_name=name)
        self.solution = monitoring

        self.info("Check that MonitoringStack is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{monitoring.domain}")
        self.assertEqual(request.status_code, 200)

    def test14_Digibyte(self):
        """Test case for deploying Digibyte.

        **Test Scenario**

        - Deploy VDC
        - Deploy Digibyte.
        - Check that Digibyte is reachable and certified.
        """
        self.info("Deploy Digibyte")
        name = self.random_name().lower()
        rpc_username = self.random_name().lower()
        rpc_password = self.random_name().lower()
        digibyte = deployer.deploy_digibyte(release_name=name, rpc_username=rpc_username, rpc_password=rpc_password,)
        self.solution = digibyte

        self.info("Check that Digibyte is reachable and certified.")
        request = self._get_and_wait_ssl(domain=f"https://{digibyte.domain}")
        self.assertEqual(request.status_code, 200)

    def test15_ExtendKubernetes(self):
        """Test case for extending Kubernetes cluster.

        **Test Scenario**

        - Deploy VDC.
        - Get the number of nodes before extending.
        - Extend Kubernetes cluster.
        - Get the number of nodes after extending.
        - Check that node has been added.
        """
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
