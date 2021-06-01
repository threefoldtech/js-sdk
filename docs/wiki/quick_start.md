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

## Create a reservation via jsng Shell (without admin panel)

See [here](https://github.com/threefoldtech/js-sdk/blob/30fbc245e22030e5b3fc1a393a9ae2a838d78c22/docs/wiki/tutorials/deploy_ubuntu_container.md)

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

## Create your Capacity pool

Before we get to deploying the actual Ubuntu container, we need to create a capacity pool which will be used by any solutions deployed.

First step is to choose whether you want to create a new pool or extend an existing one.

![](images/pool1.png)

How much cu units(cpu/memory) and su units(storage) your pool needs and the type of token you will pay with.

![](images/pool2.png)

Choose the farm for your pool

![](images/pool3.png)

Pay using your stellar wallet or scan the QR code using 3bot staging application

![](images/pool4.png)
![](images/pool5.png)
![](images/pool6.png)

## Deploy your private overlay network

Before we get to deploy the actual Ubuntu container, we first need to create a private overlay network.

The technology used to implement the network overlay is [Wireguard](https://www.Wireguard.com/). Make sure you have installed Wireguard on your device to able to continue: [Wireguard installation](https://www.wireguard.com/install/)

For this tutorial we will use the network wizard that will guide us through the creation of your network.

To start the wizard click the left menu on Solutions then Network then Create new

![solutions menu](images/solutions_list.png)

First step is to choose whether you want to create a new network or add access to a specific node.

![choose network name](images/network1.png)

Choose the name of your network. This name is only used to identify the network later on when deploying workloads.

![choose network name](images/network2.png)

The nodes running on the TFGrid all communicate over IPv6. While this is very convenient for the nodes, not everyone has access to IPv6 already. For this reason we allow people to configure `endpoint` using IPv4 address.

This step lets you choose between IPv6 or IPv4 for your `endpoint`. If you are not sure what to choose, pick IPv4.

![](images/network3.png)

This step is there to let you configure the subnet used by your network. To make it easy here we just let the wizard pick one for us.

![choose network subnet](images/network4.png)

Last step shows you the configuration you need to download in order to configure your device. Just click the download button and save the configuration locally and configure you device.

Depending on your platform the configuration of Wireguard can look a bit different. But all the information required is shown in the configuration you have downloaded.

![Step6](images/network6.png)


On Linux system, you can just use the `wg-quick` command directly with the file sent from the chatflow, like so:

```bash
wg-quick up my_first_network.conf
```
![Step6](images/network7.png)

![Step6](images/network7.png)

## Deploy an Ubuntu container and connect to it

Now that you have a network in place. We can deploy containers and connect it to the network. To do so we will use the Ubuntu Chat flow

To start the wizard click the left menu on Solutions then Ubuntu, then Create new

![Solutions menu](images/solutions_list.png)


1. First enter a name to give your Ubuntu solution. This will be used locally to save the details of the deployment.

    ![Solution name](images/ubuntu1.png)

2. Next choose the version of Ubuntu on you want. We currently support versions 18.04 and 16.04
    ![Ubuntu version](images/ubuntu2.png)

3. Then choose how much CPU and Memory resources you want allocated for the container
    ![Container resources](images/ubuntu3.png)

4. Then select your pool you want for your container
    ![pool](images/ubuntu4.png)

5. Choose the network on which you want to deploy your Ubuntu container. Use the same name you entered previously when creating the network
    ![network](images/ubuntu5.png)

4. Then select your pool you want for your container
    ![pool](images/ubuntu4.png)

5. Choose the network on which you want to deploy your Ubuntu container. Use the same name you entered previously when creating the network
    ![network](images/ubuntu5.png)

5. The next step includes the possibility to stream the container's logs to a redis channel. In our simple deployment we will not need it so you can simply choose No
    ![container_logs](images/ubuntu6.png)

6. In order to access this container after it is deployed, you will need to upload your public ssh key. Usually your public and private ssh key pairs are found in `~/.ssh` where the public key ends in `.pub`

    ![SSH key](images/ubuntu7.png)

7. You can now choose an IP address that will be given to your Ubuntu container in your network. This is the IP address you will be using to access the container.

    ![ip_Address](images/ubuntu10.png)

8. Then if you want access your container through IPV6 .

    ![ipv6](images/ubuntu11.png)

9. Then read carefully the options you selected previously until this point in the chatflow and confirm them by clicking next to proceed.

    ![Overview](images/ubuntu13.png)

10. Once the amount is available in the wallet and the payment is successfully completed, the deployment process is continued. After the deployment is successful which may take a couple of minutes sometimes, the following message is shown with details regarding the reservation id which is a unique id used for your specific container deployment. It also views the IP address that is to be used to connect to the container.

    ![Deployment Success](images/ubuntu16.png)

11. You can now simply access the deployed Ubuntu container by the following command

    ```bash
    ssh root@IP_ADDRESS
    ```

    where the IP address is the one you chose in the chatflow earlier and is shown in the previous success message.


### Troubleshooting

- For macOS chrome may complain about self-signed certificate. In terminal execute the following

  ```
  open -n -a /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --args --user-data-dir="/tmp/chrome_dev_test" --disable-web-security --ignore-certificate-errors
  ```

- Data is stored in `~/.config/jumpscale/secureconfig/jumpscale`. if you want to start over, you can remove that directory using `rm ~/.config/jumpscale/secureconfig/jumpscale`
- There're also some configurations that gets generated e.g (nginx configurations), logs and binaries when copied in `~/sandbox` directory
