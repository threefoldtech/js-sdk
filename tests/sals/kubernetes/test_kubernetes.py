from jumpscale.sals.kubernetes.manager import is_helm_installed
from jumpscale.sals import kubernetes
import pytest
from jumpscale.loader import j

from tests.sals.vdc.vdc_base import VDCBase


@pytest.mark.integration
class TestKubernetes(VDCBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.flavor = "silver"
        cls.kube_config = cls.deploy_vdc()
        cls.kube_manager = j.sals.kubernetes.Manager(
            f"{j.sals.fs.home()}/sandbox/cfg/vdc/kube/{cls.vdc.owner_tname}/{cls.vdc.vdc_name}.yaml"
        )
        if not cls.kube_config:
            raise RuntimeError("VDC is not deployed")

    @classmethod
    def tearDownClass(cls):
        j.sals.vdc.delete(cls.vdc.instance_name)
        super().tearDownClass()

    def test_01_update_helm_repos(self):
        """Test case for updating helm repos.

        **Test Scenario**

        - Deploy VDC
        - Update helm repos
        - Check that all repos are updated.
        """
        self.info("Update all helm repos.")
        update_msg = self.kube_manager.update_repos()
        self.info("Check that all repos are successfully updated")
        self.assertEqual(update_msg.count("Successfully"), len(self.kube_manager.list_helm_repos()))

    def test_02_add_helm_repo(self):
        """Test case for adding new helm repo.

        **Test Scenario**

        - Deploy VDC
        - Add helm repo
        - Check that the added rebo listed in the helm repos.
        """
        self.info("Add prometheus-community repo")
        repo_name = "prometheus-community"
        repo_url = "https://prometheus-community.github.io/helm-charts"
        self.kube_manager.add_helm_repo(repo_name, repo_url)

        self.info("Check that prometheus-community added")
        added_repo = {"name": repo_name, "url": repo_url}
        self.assertIn(added_repo, self.kube_manager.list_helm_repos())

    def test_03_list_helm_repos(self):
        """Test case for list all helm repos.

        **Test Scenario**

        - Deploy VDC
        - list all helm repos
        - Check that all repos are listed.
        """
        self.info("list all helm Repos")
        all_repos = self.kube_manager.list_helm_repos()
        self.info("Check that helm repo listed")
        self.assertIsNotNone(all_repos)

    def test_04_install_chart(self):
        """Test case for install helm chart.

        **Test Scenario**

        - Deploy VDC
        - Install helm chart
        - Check that chart is installed.
        """
        self.info("Add bitnami repo")
        repo_name = "bitnami"
        repo_url = "https://charts.bitnami.com/bitnami"
        self.kube_manager.add_helm_repo(repo_name, repo_url)
        self.info("Install etcd chart from bitnami repo")
        release_name = "testinstallchart"
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

        - Deploy VDC
        - List all deployed charts
        - Check that all deployed charts are listed.
        """
        self.info("list all deployed charts")
        all_deployed_charts = self.kube_manager.list_deployed_releases()
        self.info("Check that deployed charts listed")
        self.assertIsNotNone(all_deployed_charts)

    def test_06_delete_deployed_chart(self):
        """Test case for delete deployed chart.

        **Test Scenario**

        - Deploy VDC
        - Deploy ETCD chart
        - Check that chart deployed
        - Delete deployed chart
        - List all deployed charts
        - Check that deleted chart not in deployed charts.
        """
        self.info("Deploy ETCD chart")
        release_name = "testdeletechart"
        release_chart = "bitnami/etcd"
        self.kube_manager.install_chart(release_name, release_chart)
        self.info("Check that chart deployed")
        is_installed = False
        for release in self.kube_manager.list_deployed_releases():
            if release["name"] == release_name and release["status"] == "deployed":
                is_installed = True
                break
        self.assertTrue(is_installed, "Failed Because chart not deployed")
        self.info("Delete etcd release that installed before")
        self.kube_manager.delete_deployed_release(release_name)
        self.info("Check if deployed chart deleted")
        deployed_releases = [release["name"] for release in self.kube_manager.list_deployed_releases()]
        self.assertNotIn(release_name, deployed_releases)

    def test_07_is_helm_installed(self):
        """Test case to check if helm installed.

        **Test Scenario**

        - Deploy VDC
        - Check is_helm_installed against process.is_installed.
        """
        self.info("Get is_helm_installed result")
        is_helm_installed_function = j.sals.kubernetes.manager.is_helm_installed()
        process_is_installed = j.sals.process.is_installed("helm")
        self.assertEqual(is_helm_installed_function, process_is_installed)

    def test_08_execute_native_cmd(self):
        """Test case for executing a native kubernetes commands.

        **Test Scenario**

        - Deploy VDC
        - Excute kubernetes command
        - Check that the command executed correctly.
        """

        self.info("Execute kubectl get nodes")
        cmd_out = self.kube_manager.execute_native_cmd("kubectl get nodes")
        self.info("Check if command executed correctly")
        self.assertEqual(cmd_out.count("master"), 1)
        self.assertGreaterEqual(cmd_out.count("Ready"), 1)
