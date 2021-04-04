# VDC Deployer

This manual will go through the `VDC_dashboard` package and how to add new solutions to its marketplace.

- The `VDC dashboard` is the end user interface, where the user can interact with their VDC Settings and Marketplace.

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
- [REST Interfaces](./vdc_dashboard_rest_interface.md) are available that allow the user to perform VDC related actions to control and monitor their VDC.
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
- The frontend is built with [Vue js](https://vuejs.org/) using some components from [vuetify js](https://vuetifyjs.com/).

- The VDC Marketplace home page:
  - The user can deploy, list, and delete their solutions.
![vdc_marketplace](./images/vdc_marketplace.png)

- The VDC setting home page:
  - `Compute Nodes tab` is the default tab for the VDC Kubernetes cluster, where the user can add or remove their VDC's nodes.
  ![vdc_setting](./images/vdc_setting.png)
  - In the `Storage Nodes` tab the user can:
    - Add/Delete storage nodes.
    - Enable quantum storage.
    - Download [Z-stor](https://github.com/threefoldtech/0-stor_v2) configuration.
    - Download ZDBs information.

    ![vdc_storage_nodes](./images/vdc_storage_nodes.png)

  - `Wallet Information tab`: consists of the prepaid wallet information.

    ![vdc_storage_nodes](./images/vdc_wallet.png)

  - `Backup And Restore tab`: consists of a list of backups. It also enables the user to create new ones or restore any of the previously backed up ones.

    ![vdc_storage_nodes](./images/vdc_backup.png)
