import gevent
from jumpscale.loader import j

from jumpscale.tools.servicemanager.servicemanager import BackgroundService


class UpdateExpiration(BackgroundService):
    def __init__(self, interval=5 * 60, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    def job(self):
        j.logger.info("Updating VDCs expiration")
        threads = []
        for vdc_name in j.sals.vdc.list_all():
            thread = gevent.spawn(self.update_expiration, vdc_name)
            threads.append(thread)

        gevent.joinall(threads)

    def update_expiration(self, name):
        vdc = j.sals.vdc.get(name)
        if vdc.is_empty():
            return
        vdc.expiration = vdc.calculate_expiration_value()
        vdc.save()


service = UpdateExpiration()
