from jumpscale.loader import j
from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.tools.notificationsqueue.queue import LEVEL


class DiskCheckService(BackgroundService):
    def __init__(self, name="admin_diskcheck", interval=60 * 60 * 12, *args, **kwargs):
        """
            Check disk space every 12 hours
        """
        super().__init__(name, interval, *args, **kwargs)

    def job(self):
        disk_obj = j.sals.fs.shutil.disk_usage("/")
        free_disk_space = disk_obj.free // (1024.0 ** 3)
        if free_disk_space <= 10:
            j.logger.warning("[Admin Package - Disk Check Service] Your free disk space is less than 10 GBs")
            j.tools.notificationsqueue.push(
                "Your free disk space is less than 10 GBs", category="Health check", level=LEVEL.WARNING
            )


service = DiskCheckService()
