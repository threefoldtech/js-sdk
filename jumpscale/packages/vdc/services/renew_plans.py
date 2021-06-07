import gevent
from jumpscale.loader import j

from jumpscale.clients.stellar import TRANSACTION_FEES
from jumpscale.sals.vdc import VDCFACTORY
from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.sals.vdc.size import INITIAL_RESERVATION_DURATION

RENEW_PLANS_QUEUE = "vdc:plan_renewals"
UNHANDLED_RENEWS = "vdc:plan_renewals:unhandled"


class RenewPlans(BackgroundService):
    def __init__(self, interval=60 * 60, *args, **kwargs):
        """Service to renew plans in the background
        """
        super().__init__(interval, *args, **kwargs)

    def job(self):
        while True:
            vdc_name = None
            if j.core.db.llen(UNHANDLED_RENEWS) > 0:
                vdc_name = j.core.db.lpop(UNHANDLED_RENEWS)
            else:
                vdc_name = j.core.db.lpop(RENEW_PLANS_QUEUE)
            if vdc_name:
                j.logger.info(f"renewing plan for {vdc_name}")
                try:
                    j.core.db.lpush(
                        UNHANDLED_RENEWS
                    )  # push it here instead of on exception just in case anything else goes wrong
                    vdc = j.sals.vdc.get(vdc_name)
                    vdc.load_info()
                    deployer = vdc.get_deployer()
                    deployer.renew_plan(14 - INITIAL_RESERVATION_DURATION / 24)
                except Exception as e:
                    raise e
                else:
                    j.core.db.lrem(UNHANDLED_RENEWS, 0, vdc_name)
            gevent.sleep(1)


service = RenewPlans()
