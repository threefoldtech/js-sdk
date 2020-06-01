from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j


class Auth(BaseActor):

    @actor_method
    def authorizedhello(self) -> str:
        return "hello from admin's actor"
   
Actor = Auth