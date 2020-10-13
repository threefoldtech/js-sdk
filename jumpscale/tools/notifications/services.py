import gevent
from .notificationshandler import NotificationsHandler

from jumpscale.loader import j


class StellarService:
    handler = NotificationsHandler("stellar")


# def get_stellar_notifications():
#     return handler.find()


def stellar_service():
    while True:
        retries = 3
        current_state = None
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
            print("stellar state", current_state, " :: ", last_state)
            if current_state != last_state:
                message = (current_state and "Stellar service is now up") or "Stellar service is now down"
                handler.notification_raise(
                    message=message, data={"previous_state": current_state},
                )
        else:
            print("stellar is up", current_state)
            message = (current_state and "Stellar service is now up") or "Stellar service is now down"
            handler.notification_raise(
                message=message, data={"previous_state": current_state},
            )

        # print(f"{j.data.time.now().timestamp}: {j.clients.stellar.check_stellar_service()}")

        gevent.sleep(10)
