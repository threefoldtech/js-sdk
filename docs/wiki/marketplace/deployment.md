# MarketPlace Package

## Overview

Marketplace package is created to offer a centralized place where end-users can deploy different types of solutions without needing to have an idnetity registered in the explorer or even have a 3bot running. All the user needs is to have 3Bot Connect ([Android](https://play.google.com/store/apps/details?id=org.jimber.threebotlogin&hl=en)/[IOS](https://apps.apple.com/us/app/3bot-connect/id1459845885)) app installed on his mobile device with logged in user.

### Installation

Marketplace package is installed normally like any other package using the admin dashboard or from `jsng` shell using the package path as below:

```python
j.servers.threebot.default.packages.add("/root/js-sdk/jumpscale/packages/marketplace/")
j.servers.threebot.default.save()
```

### Configuration

- Domain:

    Marketplace package can be accessed through it's url `https://localhost/marketplace/#/` if running locally. But it is intended to be run on a public server where anyone can use it to deploy so, it uses `certbot` to configure a certificate for the domain specified in `package.toml` which is by default `marketplace.grid.tf`

    ```toml
    [[servers]]
    name = "marketplace_root_proxy"
    domain = "marketplace.grid.tf"
    letsencryptemail = "motaweam@incubaid.com"
    includes = ["default_443.chatflows_*", "default_443.auth_*", "default_443.marketplace*"]

    ```

- Identity:

    Marketplace uses the default identity on the server to deploy workloads on the grid. the deployed workloads are associated with the logged-in user by injecting the `owner` in the metadata of all workloads except for pools. Pools association with their owners is done by storing these pools using the config manager.

    ```python
    JS-NG> from jumpscale.sals.marketplace.models import UserPool
    JS-NG>
    JS-NG> from jumpscale.core.base import StoredFactory
    JS-NG> factory = StoredFactory(UserPool)
    JS-NG> factory.list_all()
    {'pool_magidentfinal_393', 'pool_magidentfinal_228', 'pool_magidentfinal_242', 'pool_magidentfinal_231'}
    JS-NG>
    ```

    which means pools are not synced across different machines by default.
    note: make sure to use different idnetities for the server if you deploy separate machines using the same explorer.

- Over Provisioning:

    When searching for a node to deploy on, the chatflow searches by the required resources and selects one of them. this works ok on mainnet where there are plenty of resources but on testnet where resources are limited you may not be able to find enough reosurces (CPU and Memeory) so you can over provision CPU and Memeory. This can be enabled globally by setting the below config key

    ```python
    JS-NG> j.config.set("OVER_PROVISIONING", True)
    ```

- Test Certificates:

    Our solutions that expose their addresses over public domain names with certificates generated using `certbot` which have a limit of ~50 domains per week. to avoid reaching that limit when testing or staging deployments we set the below configuration to use letsencrypt staging certificates

    ```python
    JS-NG> j.config.set("TEST_CERT", True)
    ```

- Backup Servers:
    Marketplace uses two separate servers for 3Bot backups.

    1- Configure both servers by running the below script

    ```bash
    bash /sandbox/code/github/threefoldtech/js-sdk/jumpscale/packages/marketplace/scripts/backup.sh
    ```

    2- Add the ssh-key of the marketplace in two servers.

    3- Configure ssh clients on marketplace machine's `jsng` shell

    ```python
    JS-NG> BACKUP_SERVER1 = "backup_server1"
    JS-NG> BACKUP_SERVER2 = "backup_server2"
    JS-NG> ssh_server1 = j.clients.sshclient.get(BACKUP_SERVER1)
    JS-NG> ssh_server2 = j.clients.sshclient.get(BACKUP_SERVER2)
    JS-NG> ssh_server1.host = IP_SERVER1
    JS-NG> ssh_server2.host = IP_SERVER2
    JS-NG> ssh_server1.save()
    JS-NG> ssh_server2.save()
    ```

now you can start your `3Bot` server and access marketplace dashboard on `/marketplace`
