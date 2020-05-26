from jumpscale.core.base import StoredFactory
from .explorer import Explorer
from jumpscale.core.config import get_config


class explorerFactory(StoredFactory):
    def get_default(self):
        return self.get("default", url=get_config()["threebot"]["explorer_url"])


def export_module_as():

    return explorerFactory(Explorer)
