"""This module gives you all the facilities to communicate with gedis server

Connecting to a gedis server
```
JS-NG> gedis = j.clients.gedis.get("local")
JS-NG> gedis.list_actors()
['system']
```

Registering actor
```
JS-NG> gedis.actors.system.register_actor("greeter", "/home/ahmed/wspace/threefoldtech/js-ng/jumpscale/servers/gedis/example_greeter.py")
1
```

Listing actors
```
JS-NG> gedis.list_actors()
['system', 'greeter']
```

Documentation of an actor

```
JS-NG> gedis.ppdoc("greeter")
{
  "add2": {
    "args": [
      "a",
      "b"
    ],
    "doc": "Add two args\n        \n        "
  },
  "hi": {
    "args": [],
    "doc": "returns hello world\n        "
  },
  "info": {
    "args": [
      "result",
      "members",
      "name",
      "attr"
    ],
    "doc": ""
  },
  "ping": {
    "args": [],
    "doc": "\n        \n        "
  }
}
```
Invoking an actor method
```
JS-NG> gedis.execute("greeter", "hi")
b'hello world'

JS-NG> gedis.execute("greeter", "ping")
b'pong no?'

JS-NG> gedis.execute("greeter", "add2", "first", "second")
b'firstsecond'
```
Invoking actor method with attribute access
```
JS-NG> gedis.actors.greeter.hi()
b'hello world'

JS-NG> gedis.actors.greeter.add2("a", "b")
b'ab'
```
"""


def export_module_as():

    from jumpscale.core.base import StoredFactory

    from .gedis import GedisClient

    return StoredFactory(GedisClient)
