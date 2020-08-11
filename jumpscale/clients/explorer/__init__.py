from jumpscale.core.base import StoredFactory
from .explorer import Explorer
from jumpscale.loader import j


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
        return Explorer(j.core.config.get("explorer")["default_url"])

    def get_by_url(self, url):
        # gets an explorer client with the "default identity"
        return Explorer(url)

    def get_by_url_and_identity(self, url, identity_name):
        # gets an explorer client with the "identity"
        return Explorer(url, identity_name=identity_name)

    def default_addr_set(self, url):
        j.core.config.set("explorer", {"default_url": url})


def export_module_as():
    return ExplorerFactory(Explorer)
