from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j
from jumpscale.core.exceptions import JSException

class Solutions(BaseActor):

    @actor_method
    def solutions_list(self, name: str = "") -> str:
        return "hello from solutions actor"
               
    @actor_method
    def solution_delete(self, name: str) -> str:
        return "hello from solutions actor"

Actor = Solutions
