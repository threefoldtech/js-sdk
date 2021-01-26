import pytest
import yaml
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

    def setUp(self):
        super().setUp()
        self.release_name = ""

    def tearDown(self):
        if self.release_name:
            self.info(f"Delete {self.release_name}")
            self.kube_manager.delete_deployed_release(self.release_name)

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
        - Check that the added repo listed in the helm repos.
        """
        self.info("Add prometheus-community repo")
        repo_name = "prometheus-community"
        repo_url = "https://prometheus-community.github.io/helm-charts"
        self.kube_manager.add_helm_repo(repo_name, repo_url)

        self.info("Check that prometheus-community added")
        added_repo = {"name": repo_name, "url": repo_url}
        self.assertIn(added_repo, self.kube_manager.list_helm_repos())

    def test_03_install_chart(self):
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
        self.release_name = "testinstallchart"
        self.release_chart = "bitnami/etcd"
        self.kube_manager.install_chart(self.release_name, self.release_chart)

        self.info("Check if chart installed")
        is_installed = False
        for release in self.kube_manager.list_deployed_releases():
            if release["name"] == self.release_name and release["status"] == "deployed":
                is_installed = True
                break
        self.assertTrue(is_installed)

    def test_04_delete_deployed_chart(self):
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
        self.release_name = "testdeletechart"
        self.release_chart = "bitnami/etcd"
        self.kube_manager.install_chart(self.release_name, self.release_chart)

        self.info("Check that chart deployed")
        is_installed = False
        for release in self.kube_manager.list_deployed_releases():
            if release["name"] == self.release_name and release["status"] == "deployed":
                is_installed = True
                break
        self.assertTrue(is_installed, "Failed Because chart not deployed")

        self.info("Delete etcd release that installed before")
        self.kube_manager.delete_deployed_release(self.release_name)

        self.info("Check if deployed chart deleted")
        deployed_releases = [release["name"] for release in self.kube_manager.list_deployed_releases()]
        self.assertNotIn(self.release_name, deployed_releases)
        self.release_name = ""

    def test_05_is_helm_installed(self):
        """Test case to check if helm installed.

        **Test Scenario**

        - Deploy VDC
        - Check is_helm_installed against process.is_installed.
        """
        self.info("Check if helm is installed")
        self.assertEqual(j.sals.kubernetes.manager.is_helm_installed(), j.sals.process.is_installed("helm"))

    def test_06_execute_native_cmd(self):
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

    def test_07_get_helm_chart_user_values(self):
        """Test case for getting the custom user values for helm chart

        **Test Scenario**

        - Deploy VDC
        - Install chart with custom user values
        - Get helm chart user values
        - Check if values are equal
        """
        self.info("Add bitnami repo")
        repo_name = "bitnami"
        repo_url = "https://charts.bitnami.com/bitnami"
        self.kube_manager.add_helm_repo(repo_name, repo_url)

        self.info("Install etcd chart from bitnami repo with custom value")
        self.release_name = "testgetuservalues"
        self.release_chart = "bitnami/etcd"
        input_user_values = {"auth.rbac.enabled": "false"}
        # Modified version of input_user_values as str to be comparable
        input_user_values_str = "auth:rbac:enabled:false"
        self.kube_manager.install_chart(self.release_name, self.release_chart, extra_config=input_user_values)

        self.info("Get user values from get_helm_chart_user_values function")
        func_user_values_str = self.kube_manager.get_helm_chart_user_values(self.release_name)
        # Modify returned value to be comparable
        func_user_values_str = func_user_values_str.replace("{", "").replace("}", "").replace('"', "").replace("\n", "")

        self.info("Check if get user input work correctly")
        self.assertEqual(input_user_values_str, func_user_values_str)

    def test_08_upgrade_release(self):
        """Test case for upgrading helm release

        **Test Scenario**

        - Deploy VDC
        - Install chart
        - Upgrade release
        - Check if release upgraded
        """
        self.info("Add bitnami repo")
        repo_name = "bitnami"
        repo_url = "https://charts.bitnami.com/bitnami"
        self.kube_manager.add_helm_repo(repo_name, repo_url)

        self.info("Install etcd chart from bitnami repo")
        self.release_name = "testupgraderelease"
        self.release_chart = "bitnami/etcd"
        self.kube_manager.install_chart(self.release_name, self.release_chart)

        self.info("Upgrade Release")
        upgrade_status = self.kube_manager.upgrade_release(self.release_name, self.release_chart)

        self.info("Check if release upgraded")
        self.assertTrue(upgrade_status.find(f'Release "{self.release_name}" has been upgraded. Happy Helming!') != -1)

    def test_09_upgrade_release_with_yaml_config(self):
        """Test case for upgrading helm release with given yaml config

        **Test Scenario**

        - Deploy VDC
        - Install chart
        - Upgrade release with a yaml config file
        - Check if release upgraded
        - Check if yaml config updated in the release values
        """
        self.info("Add bitnami repo")
        repo_name = "bitnami"
        repo_url = "https://charts.bitnami.com/bitnami"
        self.kube_manager.add_helm_repo(repo_name, repo_url)

        self.info("Install etcd chart from bitnami repo")
        self.release_name = "testupgradereleasewithyaml"
        self.release_chart = "bitnami/etcd"
        self.kube_manager.install_chart(self.release_name, self.release_chart)

        self.info("Upgrade Release with yaml config")
        yaml_config = yaml.safe_dump({"auth:rbac:enabled": "false"})
        upgrade_status = self.kube_manager.upgrade_release(
            self.release_name, self.release_chart, yaml_config=yaml_config
        )

        self.info("Check if release upgraded")
        self.assertTrue(upgrade_status.find(f'Release "{self.release_name}" has been upgraded. Happy Helming!') != -1)
        input_user_values_str = "auth:rbac:enabled:false"

        self.info("Get current user values")
        func_user_values_str = self.kube_manager.get_helm_chart_user_values(self.release_name)
        # Modify returned value to be comparable
        func_user_values_str = func_user_values_str.replace("{", "").replace("}", "").replace('"', "").replace("\n", "")

        self.info("Check if value in the yaml config update release correctly")
        self.assertEqual(input_user_values_str, func_user_values_str)
