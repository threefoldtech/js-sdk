### test01_system_packages


Test case for checking system packages list.
**Test Scenario**
- Check the system packages list.
the package list that should be started by default with threebot server.
['auth', 'chatflows', 'admin', 'weblibs', 'tfgrid_solutions', 'backup']

### test02_add_install_delete_package


Test case for adding a package and deleting it.
**Test Scenario**
- Add a package using GitURL.
- Check that the package has been installed correctly.
- Add a package using path.
- Check that the package has been installed correctly.
- Install another package.
- Check that the package has been installed correctly.
- Delete the three packages.
- Check that the packages have been deleted successfully.

### test03_open_in_browser


Test case for testing open in browser button.
**Test Scenario**
- Check if threebot deployer package is installed ot not, If not install it.
- Press open in browser button.
- Check the current URL.

### test04_chatflows


Test case for testing chatflow window.
**Test Scenario**
- Check if threebot deployer package is installed ot not, If not install it.
- Press chatflows button.
- Check that the chatflow pop-up window appears.
