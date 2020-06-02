from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j


class Logs(BaseActor):

    @actor_method
    def list_apps(self) -> str:
        return "hello from admin's actor"
    

    @actor_method
    def list_logs(self, appname: str, id_from: int = 0) -> str:
        return "hello from admin's actor"
    
    @actor_method
    def delete(self, appname: str = "") -> str:
        # if no appname delete all logs 
        return "hello from admin's actor"
    
    @actor_method
    def delete_selected(self, ids: list) -> str:
        return "hello from admin's actor"
   
Actor = Logs