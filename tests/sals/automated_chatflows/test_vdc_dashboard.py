from tests.base_tests import BaseTests
from jumpscale.sals.marketplace import solutions
import pytest
from jumpscale.loader import j
from solutions_automation.vdc import deployer
from tests.sals.vdc.vdc_base import VDCBase


@pytest.mark.integration
class VDCDashboardChatflows(VDCBase):
    @classmethod
    def setUpClass(cls):
        # super().setUpClass()
        cls._get_env_vars()
        cls._import_wallet()
        cls._start_threebot_server()
        cls.vdc = j.sals.vdc.vdc_essamvdc_essam
        cls.kube_manager = j.sals.kubernetes.Manager(
            f"{j.sals.fs.home()}/sandbox/cfg/vdc/kube/{cls.vdc.owner_tname}/{cls.vdc.vdc_name}.yaml"
        )
        # cls.flavor = "silver"
        # cls.kube_config = cls.deploy_vdc()
        # if not cls.kube_config:
        #     raise RuntimeError("VDC is not deployed")
        # Timeout for any exposed solution to be reachable.
        cls.timeout = 60

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()
        # j.sals.vdc.delete(cls.vdc.instance_name)
        # super().tearDownClass()

    def setUp(self):
        self.solution = None
        return super().setUp()

    def tearDown(self):
        self.info(f"Delete {self.solution.release_name}")
        if self.solution:
            self.solution.k8s_client.delete_deployed_release(self.solution.release_name)

        super().tearDown()

    @classmethod
    def _import_wallet(cls):
        j.clients.stellar.get("demos_wallet", network="STD", secret=cls.wallet_secret)

    # def test01_wiki(self):
    #     """Test case for deploying a wiki.

    #     **Test Scenario**

    #     - Deploy VDC
    #     - Deploy a wiki.
    #     - Check that the wiki is reachable.
    #     """
    #     self.info("Deploy a wiki.")
    #     name = self.random_string().lower()
    #     title = self.random_string().lower()
    #     repo = "https://github.com/threefoldfoundation/wiki_example"
    #     branch = "main"
    #     wiki = deployer.deploy_wiki(release_name=name, title=title, url=repo, branch=branch)
    #     self.solution_uuid = wiki.solution_id
    #     self.solution = wiki

    #     self.info("Check that the wiki is reachable.")
    #     request = j.tools.http.get(f"https://{wiki.domain}", verify=False, timeout=self.timeout)
    #     self.assertEqual(request.status_code, 200)

    # def test02_blog(self):
    #     """Test case for deploying a blog.

    #     **Test Scenario**

    #     - Deploy VDC
    #     - Deploy a Blog.
    #     - Check that the blog is reachable.
    #     """
    #     self.info("Deploy blog.")
    #     name = self.random_string().lower()
    #     title = self.random_string().lower()
    #     repo = "https://github.com/threefoldfoundation/blog_threefold"
    #     branch = "main"
    #     blog = deployer.deploy_blog(release_name=name, title=title, url=repo, branch=branch)
    #     self.solution_uuid = blog.solution_id
    #     self.solution = blog

    #     self.info("Check that the blog is reachable.")
    #     request = j.tools.http.get(f"https://{blog.domain}", verify=False, timeout=self.timeout)
    #     self.assertEqual(request.status_code, 200)

    # def test03_website(self):
    #     """Test case for deploying a website.

    #     **Test Scenario**

    #     - Deploy VDC
    #     - Deploy a website.
    #     - Check that the website is reachable.
    #     """
    #     self.info("Deploy a website")
    #     name = self.random_string().lower()
    #     title = self.random_string().lower()
    #     repo = "https://github.com/xmonader/www_incubaid"
    #     branch = "main"
    #     website = deployer.deploy_website(solution_name=name, title=title, repo=repo, branch=branch)
    #     self.solution_uuid = website.solution_id
    #     self.solution = website

    #     self.info("Check that the website is reachable.")
    #     request = j.tools.http.get(f"https://{website.domain}", verify=False, timeout=self.timeout)
    #     self.assertEqual(request.status_code, 200)

    def test04_cryptpad(self):
        """Test case for deploying Cryptpad.

        **Test Scenario**

        - Deploy VDC
        - Deploy Cryptpad.
        - Check that Cryptpad is reachable.
        """
        self.info("Deploy Cryptpad")
        name = self.random_string().lower()
        cryptpad = deployer.deploy_cryptpad(release_name=name)
        self.solution_uuid = cryptpad.solution_id
        self.solution = cryptpad

        self.info("Check that Cryptpad is reachable")
        request = j.tools.http.get(f"https://{cryptpad.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)

    def test05_gitea(self):
        """Test case for deploying Gitea.

        **Test Scenario**

        - Deploy VDC
        - Deploy Gitea.
        - Check that Gitea is reachable.
        """
        self.info("Deploy Gitea")
        name = BaseTests.random_name().lower()
        gitea = deployer.deploy_gitea(release_name=name)
        self.solution_uuid = gitea.solution_id
        self.solution = gitea

        self.info("Check that Gitea is reachable.")
        request = j.tools.http.get(f"https://{gitea.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)

    def test06_discourse(self):
        """Test case for deploying Discourse.

        **Test Scenario**

        - Deploy VDC
        - Deploy Discourse.
        - Check that Discourse is reachable.
        """
        self.info("Deploy Discourse")
        name = self.random_string().lower()
        discourse = deployer.deploy_discourse(release_name=name)
        self.solution_uuid = discourse.solution_id
        self.solution = discourse

        self.info("Check that Discourse is reachable.")
        request = j.tools.http.get(f"https://{discourse.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)

    def test07_Kubeapps(self):
        """Test case for deploying Kubeapps.

        **Test Scenario**

        - Deploy VDC
        - Deploy Kubeapps.
        - Check that Kubeapps is reachable.
        """
        self.info("Deploy Kubeapps")
        name = self.random_string().lower()
        kubeapps = deployer.deploy_kubeapps(release_name=name)
        self.solution_uuid = kubeapps.solution_id
        self.solution = kubeapps

        self.info("Check that Kubeapps is reachable.")
        request = j.tools.http.get(f"https://{kubeapps.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)

    def test08_Peertube(self):
        """Test case for deploying Peertube.

        **Test Scenario**

        - Deploy VDC
        - Deploy Peertube.
        - Check that Peertube is reachable.
        """
        self.info("Deploy Peertube")
        name = self.random_string().lower()
        peertube = deployer.deploy_peertube(release_name=name)
        self.solution_uuid = peertube.solution_id
        self.solution = peertube

        self.info("Check that Peertube is reachable.")
        request = j.tools.http.get(f"https://{peertube.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)

    def test09_Taiga(self):
        """Test case for deploying Taiga.

        **Test Scenario**

        - Deploy VDC
        - Deploy Taiga.
        - Check that Taiga is reachable.
        """
        self.info("Deploy Taiga")
        name = self.random_string().lower()
        taiga = deployer.deploy_taiga(release_name=name)
        self.solution_uuid = taiga.solution_id
        self.solution = taiga

        self.info("Check that Taiga is reachable.")
        request = j.tools.http.get(f"https://{taiga.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)

    def test10_Mattermost(self):
        """Test case for deploying Mattermost.

        **Test Scenario**

        - Deploy VDC
        - Deploy Mattermost.
        - Check that Mattermost is reachable.
        """
        self.info("Deploy Mattermost")
        name = self.random_string().lower()
        mysql_username = self.random_string().lower()
        mysql_password = self.random_string().lower()
        mysql_root_password = self.random_string().lower()
        mattermost = deployer.deploy_mattermost(
            release_name=name,
            mysql_username=mysql_username,
            mysql_password=mysql_password,
            mysql_root_password=mysql_root_password,
        )
        self.solution_uuid = mattermost.solution_id
        self.solution = mattermost

        self.info("Check that Mattermost is reachable.")
        request = j.tools.http.get(f"https://{mattermost.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)

    def test11_ZeroCI(self):
        """Test case for deploying ZeroCI.

        **Test Scenario**

        - Deploy VDC
        - Deploy ZeroCI.
        - Check that ZeroCI is reachable.
        """
        self.info("Deploy ZeroCI")
        name = self.random_string().lower()
        zeroci = deployer.deploy_zeroci(release_name=name)
        self.solution_uuid = zeroci.solution_id
        self.solution = zeroci

        self.info("Check that ZeroCI is reachable.")
        request = j.tools.http.get(f"https://{zeroci.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)

    def test12_MonitoringStack(self):
        """Test case for deploying MonitoringStack.

        **Test Scenario**

        - Deploy VDC
        - Deploy MonitoringStack.
        - Check that MonitoringStack is reachable.
        """
        self.info("Deploy MonitoringStack")
        name = self.random_string().lower()
        monitoring = deployer.deploy_monitoring(release_name=name)
        self.solution_uuid = monitoring.solution_id
        self.solution = monitoring

        self.info("Check that MonitoringStack is reachable.")
        request = j.tools.http.get(f"https://{monitoring.domain}", verify=False, timeout=self.timeout)
        self.assertEqual(request.status_code, 200)

    def test13_ExtendKubernetes(self):
        """Test case for Extend Kubernetes cluster.

        **Test Scenario**

        - Deploy VDC
        - Extend Kubernetes cluster.
        - Check that node added.
        """
        self.info("Get Number of Nodes before extend")
        before_extend = self.kube_manager.execute_native_cmd("kubectl get nodes")
        self.info("Extend Kubernetes")
        name = self.random_string().lower()
        size = "MEDIUM"
        extend_node = deployer.ExtendKubernetesAutomated(release_name=name, size=size)

        self.info("Check that node added and ready")
        after_extend = self.kube_manager.execute_native_cmd("kubectl get nodes")
        self.assertEqual(after_extend.count("Ready"), before_extend.count("Ready") + 1)
