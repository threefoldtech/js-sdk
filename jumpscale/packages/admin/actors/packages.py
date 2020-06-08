from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j
from jumpscale.core.exceptions import JSException

class Packages(BaseActor):
    def __init__(self):
        self.threebot = j.servers.threebot.get("default")

    @actor_method
    def packages_get_status(self, names: list) -> str:
        return "hello from packages_get_status actor"
    
    @actor_method
    def packages_list(self) -> str:
        # TODO: should return packages info not names only
        try:
            return j.data.serializers.json.dumps(
                self.threebot.packages.get_packages()
            )
        except JSException:
            return j.data.serializers.json.dumps(
                "Error fetching packages. Check alerts")

    @actor_method
    def package_add(self, path: str = "", git_url: str = "") -> str:
        if not path and not git_url:
            return j.data.serializers.json.dumps(
                "No path or git url provided")

        try:
            return j.data.serializers.json.dumps(
                {"package":self.threebot.packages.add(path=path)}
            ) 
        except JSException:
            return j.data.serializers.json.dumps(
                "Error on adding package. Check alerts")

    @actor_method
    def package_delete(self, name: str) -> str:
        try:
            self.threebot.packages.delete(name)
            return j.data.serializers.json.dumps("OK")
        except JSException as e:
            return j.data.serializers.json.dumps(str(e))

    @actor_method
    def package_start(self, name: str) -> str:
        try:
            return j.data.serializers.json.dumps(
                {"package":self.threebot.packages.start_package(name)}
            ) 
        except JSException as e:
            return j.data.serializers.json.dumps(str(e))

    @actor_method
    def package_stop(self, name: str) -> str:
        try:
            return j.data.serializers.json.dumps(
                {"package":self.threebot.packages.stop_package(name)}
            ) 
        except JSException as e:
            return j.data.serializers.json.dumps(str(e))

    # @actor_method
    # def package_disable(self, name: str) -> str:
    #     return "hello from package_disable actor"

    # @actor_method
    # def package_enable(self, name: str) -> str:
    #     return "hello from package_enable actor"
   
Actor = Packages
