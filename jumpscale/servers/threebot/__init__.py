from jumpscale.core.base import StoredFactory


class ThreebotServerFactory(StoredFactory):
    def get(self, *args, **kwargs):
        return super().get("default", *args, **kwargs)

    def start_default(self, wait=False):
        server = self.get("default")
        server.save()
        server.start(wait=wait)


def export_module_as():
    from .threebot import ThreebotServer

    return ThreebotServerFactory(ThreebotServer)
