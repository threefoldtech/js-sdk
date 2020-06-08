from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j

class Health(BaseActor):

    @actor_method
    def get_disk_space(self) -> str:
        res = {}
        disk_obj = j.sals.fs.shutil.disk_usage('/')
        res["total"] = disk_obj.total // (1024.0 ** 3)
        res["used"] = disk_obj.used // (1024.0 ** 3)
        res["free"] = disk_obj.free // (1024.0 ** 3)
        res["percent"] = (res["used"] / res["total"]) * 100
        return j.data.serializers.json.dumps(res)

    @actor_method
    def health(self) -> str:
        return "All is good"
    
    @actor_method
    def get_identity(self) -> str:
        # TODO: get Identify
        return "identity actor"
    
    @actor_method
    def network_info(self) -> str:
        return j.data.serializers.json.dumps({"network":j.sals.nettools.get_default_ip_config()})
    
    @actor_method
    def js_version(self) -> str:
        #  TODO: add version actor
        return "need to add version actor"
    
    @actor_method
    def get_running_processes(self) -> str:
        return "hello from admin's actor"
    
    @actor_method
    def get_process_details(self, pid: int) -> str:
        return "hello from admin's actor"

Actor = Health
