from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.loader import j

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
        return j.data.serializers.json.dumps( {"data":{ "name":j.core.identity.me.tname, "id":j.core.identity.me.tid }} )

    @actor_method
    def network_info(self) -> str:
        return j.data.serializers.json.dumps({ "data":j.sals.nettools.get_default_ip_config() })

    @actor_method
    def js_version(self) -> str:
        #  TODO: add version actor
        return "need to add version actor"

    @actor_method
    def get_memory_usage(self) -> str:
        return j.data.serializers.json.dumps( {"data":j.sals.process.get_memory_usage() })

    @actor_method
    def get_running_processes(self) -> str:
        return j.data.serializers.json.dumps({"data": j.sals.process.get_processes_info()})

Actor = Health
