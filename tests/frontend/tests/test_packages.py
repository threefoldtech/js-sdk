import pytest
from tests.frontend.pages.Packages.packages import Packages
from tests.frontend.tests.base_tests import BaseTest

from gevent import monkey

monkey.patch_all(subprocess=False)


@pytest.mark.integration
class PackagesTests(BaseTest):
    def test01_system_packages(self):
        """
        Test case for checking system packages list.
        **Test Scenario**
        - Check the system packages list.
          the package list that should be started by default with threebot server.
          ['auth', 'chatflows', 'admin', 'weblibs', 'tfgrid_solutions', 'backup']
        """

        packages = Packages(self.driver)
        packages.load()
        packages_list = packages.system_packages()

        self.info("Check the system packages list")
        default_packages_list = ["auth", "chatflows", "admin", "weblibs", "tfgrid_solutions", "backup"]
        self.assertTrue(set(default_packages_list).issubset(packages_list), "not all default packages exist")

    def test02_add_delete_package(self):
        """
        Test case for installing a package and deleting it.
        **Test Scenario**
        - Install a package.
        - Check that the package has been installed correctly.
        - Delete the package.
        - Check that the package has been deleted successfully.
        """

        self.info("Install a package")
        packages = Packages(self.driver)
        packages.load()
        git_url = "https://github.com/threefoldtech/js-sdk/tree/development/jumpscale/packages/notebooks"
        packages.add_package(git_url)

        self.info("Check that the package has been installed correctly")
        installed_packages, available_packages = packages.check_package_card()
        self.assertIn("notebooks", installed_packages.keys())

        print(installed_packages, available_packages)
        self.info("Delete the package")
        packages.delete_package("notebooks")

        self.info("Check that the package has been deleted successfully")
        installed_packages, available_packages = packages.check_package_card()
        self.assertIn("notebooks", available_packages.keys())
