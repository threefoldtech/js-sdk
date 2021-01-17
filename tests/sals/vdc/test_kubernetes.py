from jumpscale.sals.kubernetes.manager import is_helm_installed
from jumpscale.sals import kubernetes
import pytest
from jumpscale.loader import j
from parameterized import parameterized_class

from .vdc_base import VDCBase


@parameterized_class(("flavor"), [("silver",)])
@pytest.mark.integration
class TestVDC(VDCBase):
    flavor = "silver"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kube_config = cls.deploy_vdc()
        cls.kube_manager = j.sals.kubernetes.Manager()
        if not cls.kube_config:
            raise RuntimeError("VDC is not deployed")

    @classmethod
    def deploy_vdc(cls):
        cls.vdc_name = cls.random_name()
        cls.password = cls.random_string()
        cls.vdc = j.sals.vdc.new(cls.vdc_name, cls.tname, cls.flavor)

        cls.info("Transfer needed TFT to deploy vdc for an hour to the provisioning wallet.")
        vdc_price = j.tools.zos.consumption.calculate_vdc_price(cls.flavor)
        needed_tft = float(vdc_price) / 24 / 30 + 0.2  # 0.2 transaction fees for creating the pool and extend it
        cls.vdc.transfer_to_provisioning_wallet(needed_tft, "test_wallet")

        cls.info("Deploy VDC.")
        deployer = cls.vdc.get_deployer(password=cls.password)
        minio_ak = cls.random_name()
        minio_sk = cls.random_string()
        kube_config = deployer.deploy_vdc(minio_ak, minio_sk)
        return kube_config

    @classmethod
    def tearDownClass(cls):
        # j.sals.vdc.delete(cls.vdc.instance_name) Todo: Uncomment before merging with development_vdc
        super().tearDownClass()

    def test_01_update_helm_repos(self):
        """Test case for updating helm repos.

        **Test Scenario**

        - Deploy VDC - OR Kubernetes
        - Update Helm Repos
        - Check from Logs that all repos are updated.
        """
        self.info("Update all helm repos.")
        update_msg = self.kube_manager.update_repos()
        is_updated = False
        self.info("Check that all repos are successfully updated")
        if update_msg.count("Successfully") == len(self.kube_manager.list_helm_repos()):
            is_updated = True
        self.assertTrue(is_updated)

    def test_02_add_helm_repo(self):
        """Test case for adding new helm repo.

        **Test Scenario**

        - Deploy VDC - OR Kubernetes
        - Add Helm Repo
        - Check that the added rebo listed in the helm repos.
        """
        self.info("Add prometheus-community repo")
        repo_name = "prometheus-community"
        repo_url = "https://prometheus-community.github.io/helm-charts"
        self.kube_manager.add_helm_repo(repo_name, repo_url)

        self.info("Check that prometheus-community added")
        is_added = False
        for repo in self.kube_manager.list_helm_repos():
            if repo["name"] == repo_name and repo["url"] == repo_url:
                is_added = True
                break
        self.assertTrue(is_added)

    def test_03_list_helm_repos(self):
        """Test case for list all helm repos.

        **Test Scenario**

        - Deploy VDC - OR Kubernetes
        - list all Helm Repos
        - Check that all repos are listed.
        """
        self.info("list all Helm Repos")
        all_repos = self.kube_manager.list_helm_repos()
        is_listed = False
        self.info("Check that helm repo listed")
        if not (all_repos is None):
            is_listed = True
        self.assertTrue(is_listed)

    def test_04_install_chart(self):
        """Test case for install helm chart.

        **Test Scenario**

        - Deploy VDC - OR Kubernetes
        - Install Helm Chart
        - Check that chart is installed.
        """
        self.info("Install etcd chart from bitnami repo")
        release_name = "testetcd"
        release_chart = "bitnami/etcd"
        self.kube_manager.install_chart(release_name, release_chart)
        self.info("Check if chart installed")
        is_installed = False
        for release in self.kube_manager.list_deployed_releases():
            if release["name"] == release_name and release["status"] == "deployed":
                is_installed = True
                break
        self.assertTrue(is_installed)

    def test_05_list_deployed_charts(self):
        """Test case for listing all deployed charts.

        **Test Scenario**

        - Deploy VDC - OR Kubernetes
        - List all deployed charts
        - Check that all deployed charts are listed.
        """
        self.info("list all deployed charts")
        all_deployed_charts = self.kube_manager.list_deployed_releases()
        is_listed = False
        self.info("Check that deployed charts listed")
        if not (all_deployed_charts is None):
            is_listed = True
        self.assertTrue(is_listed)

    def test_06_delete_deployed_chart(self):
        """Test case for delete deployed chart.

        **Test Scenario**

        - Deploy VDC - OR Kubernetes
        - Deploy ETCD Chart
        - Delete Deployed Chart
        - List all deployed charts
        - Check that deleted chart not in deployed charts.
        """
        self.info("Deploy ETCD chart")
        release_name = "testdeletechart"
        release_chart = "bitnami/etcd"
        self.kube_manager.install_chart(release_name, release_chart)
        self.info("Delete etcd release that installed before")
        self.kube_manager.delete_deployed_release(release_name)
        self.info("Check if deployed chart deleted")
        is_deleted = True
        for release in self.kube_manager.list_deployed_releases():
            if release["name"] == release_name:
                is_deleted = False
                break
        self.assertTrue(is_deleted)

    def test_07_is_helm_installed(self):
        """Test case to check if helm installed.

        **Test Scenario**

        - Deploy VDC - OR Kubernetes
        - Check if helm installed.
        """
        self.info("Check if helm installed")
        is_helm_installed = j.sals.kubernetes.manager.is_helm_installed()
        self.assertTrue(is_helm_installed)

    def test_08_execute_native_cmd(self):
        """Test case for executing a native kubernetes commands.

        **Test Scenario**

        - Deploy VDC - OR Kubernetes
        - Excute Kubernetes Command
        - Check that the command executed correctly.
        """

        self.info("Execute kubectl get nodes")
        cmd_out = self.kube_manager.execute_native_cmd("kubectl get nodes")
        self.info("Check if command executed correctly")
        # Check is True if there is one master node and at least 2 Ready nodes
        is_executed = False
        if cmd_out.count("master") == 1 and cmd_out.count("Ready") >= 2:
            is_executed = True
        self.assertTrue(is_executed)
