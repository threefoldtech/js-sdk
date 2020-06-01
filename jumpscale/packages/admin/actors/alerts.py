from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j


class Alerts(BaseActor):

    @actor_method
    def list_alerts(self) -> str:
        return "hello from admin's actor"

    @actor_method
    def delete_alerts(self, identifiers: list) -> str:
        return "hello from admin's actor"
   
Actor = Alerts