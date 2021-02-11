### test01_load_info

Test case for loading info.

**Test Scenario**

- Deploy VDC.
- Get VDC by j.sals.vdc
- Check that VDC should be empty.
- Load info.
- Check that kubernetes node should be filled.

### test02_list_vdcs

Test case for listing deployed vdcs.

**Test Scenario**

- Deploy VDC.
- List deployed vdcs.
- Check that the vdc has been deployed is in the list.

### test03_calculate_expiration_value

Test case for checking the expiration value.

**Test Scenario**

- Deploy VDC.
- Get the expiration value.
- Check expiration value after one hour.

### test04_is_empty

Test case for checking that deployed vdc is not empty.

**Test Scenario**

- Deploy VDC.
- Check that the deployed vdc not empty.

### test05_find_vdc

Test case for find vdc.

**Test Scenario**

- Deploy VDC.
- Try to find this vdc

### test06_add_delete_k8s_node

Test case for adding and deleting node.

**Test Scenario**

- Deploy VDC.
- Calculate the price of added zdb and fund the provisioning wallet.
- Add kubernetes node.
- Check that the node has been added.
- Delete this node.
- Check that this node has been deleted.

### test07_apply_grace_period_action

Test case for applying and reverting grace period action.

**Test Scenario**

- Deploy VDC.
- Apply grace period action.
- Check that k8s hasn't been reachable.
- Revert grace period action.
- Check that k8s has been reachable.

### test08_renew_plan

Test case for renewing the plan.

**Test Scenario**

- Deploy VDC.
- Get the expiration date
- Renew plan with one day.
- Check that the expiration value has been changed.

### test09_transfer_to_provisioning_wallet

Test case for transfer TFT to provisioning wallet.

**Test Scenario**

- Deploy VDC.
- Get wallet balance.
- Transfer TFT to provisioning wallet.
- Check that the wallet balance has been changed.

### test10_extend_zdb

Test case for extending zdbs.

**Test Scenario**

- Deploy VDC.
- Get the zdbs total size.
- Calculate the price of added zdb and fund the provisioning wallet.
- Extend zdbs.
- Check that zdbs has been extended.
