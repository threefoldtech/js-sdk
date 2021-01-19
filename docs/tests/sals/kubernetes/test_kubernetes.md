### test_01_update_helm_repos

Test case for updating helm repos.

**Test Scenario**

- Deploy VDC
- Update helm repos
- Check that all repos are updated.

### test_02_add_helm_repo

Test case for adding new helm repo.

**Test Scenario**

- Deploy VDC
- Add helm repo
- Check that the added rebo listed in the helm repos.

### test_03_list_helm_repos

Test case for list all helm repos.

**Test Scenario**

- Deploy VDC
- list all helm repos
- Check that all repos are listed.

### test_04_install_chart

Test case for install helm chart.

**Test Scenario**

- Deploy VDC
- Install helm chart
- Check that chart is installed.

### test_05_list_deployed_charts

Test case for listing all deployed charts.

**Test Scenario**

- Deploy VDC
- List all deployed charts
- Check that all deployed charts are listed.

### test_06_delete_deployed_chart

Test case for delete deployed chart.

**Test Scenario**

- Deploy VDC
- Deploy ETCD chart
- Check that chart deployed
- Delete deployed chart
- List all deployed charts
- Check that deleted chart not in deployed charts.

### test_07_is_helm_installed

Test case to check if helm installed.

**Test Scenario**

- Deploy VDC
- Check is_helm_installed against process.is_installed.

### test_08_execute_native_cmd

Test case for executing a native kubernetes commands.

**Test Scenario**

- Deploy VDC
- Excute kubernetes command
- Check that the command executed correctly.
