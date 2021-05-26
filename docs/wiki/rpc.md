# Gedis
Gedis is a RPC framework that provide automatic generation of client side code at runtime.
Which means you only need to define the server interface and the client will automatically receive the code it needs to talk to the server at connection time.


## Gedis Actor
The ```Gedis``` actors should inherts from the ```BaseActor``` class and all function should define the type annotations of its parameters

```python
from jumpscale.servers.gedis.baseactor import BaseActor


class Example(BaseActor):
    def add_two_ints(self, x: int, y: int) -> int:
        """Adds two ints

        Arguments:
            x {int} -- first int
            y {int} -- second int

        Returns:
            int -- the sum of the two ints
        """
        return x + y

    def concate_two_strings(self, x: str, y: str) -> str:
        """Concate two strings

        Arguments:
            x {str} -- first string
            y {str} -- second string

        Returns:
            str -- the concate of the two strings
        """
        return x + y


Actor = Example
```

### Starting the server and loading actors
``` python
JS-NG> server = j.servers.gedis.get("main")
JS-NG> server.actor_add("example", "/sandbox/code/github/threefoldtech/js-ng/jumpscale/servers/gedis/example_actor.py")
JS-NG> server.start()
```

### Getting a client and calling actors
```python
JS-NG> cl = j.clients.gedis.get("main")
JS-NG> cl.actors.example.add_two_ints(1, 2)
3
```

> in case the actor method is missing the type annotation of one of its parameters, the server will return an error for example ```jumpscale.core.exceptions.exceptions.Runtime: argument x in method add_two_ints doesn't have type annotation```



## Type annotations and Actors

We make use of type annotations for many things in gedis framework, including types and parameters validations, self documenting actors

Here is an example actor
```python
from jumpscale.servers.gedis.baseactor import BaseActor
from typing import Sequence
from jumpscale.loader import j
import inspect, sys

class TestObject:
    def __init__(self):
        self.attr = None

    def to_dict(self):
        return self.__dict__

    def from_dict(self, ddict):
        self.__dict__ = ddict


class Example(BaseActor):
    def add_two_ints(self, x: int, y: int) -> int:
        """Adds two ints

        Arguments:
            x {int} -- first int
            y {int} -- second int

        Returns:
            int -- the sum of the two ints
        """
        return x + y

    def concate_two_strings(self, x: str, y: str) -> str:
        """Concate two strings

        Arguments:
            x {str} -- first string
            y {str} -- second string

        Returns:
            str -- the concate of the two strings
        """
        return x + y

    def get_testobject(self, myobj: TestObject, new_value: int) -> TestObject:
        """returns an object of type Test object with update attribute attr to `new_value`

        Arguments:
            myobj {TestObject} -- the object to be modified

        Returns:
            TestObject -- modified object
        """
        myobj.attr = new_value
        return myobj

Actor = Example

```
This actor has `add_two_ints`, `concate_two_strings`, and `modify_objet` methods. The first two are pretty basic

Let's do a walkthrough and check the invocation, and the errors

```
JS-NG> ACTOR_PATH = "/home/xmonader/wspace/threefoldtech/js-ng/jumpscale/servers/gedis/example_actor.py"
JS-NG> cl = j.clients.gedis.get("test")
JS-NG> cl.actors.system.register_actor("test_actor", ACTOR_PATH)
True

```
At this point we can do `cl.reload` to add `test_actor` into the client domain

```
JS-NG> cl.reload()
```
### Getting actor documentation and information from

```
JS-NG> cl.actors.test_actor.info()
{'module': '/home/xmonader/wspace/threefoldtech/js-ng/jumpscale/servers/gedis', 'path': '/home/xmonader/wspace/threefoldtech/js-ng/jumpscale/servers/gedis/example_actor.py', 'methods': {'add_two_ints': {'args': [['x', 'int'], ['y', 'int']], 'doc': 'Adds two ints\n        \n        Arguments:\n            x {int} -- first int\n            y {int} -- second int\n        \n        Returns:\n            int -- the sum of the two ints\n        ', 'response_type': None}, 'concate_two_strings': {'args': [['x', 'str'], ['y', 'str']], 'doc': 'Concate two strings\n        \n        Arguments:\n            x {str} -- first string\n            y {str} -- second string\n        \n        Returns:\n            str -- the concate of the two strings\n        ', 'response_type': None}, 'info': {'args': [], 'doc': '', 'response_type': None}, 'get_testobject': {'args': [['myobj', 'TestObject'], ['new_value', 'int']], 'doc': 'returns an object of type Test object with update attribute attr to `new_value`\n        \n        Arguments:\n            myobj {TestObject} -- the object to be modified\n        \n        Returns:\n            TestObject -- modified object\n        ', 'response_type': 'TestObject'}}}

```

### Using the actor methods

```
JS-NG> cl.actors.test_actor.add_two_ints(4, 5)
9

```
What if we pass a wrong type?

```
JS-NG> cl.actors.test_actor.add_two_ints(4, "11")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/xmonader/wspace/threefoldtech/js-ng/jumpscale/clients/gedis/gedis.py", line 57, in method
    response = self._gedis_client.execute(actor_name, actor_method, *args, **kwargs)
               │                          │           │              │       └ {}
               │                          │           │              └ (4, '11')
               │                          │           └ 'add_two_ints'
               │                          └ 'test_actor'
               └ <jumpscale.clients.gedis.gedis.ActorProxy object at 0x7fb434817390>
  File "/home/xmonader/wspace/threefoldtech/js-ng/jumpscale/clients/gedis/gedis.py", line 161, in execute
    raise RemoteException(response_json['error'])
          │               └ {'success': False, 'error': 'parameter (y) supposed to be of type (int), but found (str)', 'result': None}
          └ <class 'jumpscale.clients.gedis.gedis.RemoteException'>
jumpscale.clients.gedis.gedis.RemoteException: parameter (y) supposed to be of type (int), but found (str)

parameter (y) supposed to be of type (int), but found (str)

```
What if we pass more than the specified arguments?

```
JS-NG> cl.actors.test_actor.add_two_ints(4, 2, 6)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/xmonader/wspace/threefoldtech/js-ng/jumpscale/clients/gedis/gedis.py", line 57, in method
    response = self._gedis_client.execute(actor_name, actor_method, *args, **kwargs)
               │                          │           │              │       └ {}
               │                          │           │              └ (4, 2, 6)
               │                          │           └ 'add_two_ints'
               │                          └ 'test_actor'
               └ <jumpscale.clients.gedis.gedis.ActorProxy object at 0x7fb434817390>
  File "/home/xmonader/wspace/threefoldtech/js-ng/jumpscale/clients/gedis/gedis.py", line 161, in execute
    raise RemoteException(response_json['error'])
          │               └ {'success': False, 'error': 'Traceback (most recent call last):\n  File "/home/xmonader/wspace/threefoldtech/js-ng/jumpscale/servers/g...
          └ <class 'jumpscale.clients.gedis.gedis.RemoteException'>
jumpscale.clients.gedis.gedis.RemoteException: Traceback (most recent call last):
  File "/home/xmonader/wspace/threefoldtech/js-ng/jumpscale/servers/gedis/server.py", line 210, in _exceute
    args, kwargs = self._validate_method_arguments(method, args, kwargs)
    │     │        │                               │       │     └ {}
    │     │        │                               │       └ [4, 2, 6]
    │     │        │                               └ <bound method Example.add_two_ints of </home/xmonader/wspace/threefoldtech/js-ng/jumpscale/servers/gedis.Example object at 0x7f75132cf...
    │     │        └ GedisServer(_Base__instance_name='test', _Base__parent=None, ___actors={}, __enable_system_actor=True, __host='127.0.0.1', __por...
    │     └ {}
    └ [4, 2, 6]
  File "/home/xmonader/wspace/threefoldtech/js-ng/jumpscale/servers/gedis/server.py", line 188, in _validate_method_arguments
    bound_arguments = signature.bind(*args, **kwargs)
                      │               │       └ {}
                      │               └ [4, 2, 6]
                      └ <Signature (x: int, y: int) -> int>
  File "/home/linuxbrew/.linuxbrew/opt/python/lib/python3.7/inspect.py", line 3015, in bind
    return args[0]._bind(args[1:], kwargs)
           │             │         └ {}
           │             └ (<Signature (x: int, y: int) -> int>, 4, 2, 6)
           └ (<Signature (x: int, y: int) -> int>, 4, 2, 6)
  File "/home/linuxbrew/.linuxbrew/opt/python/lib/python3.7/inspect.py", line 2936, in _bind
    raise TypeError('too many positional arguments') from None
TypeError: too many positional arguments

```

### Complex types

Let's assume that we have a complex type like

```python
class TestObject:
    def __init__(self):
        self.attr = None

    def to_dict(self):
        return self.__dict__

    def from_dict(self, ddict):
        self.__dict__ = ddict
```
Any object with `to_dict` and `from_dict` is ok to use in actor methods for the serialization on the wire.

```python
    def get_testobject(self, myobj: TestObject, new_value: int) -> TestObject:
        """Modify atrribute attr of the given object

        Arguments:
            myobj {TestObject} -- the object to be modified

        Returns:
            TestObject -- modified object
        """
        myobj.attr = new_value
        return myobj
```
Let's test it

```
JS-NG> class TestObject:
     2     def __init__(self):
     3         self.attr = None
     4
     5     def to_dict(self):
     6         return self.__dict__
     7
     8     def from_dict(self, ddict):
     9         self.__dict__ = ddict
JS-NG> obj = TestObject()
JS-NG> res = cl.actors.test_actor.get_testobject(obj, 6)
JS-NG> res.attr
6
JS-NG> obj.attr
JS-NG>
```
