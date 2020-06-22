# Threebot Server

Threebot server is an application server based on nginx and gedis. It can further be extended using packages.

When adding packages to a server, they should first be defined, then added to the threebot server then the server can be started.


## Packages

Packages are the way to write extensions and applications to your threebot server and it can(optional) be driven using a package.py file which controls the life cycle of the application including  install,uninstall,start .. etc.

### Creating a new package
A package is a self contained code where you define the configurations, the API endpoints, and your database models. It should have the same structure that we will go through in the upcoming sections
```
hello
├── actors
│   └── helloActor.py
├── chats
│   └── helloChatflow.py
├── package.py
├── package.toml
└── __init__.py
```

### Package structure

Some components will be defined by default based on the parent package classes if not provided in the package while other components have to be included in the package when loading it to the jumpscale server.

#### Mandatory components
- **package.toml** is where the package information is defined such as its name, ports, and type of content for example static website.<br />
    Example
    ```
    name = "chatflows"
    ports = [ 80,443]

    [[static_dirs]]
    name = "frontend"
    path_url = "/static"
    path_location = "frontend"
    ```

    We can also define bottle server to start in the toml file like in the following example

    ```
    [[bottle_servers]]
    name = "main"
    file_path = "bottle/bottle.py"
    path_url = "/"
    path_dest = "/"
    host = "0.0.0.0"
    port = 8552
    ```

    Other servers locations can also be defined, for example using codeserver
    ```
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

        ```python3
        from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
        from jumpscale.god import j

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
    - Parent class : `from jumpscale.sals.chatflows.chatflows import GedisChatBot`
    - decorator for chatflow methods `from jumpscale.sals.chatflows.chatflows import chatflow_step`
    <br />
    Example
        ```
        from jumpscale.god import j

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

### Basic Package functionalities and properties
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


## Start threebot server

- start redis
- `poetry run jsng`

### start nginx

- On container it just works!

- On host

  - Nginx starts automatically with threebotserver but we have to increse its capablitites
  to be able to use port 80 and 443.

  using this command in your bash shell

  ```bash
  sudo setcap cap_net_bind_service=+ep /path/to/program
  ```

  `/path/to/program` usually be: `/usr/sbin/nginx` depending on your installation

  -if you don't want that you can manually do it using manually using: `sudo nginx -c ~/sandbox/cfg/nginx/main/nginx.conf`

- start threebotserver

  ```python
  threebot_server = j.servers.threebot.get("my_threebot_server", domain="<optional><your-threebotdomain>", email="<your email><required if you want to use domain and ssl for certbot")
  threebot_server.save()
  threebot_server.start()
  ```
- To add packages

```python
threebot_server.packages.add(<path or giturl>)
threebot_server.packages.add(path="/home/xmonader/wspace/threefoldtech/js-ng/jumpscale/packages/hello")
```

  ```
  ➜  js-ng git:(development_threebot) ✗ curl -XPOST localhost:80/    hello/actors/helloActor/hello
  "hello from foo's actor"%

  ```
