from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j

class Packages(BaseActor):

    @actor_method
    def packages_get_status(self, names: list) -> str:
        return "hello from packages_get_status actor"
    
    @actor_method
    def packages_list(self) -> str:
        threebot = j.servers.threebot.get("default")

        # TODO: should return packages info not names only
        return j.data.serializers.json.dumps(
            list(threebot.packages.list_all())
        )

    @actor_method
    def package_add(self, path: str = "", git_url: str = "") -> str:
        if not path and not git_url:
            return j.data.serializers.json.dumps(
                "No path or git url provided")

        threebot = j.servers.threebot.get("default")
        try:
            threebot.packages.add(path=path)
            return j.data.serializers.json.dumps("OK") 
        except Exception:
            return j.data.serializers.json.dumps(
                "Error on adding package. Check alerts")

    @actor_method
    def package_delete(self, name: str) -> str:
        return "hello from package_delete actor"

    @actor_method
    def package_start(self, name: str) -> str:
        return "hello from package_start actor"

    @actor_method
    def package_stop(self, name: str) -> str:
        return "hello from package_stop actor"

    @actor_method
    def package_disable(self, name: str) -> str:
        return "hello from package_disable actor"

    @actor_method
    def package_enable(self, name: str) -> str:
        return "hello from package_enable actor"
   
Actor = Packages
