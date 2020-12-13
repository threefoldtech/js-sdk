from jumpscale.tools.servicemanager.servicemanager import BackgroundService


class BillingService(BackgroundService):
    def __init__(self, name="billing", interval=1, *args, **kwargs):
        super().__init__(name, interval, *args, **kwargs)

    def job(self):
        pass
