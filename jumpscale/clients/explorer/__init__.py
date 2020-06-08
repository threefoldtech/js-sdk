from jumpscale.core.base import StoredFactory
from .explorer import Explorer
from jumpscale.core.config import get_config, set as set_config


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

    def default_addr_set(self, url):
        threebot_cfg = get_config()["threebot"]
        threebot_cfg["explorer_url"] = url
        set_config("threebot", threebot_cfg)

def export_module_as():

    return ExplorerFactory(Explorer)
