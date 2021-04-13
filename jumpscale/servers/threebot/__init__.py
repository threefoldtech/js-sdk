from jumpscale.core.base import StoredFactory
from jumpscale.sals.nginx.nginx import PORTS
from jumpscale.entry_points.threebot import create_wallets_if_not_exists


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

    def start_default(self, wait=False, local=False, domain=None, email=None, cert=True):
        PORTS.init_default_ports(local)
        server = self.get("default")
        if not server.domain:
            server.domain = domain
            server.email = email
        server.save()
        create_wallets_if_not_exists()
        server.start(wait=wait, cert=cert)


def export_module_as():
    from .threebot import ThreebotServer

    return ThreebotServerFactory(ThreebotServer)
