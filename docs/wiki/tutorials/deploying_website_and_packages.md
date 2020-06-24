# Deploy website and packages on jsng

## Index

- [Requirments](#requirments)
- [create package using jsng](#creating-jsng-package)
- [create website with custom locations](#create-website-with-custom-locations)

## Requirments

- JS-NG
- Redis (Install using: `apt install redis`)
- Nginx (Install using: `apt install nginx`)
- Certbot [Install](https://certbot.eff.org/lets-encrypt/ubuntuxenial-nginx.html)
- DO Machine and domain
- A test package [here](https://github.com/threefoldtech/www_threefold.tech)

## Creating jsng package (Automatically with jsng and threebotserver)

- See the quick start how to install jsng with sdk [here](https://github.com/threefoldtech/js-sdk/blob/development/docs/wiki/quick_start.md#L1)

- Upgrade the package to jsng, modify package.toml to be the following

  ```toml
  name = "threefold_tech"
  ports = [80, 443]

  [[static_dirs]]
  name = "html"
  path_url = "threefold_tech" # access location path example localhost/threefold_tech
  path_location = "html"
  index = "index.html"

  [[servers]]
  name = "threefold_tech"
  ports = [80, 443]
  domain = "waleed.grid.tf" # your domain name
  letsencryptemail = "aa@example.com" # email to get notifications from lets encrypt

  [[servers.locations]]
  type = "proxy"
  host = "127.0.0.1"
  port = 80
  name = "threefold_tech"
  path_url = "/"
  path_dest = "/threefold_tech/"
  ```

- Example package structure

  ![cert](../images/package.png)


- Start threebot server

  ```python
  threebot_server = j.servers.threebot.get("default",   domain="<optional><your-threebotdomain>", email="<your email><required if you want to   use domain and ssl for certbot>")
  threebot_server.start()
  ```

- More about starting 3bot server start [here](https://github.com/threefoldtech/js-sdk/blob/development/docs/wiki/threebot.md)

## Create website with custom locations (Manually)

- Get nginx sal instance

  ```python
  nginx = j.sals.nginx.get("threefold_tech_nginx")
  nginx.configure()
  nginx.save()
  ```

- create 443 website

  ```python
  website = nginx.websites.get("threefold_tech_website_443")
  website.port = 443
  website.ssl = True
  website.domain = "waleed.grid.tf"
  website.letsencryptemail =  "waleed.hammam@gmail.com"
  ```

- create 443 location

  ```python
  loc = website.locations.get("location_443")
  loc.path_url = "/" #  location path
  loc.path_location = "/root/js-ng/jumpscale/packages/threefold_tech/html/" #  alias for the location
  loc.index = "index.html"#  index of the location
  loc.location_type = "static" # static,spa,proxy type of   location config
  loc.scheme = "https" #  https or https
  website.configure()
  ```

- create 80 website

  ```python
  website = nginx.websites.get("threefold_tech_website_80")
  website.port=80
  website.domain = "waleed.grid.tf"
  ```

- create 80 location

  ```python
  loc = website.locations.get("location_80")
  loc.path_url = "/" #  location path
  loc.path_location = "/root/js-ng/jumpscale/packages/threefold_tech/html/" #  alias for the location
  loc.index = "index.html"#  index of the location
  loc.location_type = "static" # static,spa,proxy type of   location config
  loc.scheme = "http" #  https or https
  ```

- Configure website and locations

  ```python
  website.configure()
  ```

- start nginx

  ```bash
  nginx -c ~/sandbox/cfg/nginx/threefold_tech_nginx/nginx.conf
  ```

- Locations should be like the following

  ![cert](../images/location_custom.png)

- visit your domain to make sure you are ok and with https certificate

  ![cert](../images/cert1.png)

### Troubleshooting

- if you got 403 forbidden error this is due to permissions, make sure you using nginx with the correct user in nginx.conf file first line
