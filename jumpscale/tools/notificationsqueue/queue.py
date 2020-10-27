from enum import Enum

from jumpscale.loader import j


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
        self._seen_list_max_size = 10
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = j.core.db
        return self._db

    def push(self, message: str, category: str = "default", level: LEVEL = LEVEL.INFO):
        """Push a new notification

        Arguments:
            message {str}: notification message

        Keyword Arguments:
            type {str}: notification type (default: {"default"})
            level {LEVEL}: notification level (default: {LEVEL.INFO})
        """
        if not self.db.is_running():
            return

        if not isinstance(level, LEVEL):
            raise j.exceptions.Value(f"{level} is not of type: LEVEL")

        notification = Notification()

        notification.message = message
        notification.level = level.value
        notification.category = category
        notification.date = j.data.time.utcnow().timestamp
        notification.id = self.db.incr(self._rkey_incr)

        self.db.lpush(self._rkey, notification.dumps())

    def fetch(self, count: int = -1) -> list:
        """Fetch notifications from queue

        Keyword Arguments:
            count {int}: number of new notifications to fetch (default: {-1} = new notifications only)
                           if new notifications < count => will return list of (new notifications + old notifications) with length = count

        Returns:
            list: Notification objects
        """
        get_all_new = count == -1
        ret_notifications_count = 0

        if get_all_new:
            ret_notifications_count = self.count()
            if ret_notifications_count == 0:
                return []
        else:
            ret_notifications_count = count

        # Transactional pipeline to fetch notifications from the queue and save them in the seen list
        p = self.db.pipeline()
        p.multi()

        for _ in range(ret_notifications_count):
            p.rpoplpush(self._rkey, self._rkey_seen)
        p.lrange(self._rkey_seen, 0, ret_notifications_count - 1)
        p.ltrim(self._rkey_seen, 0, self._seen_list_max_size - 1)

        notifications = p.execute()

        return [Notification.loads(notification) for notification in notifications[-2]]  # -2 = result of lrange command

    def count(self) -> int:
        """Get notifications count

        Returns:
            int: total number of notifications
        """
        return self.db.llen(self._rkey)

    def clear(self):
        """Delete all notifications
        """
        self.db.delete(self._rkey)
        self.db.delete(self._rkey_seen)
