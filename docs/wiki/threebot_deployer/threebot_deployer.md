# Threebot Deployer Package

## Overview

Threebot Deployer package is created to offer a centralized place where end-users can deploy their own 3Bot. All the user needs is to have Threefold Connect ([Android](https://play.google.com/store/apps/details?id=org.jimber.threebotlogin&hl=en)/[IOS](https://apps.apple.com/us/app/3bot-connect/id1459845885)) app installed on his mobile device with logged in user.

### Components

Deployer Infrastructure requires three machines. One machine has `js-sdk` installed with `3Bot` server to run the threebot deployer package (3bot server running as root with no --local) and two machines used for backup.

### Configuration

- Domain:

    Threebot Deployer package can be accessed through it's url `https://localhost/threebot_deployer/#/` if running locally. But it is intended to be run on a public server where anyone can use it to deploy so, it uses `certbot` to configure a certificate for the domain specified in `package.toml` which is by default `deploy3bot.grid.tf`

    ```toml
    [[servers]]
    name = "threebot_deployer_root_proxy"
    domain = "deploy3bot.grid.tf"
    letsencryptemail = "rana@incubaid.com"
    includes = ["default_443.chatflows_*", "default_443.auth_*", "default_443.threebot_deployer*"]

    ```

- Identity:

    Threebot Deploy uses the default identity on the server to deploy workloads on the grid. the deployed workloads are associated with the logged-in user by injecting the `owner` in the metadata of all workloads except for pools. Pools association with their owners is done by storing these pools using the config manager.

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
    note: make sure to use different identities for the server if you deploy separate machines using the same explorer.

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
    Threebot Deploy uses two separate servers for 3Bot backups which can be deployed as below

    1- Create 2 ubuntu 18.04 machines then download and run the configuration script on both machines

    ```bash
    # download the backup script from github (the branch may change)
    wget https://raw.githubusercontent.com/threefoldtech/js-sdk/development/jumpscale/packages/threebot_deployer/scripts/backup.sh
    # or copy the script from your threebot_deployer server from package path jumpscale/packages/threebot_deployer/scripts/backup.sh to both backup servers
    # then run the script
    bash backup.sh
    ```

    2- Add the ssh-key of root user of the threebot deploy to authorized keys in both servers.

    3- Configure ssh clients on threebot deploy machine's `jsng` shell

    ```python
    JS-NG> BACKUP_SERVER1 = "backup_server1"
    JS-NG> BACKUP_SERVER2 = "backup_server2"
    JS-NG> ssh_key = j.clients.sshkey.new("threebot_deploy")
    JS-NG> ssh_key.private_key_path = "/root/.ssh/id_rsa"
    JS-NG> ssh_key.save()
    JS-NG> ssh_server1 = j.clients.sshclient.get(BACKUP_SERVER1)
    JS-NG> ssh_server2 = j.clients.sshclient.get(BACKUP_SERVER2)
    JS-NG> ssh_server1.host = IP_SERVER1
    JS-NG> ssh_server2.host = IP_SERVER2
    JS-NG> ssh_server1.sshkey = ssh_key.instance_name
    JS-NG> ssh_server2.sshkey = ssh_key.instance_name
    JS-NG> ssh_server1.save()
    JS-NG> ssh_server2.save()
    ```

### Installation

Threebot Deploy package is installed normally like any other package using the admin dashboard or from `jsng` shell using the package path as below:

```python
server = j.servers.threebot.get("default")
server.packages.add("/root/js-sdk/jumpscale/packages/threebot_deployer/", channel_type="redis", channel_host="<remoteRedisHostIP>", channel_port=<remoteHostRedisPort>)
server.save()
server.start()
```

Now you can start your `3Bot` server and access threebot deploy dashboard on `/threebot_deployer`

## Notes

- channel_type, channel_host, channel_port are for streaming logs to a redis instance, these are need to be a public machine and run a redis server on it using non-protected mode `redis-server --port 6378 --protected-mode no`
- You can access that logs further using:

```
redis-cli -h <remoteRedisHostIP> -p <remoteHostRedisPort>
SUBSCRIBE <solution_name>-stdout <solution_name>-stderr
```
