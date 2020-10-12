from jumpscale.loader import j


def _get_identifier(notification_type, message):
    return j.data.hash.md5(":".join([notification_type, message]))


class Notification:
    def __init__(self):
        self.id = None
        self.type = None
        self.level = 0
        self.message = None
        self.date = None
        self.unread = None
        self.data = None

    @classmethod
    def loads(cls, value):
        json = j.data.serializers.json.loads(value)
        instance = cls()
        instance.__dict__ = json
        return instance

    @property
    def identifier(self):
        return _get_identifier(self.type, self.message)

    @property
    def json(self):
        return self.__dict__

    def dumps(self):
        return j.data.serializers.json.dumps(self.__dict__)


class NotificationsHandler:
    def __init__(self, service_name):
        self._rkey = f"notifications_{service_name}"
        self._rkey_id = f"notifications_{service_name}:id"
        self._rkey_incr = f"notifications_{service_name}:id:incr"
        self._db = None

    def __dir__(self):
        return ("get", "find", "notification_raise", "count", "reset", "delete", "delete_all")

    @property
    def db(self):
        if self._db is None:
            self._db = j.core.db
        return self._db

    def get(self, notification_id: int = None, identifier: str = None, die: bool = True) -> Notification:
        """Get notification by its id or identifier

        Keyword Arguments:
            notification_id {int} -- notification id (default: {None})
            identifier {str} -- notification identifier (default: {None})
            die {bool} -- flag to raise exception if notification is not found (default: {True})

        Raises:
            j.core.exceptions.NotFound: notification is not found
            j.core.exceptions.Value: invalid arguments

        Returns:
            Notification -- [description]
        """
        if not (notification_id or identifier):
            raise j.core.exceptions.Value("Either notification id or notification identifier are required")

        notification_id = notification_id or self.db.hget(self._rkey_id, identifier)
        if notification_id:
            notification = self.db.hget(self._rkey, notification_id)
            if notification:
                return Notification.loads(notification)
        if die:
            raise j.core.exceptions.NotFound("Requested notification is not found")

    def find(self, message: str = "", start_time: int = None, end_time: int = None,) -> list:

        """Find notifications

        Keyword Arguments:
            message {str} -- filter by notification message (default: {""})
            start_time {int} -- filter by start time (default: {None})
            end_time {int} -- filter by end time (default: {None})

        Returns:
            list on Notification objects
        """

        notifications = []
        items = self.db.hscan_iter(self._rkey)

        for item in items:
            notification = Notification.loads(item[1])

            if message and message.strip().lower() not in notification.message.strip().lower():
                continue

            if start_time and start_time > notification.date:
                continue

            if end_time and end_time < notification.date:
                continue

            notifications.append(notification)
        return sorted(notifications, key=lambda notification: notification.id)

    def notification_raise(
        self,
        message: str,
        notification_type: str = "default_type",
        level: int = 40,
        unread: bool = True,
        data: object = {},
    ) -> Notification:

        """Raise a new notification

        Arguments:
            message {str} -- notification message

        Keyword Arguments:
            notification_type {str} -- notification type (default: {"default_type"})
            level {int} -- notification level (default: {40})

        Returns:
            Notification -- notification object
        """
        if not self.db.is_running():
            return

        notification = Notification()

        notification.message = message
        notification.level = level
        notification.type = notification_type
        notification.unread = unread
        if data:
            notification.data = data
        notification.date = j.data.time.now().timestamp

        self._save(notification)
        return notification

    def count(self) -> int:
        """Gets notifications count

        Returns:
            int -- total number of notifications
        """
        return self.db.hlen(self._rkey)

    def _save(self, notification: Notification):
        """Saves notification object in db

        Arguments:
            notifications {Notifications} -- notifications object
        """
        if not notification.id:
            notification.id = self.db.incr(self._rkey_incr)

        self.db.hset(self._rkey, notification.id, notification.dumps())
        self.db.hset(self._rkey_id, notification.identifier, notification.id)

    def delete(self, notification_id: int = None, identifier: str = None):
        """Delete notification by its id or identifier

        Raises:
            j.core.exceptions.Value: invalid arguments

        Keyword Arguments:
            notification_id {int} -- notification id (default: {None})
            identifier {str} -- notification identifier (default: {None})
        """
        if not (notification_id or identifier):
            raise j.core.exceptions.Value("Either notification id or notification identifier are required")

        notification_id = notification_id or self.db.hget(self._rkey_id, identifier)
        if notification_id:
            self.db.hdel(self._rkey, notification_id)

    def delete_all(self):
        """Deletes all notifications
        """
        self.db.delete(self._rkey, self._rkey_id)

    def reset(self):
        """Delete all notifications and reset the db
        """
        self.delete_all()
        self.db.delete(self._rkey_incr)
