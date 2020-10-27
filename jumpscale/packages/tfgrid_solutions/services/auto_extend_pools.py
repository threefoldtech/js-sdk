from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.packages.tfgrid_solutions.utils import auto_extend_pools
from jumpscale.loader import j


class AutoExtendPoolService(BackgroundService):
    def __init__(self, name="threebot_deployer_auto_extend_pools", interval=60 * 60 * 24, *args, **kwargs):
        """
        Test service that runs every 1 day
        """
        super().__init__(name, interval, *args, **kwargs)

    def job(self):
        auto_extend_pools()
        j.logger.info("Auto extend pool service done successfully")


service = AutoExtendPoolService()
