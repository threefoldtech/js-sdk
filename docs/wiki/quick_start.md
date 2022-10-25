# Quick Start with js-sdk

## System requirements for installation on the host

- Ubuntu 18.04 or higher, macOS 10.15 catalina or higher
- Windows 10, version 2004 can run using [wsl2](https://docs.microsoft.com/en-us/windows/wsl/wsl2-index) using ubuntu 20.04 or later
- The SDK uses  [python3](python.org), python3-pip, [git](https://git-scm.com), poetry, [nginx](https://www.nginx.com), [redis](https://redis.io), [mkcert](https://github.com/FiloSottile/mkcert) is needed to trust the self signed certificates when used in local development environment.
- Browser (we recommend using Google chrome)

### macOS

- Install packages (git, nginx, redis-server, tmux, python3) on MacOS

  ```bash
  brew install nginx redis tmux git python3
  ```


### Ubuntu

- For GNU/Linux Ubuntu systems

  ```bash
  apt-get update
  apt-get install -y git python3-venv python3-pip redis-server tmux nginx
  pip3 install poetry
  ```

## Installing js-sdk

After having the [requirements](https://github.com/threefoldtech/js-sdk/blob/development/docs/wiki/quick_start.md#system-requirements-for-installation-on-the-host) installed on your system

### Installation using pip (don't use yet until we have an official release)

Just doing `python3 -m pip install js-sdk` is enough

### Installation for experts or developers

- Make sure to have the [requirements](https://github.com/threefoldtech/js-sdk/blob/development/docs/wiki/quick_start.md#system-requirements-for-installation-on-the-host) installed
This version of the SDK tries to be isolated as possible in case of developers or the end users, and we are achieving that level of isolation using poetry for the whole development/publishing process

- To install poetry `pip3 install poetry` or from [here](https://python-poetry.org/docs/#installation)
- Clone the repository `git clone https://github.com/threefoldtech/js-sdk`
- Prepare the environment and the python dependencies

  ```bash
  cd js-sdk
  poetry install
  poetry shell
  ```

## Running the Threebot

### using mkcert

[mkcert](https://github.com/FiloSottile/mkcert) is optionally needed to trust the self signed certificates when used in local development environment. All you need to do is install it in your system under the name `mkcert` and do `mkcert -install`

After the installation steps you should have an executable `threebot`

- in case of pip it should be available for the user
- in case of poetry you need to be in the isolated environment using `poetry shell`

threebot server can run using `threebot start --local` starts a server on `8443, 8080`. If you want to use `80, 443` ports you need to set [capabilities](running3bot.md) for nginx binary (in case of linux) or install as root in case of OSX

  ```bash
  threebot start --local
  ```

- This will take you to configure your identity, It will ask you about your the network you want to use, 3Bot name, email, and words.

- Then it will start threebot server you will see some thing like that

  ![configure](images/identity_new.png)

- After success you can visit the admin dashboard at http://localhost:8080 or https://localhost:8443  and start creating reservations

  ![configure](images/success.png)

## Access admin panel

Now the admin panel should available on the host and can be accessed through `<HOST>/admin` where you will be redirected to 3bot login. The admin panel ha many functionalities but our main usage in this tutorial will be to deploy an ubuntu container using its chatflow.
Note: if you started threebot server with `--local` option, then the admin can be accessed with `https://localhost:8443/admin/`

## Create a new wallet

First we need to setup the payment method which is the wallet we will use to pay for the deployment machine. This can be done through the admin under `Wallet manager`.

![solutions menu](images/wallet_manager.png)

One of the following can be done:

- **Create a new wallet**: You can create a new wallet by clicking on the `create wallet` button then entering the name of the wallet to be created. Make sure you save the secret of the wallet created to be able get the wallet incase it was lost. Transfer the amount of tokens you need to your wallet to have enough funds for the deployment.
![Create wallet](images/create_wallet.png)

- **Import an existing wallet**:If you already have a stellar wallet then you can simply import it by clicking on `import wallet` then entering the wallet name and secret.
![Import wallet](images/import_wallet.png)

Now that the wallet is setup, you are ready for your first deployment.

## Adding tokens to a stellar wallet

To know how to obtain tokens [see here](https://sdk.threefold.io/#/sdk__mainnet_gettft)
