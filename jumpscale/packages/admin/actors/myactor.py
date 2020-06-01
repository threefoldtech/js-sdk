from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j


class MyActor(BaseActor):

    @actor_method
    def hello(self) -> str:
        return "hello from admin's actor"
    
   
Actor = MyActor