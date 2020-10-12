import gevent
from .notificationshandler import NotificationsHandler

from jumpscale.loader import j

from enum import Enum


class StellarStatus(Enum):
    true = "up"
    false = "down"


def stellar_service():
    while True:
        retries = 3
        while retries:
            current_state = j.clients.stellar.check_stellar_service()
            if current_state:
                break
            retries -= 1

        handler = NotificationsHandler("stellar")
        notifications = handler.find()  # get all notifications
        if notifications:
            # Create new notification only if state changed
            last_state = notifications[-1].data["previous_state"]
            if current_state != last_state:
                handler.notification_raise(
                    message=f"Stellar service is now {StellarStatus[current_state]}",
                    data={"previous_state": StellarStatus[current_state]},
                )

        # print(f"{j.data.time.now().timestamp}: {j.clients.stellar.check_stellar_service()}")

        gevent.sleep(2)
