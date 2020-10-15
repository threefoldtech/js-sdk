from abc import ABC, abstractmethod
import gevent

from jumpscale.loader import j
from jumpscale.tools.notificationsqueue.queue import LEVEL


class BackgroundService(ABC):
    def __init__(self, service_name, *args, **kwargs):
        self.name = service_name

    @abstractmethod
    def job(self):
        pass


class StellarService(BackgroundService):
    def __init__(self, *args, **kwargs):
        super().__init__("stellar", *args, **kwargs)
        self.stellar_state = True

    def job(self):
        while True:
            # Check 3 times to make sure service is down
            # print(j.clients.stellar.check_stellar_service())
            retries = 3
            current_state = None
            while retries:
                current_state = j.clients.stellar.check_stellar_service()
                if current_state:
                    break
                retries -= 1

            if current_state != self.stellar_state:
                if current_state:
                    j.tools.notificationsqueue.push("Stellar service is now up", level=LEVEL.INFO)
                else:
                    j.tools.notificationsqueue.push("Stellar service is now down", level=LEVEL.ERROR)
            print("done")
            gevent.sleep(10)
