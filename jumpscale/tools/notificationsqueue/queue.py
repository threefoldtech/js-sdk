from enum import Enum

from jumpscale.loader import j
from jumpscale.core.base import Base


class LEVEL(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Notification:
    def __init__(self):
        self.id = None
        self.category = None
        self.level = 0
        self.message = None
        self.date = None

    @classmethod
    def loads(cls, value):
        json = j.data.serializers.json.loads(value)
        instance = cls()
        instance.__dict__ = json
        return instance

    @property
    def json(self):
        return self.__dict__

    def dumps(self):
        return j.data.serializers.json.dumps(self.__dict__)


class NotificationsQueue:
    def __init__(self, *args, **kwargs):
        self._rkey = "queue:notifications"
        self._rkey_incr = "queue:notifications:id:incr"
        self._rkey_seen = "list:notifications:seen"
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = j.core.db
        return self._db

    def push(self, message: str, category: str = "default", level: LEVEL = LEVEL.INFO):
        """Push a new notification

        Arguments:
            message {str} -- notification message

        Keyword Arguments:
            type {str} -- notification type (default: {"default"})
            level {LEVEL} -- notification level (default: {LEVEL.INFO})
        """
        if not self.db.is_running():
            return

        if not isinstance(level, LEVEL):
            raise j.exceptions.Value(f"{level} is not of type: LEVEL")

        notification = Notification()

        notification.message = message
        notification.level = level.value
        notification.category = category
        notification.date = j.data.time.now().timestamp
        notification.id = self.db.incr(self._rkey_incr)

        self.db.rpush(self._rkey, notification.dumps())

    def fetch(self, count: int = -1) -> list:
        """Fetch notifications from queue

        Keyword Arguments:
            count {int} -- number of notifications to fetch (default: {-1} = all notifications)

        Returns:
            list on Notification objects
        """

        # Transactional pipeline to fetch notifications and trim them from the queue
        # TODO: better implementation of if/elses
        ret_notifications = []
        if count == -1:
            new_notifications = self.db.lrange(self._rkey, 0, -1)
            self.db.delete(self._rkey)
            self.db.ltrim(self._rkey_seen, 0, 9)
            # check if new notifications count less than 10 to append the old
            if len(new_notifications) < 10:
                old_notifications = self.db.lrange(self._rkey_seen, len(new_notifications) - 10, -1)
                ret_notifications += old_notifications[::-1]
            ret_notifications += new_notifications
            # update the old notifications list with the new
            if new_notifications:
                self.db.lpush(self._rkey_seen, *new_notifications)
        else:
            ret_notifications = self.db.lrange(self._rkey, 0, count - 1)  # -1 => See https://redis.io/commands/lrange
            if self.count() == 1:
                self.db.delete(self._rkey)
            else:
                self.db.ltrim(self._rkey, count, -1)

        return [Notification.loads(notification) for notification in ret_notifications]

    def count(self) -> int:
        """Get notifications count

        Returns:
            int -- total number of notifications
        """
        return self.db.llen(self._rkey)

    def clear(self):
        """Delete all notifications
        """
        self.db.delete(self._rkey)
        self.db.delete(self._rkey_seen)
