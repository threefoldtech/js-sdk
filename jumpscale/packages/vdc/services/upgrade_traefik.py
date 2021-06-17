import gevent
from jumpscale.loader import j

from jumpscale.tools.servicemanager.servicemanager import BackgroundService


class UpgradeTraefik(BackgroundService):
    def __init__(self, interval=5 * 60, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    def job(self):
        for vdc_name in j.sals.vdc.list_all():
            vdc_instance = j.sals.vdc.find(vdc_name, load_info=True)
            vdc_instance.get_deployer().kubernetes.upgrade_traefik()
            gevent.sleep(1)
