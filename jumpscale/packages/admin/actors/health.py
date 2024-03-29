from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method

from jumpscale.clients.stellar import HORIZON_NETWORKS, THREEFOLDFOUNDATION_TFTSTELLAR_SERVICES


class Health(BaseActor):
    @actor_method
    def get_disk_space(self) -> str:
        res = {}
        disk_obj = j.sals.fs.shutil.disk_usage("/")
        res["total"] = disk_obj.total // (1024.0**3)
        res["used"] = disk_obj.used // (1024.0**3)
        res["free"] = disk_obj.free // (1024.0**3)
        res["percent"] = (res["used"] / res["total"]) * 100
        return j.data.serializers.json.dumps({"data": res})

    @actor_method
    def health(self) -> str:
        return "All is good"

    @actor_method
    def network_info(self) -> str:
        return j.data.serializers.json.dumps({"data": j.sals.nettools.get_default_ip_config()})

    @actor_method
    def js_version(self) -> str:
        #  TODO: add version actor
        return "need to add version actor"

    @actor_method
    def get_memory_usage(self) -> str:
        return j.data.serializers.json.dumps({"data": j.sals.process.get_memory_usage()})

    @actor_method
    def get_running_processes(self) -> str:
        return j.data.serializers.json.dumps({"data": j.sals.process.get_processes_info()})

    @actor_method
    def get_health_checks(self, network="STD") -> str:
        services = {
            "stellar": {"name": "Stellar", "status": True},
            "token_services": {"name": "Token Services", "status": True},
        }

        # urls of services according to network
        stellar_url = HORIZON_NETWORKS[network]
        tokenservices_url = THREEFOLDFOUNDATION_TFTSTELLAR_SERVICES[network]

        # check stellar service
        try:
            j.tools.http.get(stellar_url)
        except:
            services["stellar"]["status"] = False

        # check token services
        try:
            j.tools.http.get(tokenservices_url)
        except:
            services["token_services"]["status"] = False

        return j.data.serializers.json.dumps({"data": services})


Actor = Health
