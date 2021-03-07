from jumpscale.loader import j
from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.tools.notificationsqueue.queue import LEVEL
from crontab import CronTab


class StellarService(BackgroundService):
    def __init__(self, interval=CronTab("* * * * *"), *args, **kwargs):
        """
            Check stellar service state every 1 min
        """
        super().__init__(interval, *args, **kwargs)
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
                j.logger.info("[Admin Package - Stellar Service] Stellar services are now reachable")
                j.tools.notificationsqueue.push(
                    "Stellar services are now reachable", category="Stellar", level=LEVEL.INFO
                )
            else:
                j.logger.error("[Admin Package - Stellar Service] Could not reach stellar")
                j.tools.notificationsqueue.push("Could not reach stellar", category="Stellar", level=LEVEL.ERROR)


service = StellarService()
