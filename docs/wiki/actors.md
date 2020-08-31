# Actors

Actors are our solution to interact with the backend, and it's very simple to write and extend APIs. So, actor is like a service that exposes a certain set of functionality and could be invoked using gedis client, or over http

## Adding new actors
- Adding new actors should be in the `actors/` directory of the package created

Example actor:

````python
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.loader import j

class Hello(BaseActor):
 def __init__(self):
  pass

 @actor_method
 def get_hello(self):
  return "hello from foo's actor"
 
 @actor_method
 def add_name(self,name: str) -> str:
  print(name)
  return j.data.serializers.json.dumps({"data": f"Hello {name}"})

Actor = Hello

````

- all actors methods should be decorated with `actor_method` so you could access it directly from 3Bot shell. The actor method could be imported using `from jumpscale.servers.gedis.baseactor import actor_method`

## Invoke actors

- The actors of your registered packages are exposed on http endpoint `{PACKAGE_NAME}/actors/{ACTOR_NAME}/{ACTOR_METHOD}`where 
 - **PACKAGE_NAME** is the name of the package added in the `package.toml` 
 - **ACTOR_NAME** is the name of the actor
 - **ACTOR_METHOD** is the name of the function being called, in the previous example could be `hello` or `add_name`

- or if you want to use pure http client, here's an example in javascript
 ```javascript
 import axios from 'axios'

 export function getPaste(pasteId) {
  return (axios.post("/pastebin/actors/pastebin/get_paste", { "args": { "paste_id": pasteId } }))
 }

 export function newPaste(code) {
  return (axios.post("/pastebin/actors/pastebin/new_paste", { "args": { "code": code } }))
 }
 ```

