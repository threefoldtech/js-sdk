from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method


class Logs(BaseActor):
    @actor_method
    def list_apps(self) -> str:
        apps = ["init"] + [app.decode() for app in j.core.db.smembers("applications")]
        return j.data.serializers.json.dumps({"data": apps})

    @actor_method
    def list_logs(self, appname: str = "init") -> str:
        logs = list(j.logger.redis.tail(appname=appname))
        return j.data.serializers.json.dumps({"data": logs})

    @actor_method
    def remove_records(self, appname: str = None):
        j.logger.redis.remove_all_records(appname=appname)


Actor = Logs
