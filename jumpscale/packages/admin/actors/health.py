from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j


class Health(BaseActor):

    @actor_method
    def get_disk_space(self) -> str:
        return "hello from admin's actor"

    @actor_method
    def health(self) -> str:
        return "hello from admin's actor"
    

    @actor_method
    def get_identity(self) -> str:
        return "hello from admin's actor"
    

    @actor_method
    def network_info(self) -> str:
        return "hello from admin's actor"
    

    @actor_method
    def js_version(self) -> str:
        return "hello from admin's actor"
    

    @actor_method
    def get_running_processes(self) -> str:
        return "hello from admin's actor"
    
    @actor_method
    def get_process_details(self, pid: int) -> str:
        return "hello from admin's actor"


Actor = Health