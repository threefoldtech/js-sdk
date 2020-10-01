## System requirements for installation on the host

- Ubuntu 18.04 or higher, MacOS 10.9 or higher
- The SDK uses  [python3](python.org), python3-pip, [git](https://git-scm.com), poetry, [nginx](https://www.nginx.com), [redis](https://redis.io), [mkcert](https://github.com/FiloSottile/mkcert) is optionally needed to trust the self signed certificates when used in local development environment.


### Ubuntu

  ```
  apt-get update
  apt-get install -y git python3-venv python3-pip redis-server tmux nginx;
  pip3 install poetry
  ```

### Mac OSX
Install packages (git, nginx, redis-server, tmux, python3) on MacOS
  ```
  brew install nginx redis tmux git python3
  ```


## Installing js-sdk

After preparing the dependencies on your system
### Installation using pip

Just doing `python3 -m pip install js-sdk` is enough

### Installation for experts or developers

This version of the SDK tries to be isolated as possible in case of developers or the endusers, and we are achieving that level of isolation using poetry for the whole development/publishing process

- To install poetry `pip3 install poetry` or from [here](https://python-poetry.org/docs/#installation)
- Clone the repository `git clone https://github.com/threefoldtech/js-sdk`
- Prepare the environment and the python dependencies

  ```bash
  cd js-sdk
  poetry install
  poetry shell
  ```

## Runnning 3Bot

After the installation steps you should have an executable `threebot`

- in case of pip it should be available for the user
- in case of poetry you need to be in the isolated environment using `poetry shell`

threebot server can run using `threebot start --local` starts a server on `8443, 8080`. If you want to use `80, 443` ports you need to set capabilities for nginx binary (in case of linux) or install as root in case of OSX

### Setting capabilities for nginx

```
sudo setcap cap_net_bind_service=+ep `which nginx`
```
to be able to run as a normal user, you don't need it if you are root.

- After that we will just do

  ```bash
  threebot start
  ```

- This will take you to configure your identity, It will ask you about your the network you want to use, 3Bot name, email, and words.

- Then it will start threebot server you will see some thing like that

  ![configure](images/identity_new.png)

- After success you can visit the admin dashboard at http://localhost and start creating reservations

  ![configure](images/success.png)

## Stopping 3Bot
You can stop threebot using `threebot stop`
