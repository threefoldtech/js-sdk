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
        system_packages_list = packages.system_packages()

        self.info("Check the system packages list")
        default_packages_list = ["auth", "chatflows", "admin", "weblibs", "tfgrid_solutions", "backup"]
        self.assertEqual(default_packages_list, list(system_packages_list.keys()), "not all default packages exist")

    def test02_add_install_delete_package(self):
        """
        Test case for adding a package and deleting it.
        **Test Scenario**
        - Add a package.
        - Check that the package has been installed correctly.
        - Install another package.
        - Check that the package has been installed correctly.
        - Delete the two packages.
        - Check that the packages have been deleted successfully.
        """

        packages = Packages(self.driver)
        packages.load()

        self.info("Add a package")
        git_url = "https://github.com/threefoldtech/js-sdk/tree/development/jumpscale/packages/notebooks"
        packages.add_package(git_url)

        self.info("Check that the package has been Added correctly")
        installed_packages, available_packages = packages.check_package_card()
        self.assertIn("notebooks", installed_packages.keys())

        self.info("Install another package")
        installed_package = packages.install_package()

        self.info("Check that the package has been installed correctly")
        installed_packages, available_packages = packages.check_package_card()
        self.assertIn(installed_package, installed_packages.keys())

        self.info("Delete the two packages")
        packages.delete_package("notebooks")
        packages.delete_package(installed_package)

        self.info("Check that the packages have been deleted successfully")
        installed_packages, available_packages = packages.check_package_card()
        self.assertIn("notebooks" and installed_package, available_packages.keys())

    def test03_open_in_browser(self):
        """
        Test case for testing open in browser button.
        **Test Scenario**
        - Check if threebot deployer package is installed ot not, If not install it.
        - Press open in browser button.
        - Check the current URL.
        """
        packages = Packages(self.driver)
        packages.load()

        self.info("Press open in browser button")
        current_url = packages.open_in_browser()

        self.assertEqual(current_url, "https://localhost/threebot_deployer/#/")

    def test04_chatflows(self):
        """
        Test case for testing chatflow window.
        **Test Scenario**
        - Check if threebot deployer package is installed ot not, If not install it.
        - Press chatflows button.
        - Check that the chatflow pop-up window appears.
        """
        packages = Packages(self.driver)
        packages.load()

        cards_name = packages.chatflows()
        self.info("Press chatflows button")
        self.info("Check that the chatflow pop-up window appears")
        self.assertIn("Chatflows", cards_name)
