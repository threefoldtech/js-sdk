'''
# Nginx tool

This tool is help for (install, start, stop, reload, restart) Nginx server.

NGINX is open source software for web serving, reverse proxying, caching, load balancing, media streaming, and more.
It started out as a web server designed for maximum performance and stability. In addition to its HTTP server capabilities,
NGINX can also function as a proxy server for email (IMAP, POP3, and SMTP) and a reverse proxy and load balancer for HTTP, TCP, and UDP servers.

## Install
```
main = j.tools.nginx.get(name="main")
main.install()
```
## Start
```
main = j.tools.nginx.get(name="main")
main.start()
```
## Stop
```
main = j.tools.nginx.get(name="main")
main.stop()
```
## reload
```
main = j.tools.nginx.get(name="main")
main.reload()
```
## restart
```
main = j.tools.nginx.get(name="main")
main.restart()
```
'''

def export_module_as():
    from jumpscale.core.base import StoredFactory
    from .nginxserver import NginxServer

    return StoredFactory(NginxServer)
