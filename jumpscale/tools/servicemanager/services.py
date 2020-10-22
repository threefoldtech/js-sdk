from abc import ABC, abstractmethod

from jumpscale.loader import j
from jumpscale.tools.notificationsqueue.queue import LEVEL

# TODO: handle case when service interval is smaller than service runtime


class BackgroundService(ABC):
    def __init__(self, service_name, interval=60, *args, **kwargs):
        """Abstract base class for background services managed by the service manager

        Arguments:
            service_name {str} -- identifier of the service
            interval {int} -- scheduled job is executed every interval (in seconds)
        """
        self.name = service_name
        self.interval = interval

    @abstractmethod
    def job(self):
        """
        Background job to be scheduled.
        Should be implemented by any service that inherits from this class
        """
        pass


class StellarService(BackgroundService):
    def __init__(self, name="stellar", interval=60, *args, **kwargs):
        """
            Check stellar service state every 1 min
        """
        super().__init__(name, interval, *args, **kwargs)
        self.stellar_state = True

    def job(self):
        # Check 3 times to make sure service is down
        retries = 3
        current_state = None
        while retries:
            try:
                current_state = j.clients.stellar.check_stellar_service()
            except Exception:
                current_state = False
            if current_state:
                break
            retries -= 1

        if current_state != self.stellar_state:
            self.stellar_state = current_state
            if current_state:
                j.logger.info("[Stellar Service] Stellar services are now reachable")
                j.tools.notificationsqueue.push(
                    "Stellar services are now reachable", category="Stellar", level=LEVEL.INFO
                )
            else:
                j.logger.error("[Stellar Service] Could not reach stellar")
                j.tools.notificationsqueue.push("Could not reach stellar", category="Stellar", level=LEVEL.ERROR)


class DiskCheckService(BackgroundService):
    def __init__(self, name="disk-check", interval=60 * 60 * 12, *args, **kwargs):
        """
            Check disk space every 12 hours
        """
        super().__init__(name, interval, *args, **kwargs)

    def job(self):
        disk_obj = j.sals.fs.shutil.disk_usage("/")
        free_disk_space = disk_obj.free // (1024.0 ** 3)
        if free_disk_space <= 10:
            j.logger.warning("[Disk Check Service] Your free disk space is less than 10 GBs")
            j.tools.notificationsqueue.push(
                "Your free disk space is less than 10 GBs", category="Health check", level=LEVEL.WARNING
            )
