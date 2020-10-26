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
    def add_internal_package(self, name, extras=None) -> str:
        """
        add internal package with name

        this will search `j.packages` namespace for the given name.

        Args:
            name (str): name of the package, e.g. codeserver.
            extras (dict, optional): extras to be passed to `package.install`. Defaults to None.

        Raises:
            j.exceptions.NotFound: in case package cannot be found under `j.packages`

        Returns:
            str: package information as json
        """
        try:
            package_module = getattr(j.packages, name)
        except AttributeError:
            raise j.exceptions.NotFound(f'package with name "{name}" cannot be found')

        path = package_module.__path__[0]
        return self.add_package(path=path, extras=extras)

    @actor_method
    def delete_package(self, name: str) -> str:
        return j.data.serializers.json.dumps({"data": self.threebot.packages.delete(name)})

    @actor_method
    def list_chat_urls(self, name: str) -> str:
        package_chats = []
        if name in self.threebot.packages.packages:
            package = self.threebot.packages.get(name)
            if name in self.threebot.chatbot.chats:
                package_chat_names = self.threebot.chatbot.chats[name].keys()
                for chat_name in package_chat_names:
                    package_chats.append({"name": chat_name, "url": f"{package.base_url}/chats/{chat_name}"})
        return j.data.serializers.json.dumps({"data": package_chats})


Actor = Packages
