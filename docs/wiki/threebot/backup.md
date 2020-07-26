# Threebot backup

Backing up Threebot ensusres the safety of the user's data and to allow a threebot user to restore his data.

This is achieved by backing the user's config directory which contains the following:

- His jumpscale config file
- His secure config directory containning all his sensitive data(clients/wallets/..)
- His encryption keys used to ecrypt his secure data
- His jumpscale/sdk containers data

[Restic](https://restic.readthedocs.io/en/latest/) is used to allow for fast and secure backing of the data.

Below we discuss the process of backing up:

## Marketplace backups

The official and recommended method of backing up is by using the marketplace to orchestrate backups. Especially when using theebot online accounts.

Two backup servers are used as backends for the backups, eliminating the need for the user to setup his own backend.

### Backup flow

Threebot server is loaded by default with the `backup` package which exposes a marketplace actor that handles the initial start of the backup procedure by contacting the marketplace server. Once that is done the threebot server will communicate directly with the two backup servers.

- Procedure is started by the user calling init with his secret which will be used for backup authentication and encryption
- Marketplace will reply with the two servers addresses and authorize the threebot user to connect to the backup servers
- Marketplace backup actor will save the data necessary to backup the data
- User triggers a backup/auto backup and the actor will perform the backup against the two servers

### Marketplace backup actor

The actor is responsible for all backup operations:

#### Init

The init endpoint needs to be called before any backup operations can be performed. It is necessary for getting the central backup servers addresses and allowing the user to use them as backends.

It sends both the username and the password needed for backup operations. The password is encrypted using public key encryption with the public key of the marketplace server. The marketplace server can be specified by setting the `MARKETPLACE_URL` environment variable.

After receiving the servers addresses it creates two instance of the `restic` tool and saves them to be used in the backup calls and operations.

#### Backup

Backup takes a snaphot of the current config directory and saves it in the two servers.

An epoch timestamp is added by default as a tag. This timestamp is used as identification of the snapshot between the two servers.

User specified tags can be added as well as comma seperated string.

#### Auto backup

This ensures that a backup is taken of the config directory every day at midnight. This is done by creating a cron job that handles the backup as well as cleaning up old ones. Timestamp is added as a tag as well for identification between the two servers.

Auto backup can be disables at any point by calling the `disable_auto_backup` actor method.

#### Listing snapshots

Listing snpashots is done by getting the snapshots of each server and ensuring that they have the same snapshots by checking the timestamp in the tags.

#### Restore

Restore will get the latest snaphot taken(or latest with specified tags) and restore it on the system.

This is typically used when using an already created user and wanting to restore his data. The user will need to know the secret to be able to get the stored data.

### Marketplace server

The marketplace server exposes an endpoint to initialize the backup. The server has access to the two backup servers and upon receiving the request it will do one of the following:

- If user already created(Check restore) it will verify the credentials and if correct will send the servers addresses
- Otherwise will create an entry for the user in the two servers and respond with the addresses

The endpoint will get the user's publick key from the explorer to decrypt the password.

### Backup servers

The two servers use [rest-server](https://github.com/restic/rest-server) to manage the backup data.

Access to this server is protected and the user needs to use http authentication to be able to access/backup his data.

The password is specified by the user during the initialization of the backup and the username is the threebot name.

## Minio backups

Using Minio as backend for the backup is supported although the setup of the minio server is left to the user.

Once the server is setup the user needs to specify the following:

- Server url
- secret to encrypt the restic repo
- access key and secret key to access the minio server

Everything is described above in regards to the marketplace backup actor is supported by the minio actor including having to call the `init` before any backup operations.
