import gevent
from jumpscale.loader import j

from jumpscale.sals.vdc import VDCFACTORY
from jumpscale.sals.vdc.grace_period import GRACE_PERIOD_FACTORY
from jumpscale.tools.servicemanager.servicemanager import BackgroundService


class GracePeriodWatcher(BackgroundService):
    def __init__(self, interval=60 * 60, *args, **kwargs):
        """Provisioning wallet service that will run every hour to update the status of grace period
        """
        super().__init__(interval, *args, **kwargs)

    def job(self):
        j.logger.info("Grace period service")
        for vdc_name in VDCFACTORY.list_all():
            vdc_instance = VDCFACTORY.find(vdc_name)
            if GRACE_PERIOD_FACTORY.is_eligible(vdc_instance):
                j.logger.info(f"{vdc_name} enters grace period")
                try:
                    GRACE_PERIOD_FACTORY.start_grace_period(vdc_instance)
                except Exception as e:
                    j.logger.critical(f"Error starting grace period for vdc: {vdc_name}:\n{str(e)}")
            gevent.sleep(0.1)

        for gp in GRACE_PERIOD_FACTORY.list_active_grace_periods():
            try:
                gp.update_status()
            except Exception as e:
                j.logger.critical(f"Error updating grace period status: {gp.instance_name}:\n{str(e)}")
            gevent.sleep(0.1)


service = GracePeriodWatcher()
