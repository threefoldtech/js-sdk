# Threebot Server

Threebot server is an application server based on nginx and gedis. It can further be extended using packages.

When adding packages to a server, they should first be defined, then added to the threebot server then the server can be started.


Content:

- [Threebot Server](#threebot-server)
  - [Staring threebot](#staring-threebot)
    - [Using threebot command](#using-threebot-command)
    - [Manual start](#manual-start)
    - [Nginx and privileged ports](#nginx-and-privileged-ports)
  - [Packages](#packages)
    - [Structure](#structure)
      - [Mandatory components](#mandatory-components)
      - [Optional components](#optional-components)
    - [Configuration](#configuration)
      - [Servers](#servers)
    - [More about packages](#more-about-packages)
    - [Adding new packages](#adding-new-packages)
  - [ssl](#ssl)

## Staring threebot

### Using threebot command
`threebot` command can be used to start/stop threebot and to check for current running threebot status.

It can be used without any options to start a threebot server on standard ports (http and https).

```
threebot
```

In case you need to start a local threebot, ny passing `--local` option will, it will search for free port on `80xx` range and starts threebot on this port.

```
threebot --local
```

### Manual start

Start threebot server from `jsng` shell:

```python
jsng

JS-NG> threebot_server = j.servers.threebot.get(domain="<optional><your-threebotdomain>", email="<your email><required if you want to use domain and ssl for certbot>")
JS-NG> threebot_server.save()
JS-NG> threebot_server.start()
```

It should start nginx for you too, if it's not stared, you can start it manually:

```
sudo nginx -c ~/sandbox/cfg/nginx/main/nginx.conf
```

### Nginx and privileged ports

Most of the times, you'll need to allow nginx to listen on privileged ports (80 and 443):

To increase its capabilities to be able to use port 80 and 443, using this command:

```bash
sudo setcap cap_net_bind_service=+ep `which nginx`
```


## Packages

Packages are the way to write extensions and applications to your threebot server and it can be driven by an optional package.py file which controls the life cycle of the application including install, uninstall,start .. etc.


### Structure
A package is a self contained code where you define the configurations, the API endpoints, and your database models. It should have the same structure that we will go through in the upcoming sections
```
hello
├── actors
│   └── helloActor.py
├── chats
│   └── helloChatflow.py
├── services
│   └── testservice.py
├── package.py
├── package.toml
└── __init__.py
```

Some components will be defined by default based on the parent package classes if not provided in the package while other components have to be included in the package when loading it to the jumpscale server.

#### Mandatory components
- **package.toml** is where the package information is defined such as its name, ports, and type of content for example static website.<br />
    Example
    ```toml
    name = "mypackage"                             # unique name of the package and should be the same as its directory name
    is_auth = true                                 # make the package available only to authorized users
    is_admin = true                                # make the package available only admins
    frontend = "/mypackage/<package home path>"    # Set this field if your package has frontend
    ```

    We can define static locations as follow:

    ```toml
    [[static_dirs]]
    name = "frontend"
    path_url = "/static"
    path_location = "frontend"
    ```

    We can also define bottle server to start in the toml file like in the following example

    ```toml
    [[bottle_servers]]
    name = "main"
    file_path = "bottle/bottle.py"
    path_url = "/"
    path_dest = "/"
    host = "0.0.0.0"
    port = 8552
    ```

    Other servers locations can also be defined, for example using codeserver
    ```toml
    [[servers.locations]]
    type = "proxy"
    host = "127.0.0.1"
    name = "codeserver"
    port = 8080
    path_url = "/codeserver"
    path_dest = "/"
    websocket = true
    ```
- **__init__.py** could include the docs that will summarize the use of the package where they are added in the beging of the file in docstrings.

#### Optional components

- **package.py** manages the lifecycle of the package.
    - By default, the base package.py is used defining main functionalities.
    - If additional functionalities want to be added during install,uninstall,start of the package in threebot server they can be redifined in this file.

- **actors**
    - actors directory contains the logic defined by the package and will be exposed as an API.
    - actor methods can be accessed through `<HOST>/{PACKAGE_NAME}/actors/{ACTOR_NAME}/{ACTOR_METHOD}`.
    - Parent class : `from jumpscale.servers.gedis.baseactor import BaseActor`
    - decorator for actor methods: ``from jumpscale.servers.gedis.baseactor import actor_method`
    <br />
    Example

        ```python
        from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
        from jumpscale.loader import j

        class HelloActor(BaseActor):
            def __init__(self):
                pass

            @actor_method
            def hello(self):
                return "hello from foo's actor"

        Actor = HelloActor
        ```

- **chats**
    - chats (chatflows) are interactive communication tools implemented as chatbots where interactive question structures are defined in the parent class
    - chatflows can be accessed through `<HOST>/{PACKAGE_NAME}/chats/{CHATFLOW_NAME}`.
    - Query parameter can be passed to chatflow as: `<HOST>/{PACKAGE_NAME}/chats/{CHATFLOW_NAME}#/?a=1&b=2` and can be accessed via `self.kwargs`.
    - Parent class : `from jumpscale.sals.chatflows.chatflows import GedisChatBot`
    - decorator for chatflow methods `from jumpscale.sals.chatflows.chatflows import chatflow_step`
    <br />
    Example
        ```
        from jumpscale.loader import j

        from jumpscale.sals.chatflows.chatflows import GedisChatBot, chatflow_step

        class HelloChatflow(GedisChatBot):
            steps = [
                "step1",
                "step2"
            ]

            @chatflow_step(title="Step1")
            def step1(self):
                self.name = self.string_ask("What is your name?",required=True)

            @chatflow_step(title="Step2")
            def step2(self):
                self.age = self.string_ask("How old are you?",required=True)

        chat = HelloChatflow
        ```
- **services**
    - services directory contains the background services that run with the package
    - Parent class : `from jumpscale.tools.servicemanager.servicemanager import BackgroundService`
    <br />
    Example

        ```python
        from jumpscale.tools.servicemanager.servicemanager import BackgroundService

        class TestService(BackgroundService):
          def __init__(self, interval=20, *args, **kwargs):
            """
                Test service that runs every 1 hour
            """
            super().__init__(interval, *args, **kwargs)

          def job(self):
            print("[Packagename - Test Service] Done")

        service = TestService()
        ```

### Configuration

Configuration is done in `package.toml`, where you configure servers, bottle apps, chatflows and more.

Manual configuration can be done also on package objects directly in the shell, but it's not recommended.

Example configuration:

```conf
name = "admin"

[[static_dirs]]
name = "frontend"
path_url = ""
path_location = "frontend"
index = "index.html"
spa = true
is_admin = true
```

#### Servers
In a package, the server configurations  will be mapped to nginx server configuration.

### More about packages

Basic Package functionalities and properties
- Functions
    - load_config()
    - get_bottle_server(file_path, host, port)
    - install()
    - uninstall()
    - start()
    - stop()
    - restart()

- Properties
    - module
    - base_url
    - actors_dir
    - chats_dir
    - static_dirs
    - bottle_servers
    - actors


### Adding new packages

- To add packages

  ```python
  threebot_server.packages.add(<path or giturl>)
  threebot_server.packages.add(path="/home/xmonader/wspace/threefoldtech/js-ng/jumpscale/packages/hello")
  ```

  ```python
  ➜  js-ng git:(development_threebot) ✗ curl -XPOST localhost:80/hello/actors/helloActor/hello
  "hello from foo's actor"%
  ```


**Note** that adding a package will reload python modules for all chats and actors.

## ssl

- If you to generate certificates to your website/package you can specify it in the package.toml explicitly.

for example

```toml
name = "admin"
ports = [80, 443]

[[static_dirs]]
name = "frontend"
path_url = ""
path_location = "frontend/output/"
index = "index.html"
spa = true
is_admin = true

[[servers]]
name = "default"
ports = [80, 443]
domain = "waleed.grid.tf" # your domain name
letsencryptemail = "aa@example.com" # email to get notifications from lets encrypt

[[servers.locations]]
type = "proxy"
host = "127.0.0.1"
port = 80
name = "admin"
path_url = "/"
path_dest = "/admin/"
```

- If you want to have default domain for your threebot, define it in the threebot start

```python
threebot_server = j.servers.threebot.get(domain="<optional><your-threebotdomain>", email="<your email><required if you want to use domain and ssl for certbot>")
threebot_server.start()
```

This will use certbot to generate a certificate for your domain
