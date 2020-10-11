#### test01_start_threebot
Test start threebot server.

**Test Scenario**
- Start threebot server.
- Check it works correctly.
#### test02_stop_threebot
Test stop threebot server.

**Test Scenario**
- Start threebot server.
- Check it works correctly.
- Stop threebot server.
- Check it stopped correctly.
#### test03_is_running
Test is_running method.

**Test Scenario**
- Start threebot server.
- Check it works correctly.
- Use is_running, The output should be True.
- Stop threebot server.
- Check it stopped correctly.
- Use is_running, The output should be False.
#### test04_check_default_package_list
Test default package list with threebot server.

**Test Scenario**
- Start threebot server.
- Check the package list that should be started by default with threebot server.
['auth', 'chatflows', 'admin', 'weblibs', 'tfgrid_solutions', 'backup']
#### test05_package_add_and_delete
Test case for adding and deleting package in threebot server

**Test Scenario**
- Add a package.
- Check that the package has been added.
- Try to add wrong package, and make sure that the error has been raised.
- Delete a package.
- Check that the package is deleted correctly.
- Try to delete non exists package, and make sure that the error has been raised.
