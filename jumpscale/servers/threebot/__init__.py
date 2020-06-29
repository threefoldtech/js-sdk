from jumpscale.core.base import StoredFactory


class ThreebotServerFactory(StoredFactory):
    default = None

    def new(self, name, *args, **kwargs):
        if self.default:
            return self.default
        self.default = super().new("default", *args, **kwargs)
        return self.default

    def get(self, name=None, *args, **kwargs):
        """get ThreebotServer default instance

        Args:
            name: ignored but here to be same signature as parent

        Returns:
            ThreebotServer
        """
        return super().get("default", *args, **kwargs)

    def start_default(self, wait=False):
        server = self.get("default")
        server.save()
        server.start(wait=wait)


def export_module_as():
    from .threebot import ThreebotServer

    return ThreebotServerFactory(ThreebotServer)
