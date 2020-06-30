## Requirements for insystem installation

- Ubuntu 18.04 or later, MacOS 10.9 or more
- packages [python3, python3-pip, git, poetry, nginx, redis]

- Install packages on Ubuntu

  These are for certbot:
  ```bash
  apt-get install -y software-properties-common;
  add-apt-repository universe;
  add-apt-repository ppa:certbot/certbot;
  ```

  Then:
  ```bash
  apt-get update
  apt-get install -y git python3-venv python3-pip redis-server tmux;
  apt-get install -y nginx certbot python-certbot-nginx;
  pip3 install poetry
  ```

- Install packages on MacOS
  - nginx [here](https://www.javatpoint.com/installing-nginx-on-mac)
  - certbot `brew install certbot`
  - redis-server [here](https://medium.com/@petehouston/install-and-config-redis-on-mac-os-x-via-homebrew-eb8df9a4f298)
  - git from [here](https://www.atlassian.com/git/tutorials/install-git)
  - python3 [here](https://docs.python-guide.org/starting/install3/osx/)
  - tmux `brew install tmux`

## Installation in system (Experts)
(note: for mac OSX use root user during installation to be able to use ports (80, 443) `sudo su -`)
- Clone the repository `git clone https://github.com/threefoldtech/js-sdk`
- Install the js-ng

  ```bash
  cd js-sdk
  poetry update
  poetry install
  poetry shell
  ```


- Make sure to setcap for nginx (for linux only)
```
sudo setcap cap_net_bind_service=+ep `which nginx`
```
to be able to run as a normal user, you don't need it if you are root.

- After that we will just do

  ```bash
  threebot start
  ```

- This will take you to configure your identity, It will ask you about your the network you want to use, 3bot name, email, and words.

- Then it will start threebot server you will see some thing like that

  ![configure](images/identity_new.png)

- After success you can visit the admin dashboard at http://localhost and start creating reservations

  ![configure](images/success.png)
