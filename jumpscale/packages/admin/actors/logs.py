from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method


class Logs(BaseActor):
    @actor_method
    def list_apps(self) -> str:
        apps = list(j.logger.get_app_names())
        return j.data.serializers.json.dumps({"data": apps})

    @actor_method
    def list_logs(self, app_name: str = j.logger.default_app_name) -> str:
        logs = list(j.logger.redis.tail(app_name=app_name))
        return j.data.serializers.json.dumps({"data": logs})

    @actor_method
    def remove_records(self, app_name: str = None):
        j.logger.redis.remove_all_records(app_name=app_name)


Actor = Logs
