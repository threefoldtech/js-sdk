from jumpscale.loader import j
from jumpscale.packages.vdc.billing import auto_extend_billing
from jumpscale.tools.servicemanager.servicemanager import BackgroundService


class AutoExtendbillingService(BackgroundService):
    def __init__(self, interval=60 * 60, *args, **kwargs):
        """Provisioning wallet service that will run every hour to extend the VDC pool
        """
        super().__init__(interval, *args, **kwargs)

    def job(self):
        auto_extend_billing()
        j.logger.info("Auto extend billing service")


service = AutoExtendbillingService()
