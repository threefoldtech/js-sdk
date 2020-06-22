from jumpscale.core.base import StoredFactory


class ThreebotServerFactory(StoredFactory):
    def get_running(self):
        for name in self.list_all():
            server = self.get(name)
            if server.started:
                return server


def export_module_as():
    from .threebot import ThreebotServer

    return ThreebotServerFactory(ThreebotServer)
