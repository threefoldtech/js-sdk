from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method


class MyActor(BaseActor):
    @actor_method
    def hello(self) -> str:
        return "hello from foo's actor"


Actor = MyActor
