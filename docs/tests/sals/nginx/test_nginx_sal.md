### test01_basic

Test case for server initialization with default config.

**Test Scenario:**
1. Start the nginx server.
2. Check the config is stored and the server is started.
3. Clean up the config and stop the server.
4. Check the server is stopped.

### test02_static_location

Test case for serving a static location.

**Test Scenario**

1. Start nginx server.
2. Configure a static website with two pages.
3. Check they're served.

### test03_proxy_location

Test case for serving a proxy location.

**Test Scenario**

1. Initialize a python webserver serving directory listing.
2. Start nginx server.
3. Configur the website to act as a proxy to the python server.
4. Check the http is served.

### test04_custom_location

Test case for serving a static location using custom config.

**Test Scenario**

1. Start nginx.
2. Add a location serving a static website with two pages using custom config.
3. Check it's served.

### test05_ssl_location

Test case for serving a site over https.

**Test Scenario**

1. Same scenario as the proxy server served over https.

### test06_local_server

Test case for serving a site over https using on a local port.

**Test Scenario**

1. Same scenario as the https scenario served over local https port.
