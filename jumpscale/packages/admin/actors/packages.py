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
        return j.data.serializers.json.dumps({"data": self.threebot.packages.get_packages()})

    @actor_method
    def packages_names(self) -> str:
        return j.data.serializers.json.dumps({"data": list(self.threebot.packages.list_all())})

    @actor_method
    def package_add(self, path: str = "", giturl: str = "") -> str:
        # TODO: Now package is working only with path (js-ng version)
        # until threebot is migrated to js-sdk
        if path == "" and giturl != "":
            raise j.exceptions.NotImplemented("Giturl is not yet supported")

        return j.data.serializers.json.dumps({"data": self.threebot.packages.add(path=path)})

    @actor_method
    def package_delete(self, name: str) -> str:
        return j.data.serializers.json.dumps({"data": self.threebot.packages.delete(name)})


Actor = Packages
