from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j

class Packages(BaseActor):

    @actor_method
    def packages_get_status(self, names: list) -> str:
        return "hello from admin's actor"
    
    @actor_method
    def packages_list(self) -> str:
        return "hello from admin's actor"

    @actor_method
    def package_add(self, path: str = "", git_url: str = "") -> str:
        return "hello from admin's actor"

    @actor_method
    def package_delete(self, name: str) -> str:
        return "hello from admin's actor"

    @actor_method
    def package_start(self, name: str) -> str:
        return "hello from admin's actor"

    @actor_method
    def package_stop(self, name: str) -> str:
        return "hello from admin's actor"

    @actor_method
    def package_disable(self, name: str) -> str:
        return "hello from admin's actor"

    @actor_method
    def package_enable(self, name: str) -> str:
        return "hello from admin's actor"
   
Actor = Packages
