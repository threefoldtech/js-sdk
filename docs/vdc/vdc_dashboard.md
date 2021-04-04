# VDC Deployer

This manual will go through `VDC_dashboard` package and how to add new solution to its maketplace.

- The `VDC dashboard` is the end user interface, in this package the user can interact with his/her VDC Settings and Marketplace.

## The VDC dashboard architecture
```
  ├── chats
  ├── scripts
  ├── bottle
  │   └── deployments.py
  │   └── backup.py
  │   └── models.py
  │   └── vdc_helpers.py
  ├── services
  │   └── domain.py
  │   └── etcd_backup.py
  │   └── k8s_auto_extend.py
  │   └── provisioning_wallet_billing.py
  │   └── s3_auto_topup.py
  │   └── transaction_from_prepain_to_provisioning.py
  │   └── zdb_auto_topup.py
  ├── frontend
  │   └── assets
  │   └── components
  │   └── index.js
  │   └── api.js
  │   └── index.html
  │   └── app.vue
  ├── package.py
  ├── package.toml
  └── __init__.py
  ```
### REST APIs
- There is a [REST Interfaces](./vdc_dashboard_rest_interface.md) that make the user do some actions to control and monitor the VDC.
- Some actions can be applied with the REST APIs like:
  - `Get all VDC info`
  - `Get all worker nodes`
  - `Add new worker node`
  - `Delete existing worker node`
  - `Get all storage nodes`
  - `Add new storage node`
  - `Delete storage node`
  - `Get vdc prepaid wallet info`
  - `Get all used pools`
  - `Get alerts`
### The Package Frontend
- The frontend built with [Vue js](https://vuejs.org/) and use [vuetify js](https://vuetifyjs.com/) some components.

- The VDC Marketplace home page:
  - The user can deploy, list and delete his/her solutions.
![vdc_marketplace](./images/vdc_marketplace.png)

- The VDC setting home page:
  - The default tab represent the `Compute Nodes` for the VDC Kubernetes cluster, The user can Add or remove the nodes.
  ![vdc_setting](./images/vdc_setting.png)
  - In the `Storage Nodes` tab the user can:
    - Add/Delete storage node.
    - Enable quantum storage.
    - Download [Z-stor](https://github.com/threefoldtech/0-stor_v2) configuration.
    - Download ZDBs information.

    ![vdc_storage_nodes](./images/vdc_storage_nodes.png)

  - In Wallet Information tab there is the prepaid wallet information.

    ![vdc_storage_nodes](./images/vdc_wallet.png)

  - In the Backup And Restore tab there is a list of backups and the user can create new and restore any of them.

    ![vdc_storage_nodes](./images/vdc_backup.png)
