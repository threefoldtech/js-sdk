from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method


class Alerts(BaseActor):
    @actor_method
    def list_alerts(self) -> str:
        """
            get all alerts
        """
        ret = [alert.json for alert in j.tools.alerthandler.find()]
        return j.data.serializers.json.dumps({"data": ret})

    @actor_method
    def get_alerts_count(self) -> str:
        """
            get count of alerts
        """
        return j.data.serializers.json.dumps({"data": j.tools.alerthandler.count()})

    @actor_method
    def delete_alerts(self, ids: list = []) -> str:
        """
            delete list of alerts
        """
        try:
            if ids:
                for _id in ids:
                    j.tools.alerthandler.delete(_id)
            return j.data.serializers.json.dumps({"data": "success"})
        except:
            raise j.exceptions.Value("Error in delete alerts")

    @actor_method
    def delete_all_alerts(self):
        """
            delete all alerts
        """
        try:
            j.tools.alerthandler.delete_all()
        except Exception as e:
            raise e


Actor = Alerts
