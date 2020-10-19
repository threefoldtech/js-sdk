from abc import ABC, abstractmethod
import gevent

from jumpscale.loader import j
from jumpscale.tools.notificationsqueue.queue import LEVEL

# TODO: handle case when service interval is smaller than service runtime


class BackgroundService(ABC):
    def __init__(self, service_name, interval=60, *args, **kwargs):
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
    def __init__(self, name="stellar", interval=15, *args, **kwargs):
        super().__init__(name, interval, *args, **kwargs)
        self.stellar_state = True

    def job(self):
        # Check 3 times to make sure service is down
        retries = 3
        current_state = None
        while retries:
            # TODO: handle this request failure -> on internet down raises exception
            current_state = j.clients.stellar.check_stellar_service()
            if current_state:
                break
            retries -= 1

        # if current_state != self.stellar_state:
        if current_state:
            j.tools.notificationsqueue.push("Stellar service is now up", level=LEVEL.INFO)
        else:
            j.tools.notificationsqueue.push("Stellar service is now down", level=LEVEL.ERROR)
        print("[Stellar Service] Done")
