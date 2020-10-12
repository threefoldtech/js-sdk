import gevent
from gevent.pool import Pool
from signal import SIGTERM, SIGKILL

from .services import stellar_service

from jumpscale.loader import j
from jumpscale.core.base import Base

MAX_GREENLETS = 10


class NotificationService(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pool = Pool(MAX_GREENLETS)

    def start(self):
        # handle signals
        for signal_type in (SIGTERM, SIGKILL):
            gevent.signal(signal_type, self.stop)

        # spawn stellar check service
        self.pool.spawn(stellar_service)

    def stop(self):
        self.pool.kill()
