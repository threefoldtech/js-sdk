"""Gedis server package provides all code needed to have an RPC server using redis protocol for messaging

# TODO: add code to show how to start gedis.
```
~>  redis-cli -p 16000 greeter hi
actor greeter isn't loaded
 ~>  redis-cli -p 16000 system register_actor greeter /home/ahmed/wspace/js-next/js-ng/jumpscale/servers/gedis/example_greeter.py
(integer) -1
 ~>  redis-cli -p 16000 greeter hi
 hello world
 ~>  redis-cli -p 16000 greeter add2 jo deboeck
 "jodeboeck"
 ~>  fuser -k 16000/tcp

16000/tcp:           29331
 ~>  redis-cli -p 16000 greeter hi
 actor greeter isn't loaded
 ~>  redis-cli -p 16000 system register_actor greeter /home/ahmed/wspace/js-next/js-ng/jumpscale/servers/gedis/example_greeter.py
(integer) -1
 ~>  redis-cli -p 16000 greeter hi
 hello world
 ~>  redis-cli -p 16000 greeter ping

pong no?
 ~>  redis-cli -p 16000 greeter add2 reem khamis
"reemkhamis"
```
"""
from jumpscale.core.base import StoredFactory


def export_module_as():
    from .server import GedisServer

    return StoredFactory(GedisServer)
