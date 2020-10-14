### test01_basic

Test case for server initialization with default config.

**Test Scenario**

- Start the nginx server.
- Check the config is stored and the server is started.
- Clean up the config and stop the server.
- Check the server is stopped.

### test02_static_location

Test case for serving a static location.

**Test Scenario**

- Start nginx server.
- Configure a static website with two pages.
- Check they're served.

### test03_proxy_location

Test case for serving a proxy location.

**Test Scenario**

- Initialize a python webserver serving directory listing.
- Start nginx server.
- Configur the website to act as a proxy to the python server.
- Check the http is served.

### test04_custom_location

Test case for serving a static location using custom config.

**Test Scenario**

- Start nginx.
- Add a location serving a static website with two pages using custom config.
- Check it's served.

### test05_ssl_location

Test case for serving a site over https.

**Test Scenario**

- Same scenario as the proxy server served over https.

### test06_local_server

Test case for serving a site over https using on a local port.

**Test Scenario**

- Same scenario as the https scenario served over local https port.
