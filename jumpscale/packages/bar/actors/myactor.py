from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.loader import j


class MyActor(BaseActor):

    @actor_method
    def hello(self) -> str:
        return "hello from bar's actor"


Actor = MyActor
