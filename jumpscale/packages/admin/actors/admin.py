from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j

class Admin(BaseActor):

    @actor_method
    def admin_list(self) -> str:
        return "hello from admin's actor"

    @actor_method
    def admin_add(self, name: str) -> str:
        return "hello from admin's actor"

    @actor_method
    def admin_delete(self, name: str) -> str:
        return "hello from admin's actor"

    @actor_method
    def get_explorer(self) -> str:
        return "hello from admin's actor"

    @actor_method
    def set_explorer(self, explorer_type: str) -> str:
        return "hello from admin's actor"
   
Actor = Admin
