from jumpscale.core.base import StoredFactory
from .explorer import Explorer
from jumpscale.core.config import get_config


class ExplorerFactory(StoredFactory):
    def new(self, name, url, *args, **kwargs):
        kwargs["url"] = url
        instance = super().new(name, *args, **kwargs)
        instance.url = url
        return instance

    def get(self, name, url, *args, **kwargs):
        instance = self.find(name)
        if instance:
            return instance
        return self.new(name, url, *args, **kwargs)

    def get_default(self):
        return self.get("default", url=get_config()["threebot"]["explorer_url"])


def export_module_as():

    return ExplorerFactory(Explorer)
