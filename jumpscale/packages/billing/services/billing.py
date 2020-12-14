from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.loader import j


class BillingService(BackgroundService):
    def __init__(self, name="billing", interval=1, *args, **kwargs):
        super().__init__(name, interval, *args, **kwargs)

    def job(self):
        j.sals.billing.process_payments()
        j.sals.billing.process_refunds()
