from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.loader import j
import gevent


class BillingService(BackgroundService):
    def __init__(self, interval=1, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    def job(self):
        j.sals.billing.process_payments()
        j.sals.billing.refund_extra()
        j.sals.billing.refund_failed_payments()
        j.sals.billing.process_refunds()
        gevent.sleep(5)


service = BillingService()
