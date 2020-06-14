from jumpscale.core.base import StoredFactory
from .explorer import Explorer
from jumpscale.god import j


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
        return Explorer(j.core.config.get("threebot")["explorer_url"])

    def get_by_url(self, url):
        return Explorer(url)

    def default_addr_set(self, url):
        threebot_cfg = j.core.config.get("threebot")
        threebot_cfg["explorer_url"] = url
        j.core.config.set("threebot", threebot_cfg)


def export_module_as():
    return ExplorerFactory(Explorer)
