from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.core.exceptions import JSException


class Packages(BaseActor):
    def __init__(self):
        self._threebot = None

    @property
    def threebot(self):
        if not self._threebot:
            self._threebot = j.servers.threebot.get()
        return self._threebot

    @actor_method
    def get_package_status(self, names: list) -> str:
        return "hello from packages_get_status actor"

    @actor_method
    def list_packages(self) -> str:
        return j.data.serializers.json.dumps({"data": self.threebot.packages.get_packages()})

    @actor_method
    def packages_names(self) -> str:
        return j.data.serializers.json.dumps({"data": list(self.threebot.packages.list_all())})

    @actor_method
    def add_package(self, path: str = "", giturl: str = "", extras=None) -> str:
        extras = extras or {}
        if path:
            path = path.strip()
        if giturl:
            giturl = giturl.strip()
        return j.data.serializers.json.dumps({"data": self.threebot.packages.add(path=path, giturl=giturl, **extras)})

    @actor_method
    def delete_package(self, name: str) -> str:
        return j.data.serializers.json.dumps({"data": self.threebot.packages.delete(name)})


Actor = Packages
