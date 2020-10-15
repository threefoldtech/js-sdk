import gevent
from gevent.pool import Pool
from gevent import GreenletExit
from signal import SIGTERM, SIGKILL

from .services import StellarService

from jumpscale.loader import j
from jumpscale.core.base import Base

MAX_GREENLETS = 10

DEFAULT_SERVICES = {"stellar": StellarService()}


# FIXME: Can not kill services before they run at least once and sleep
# because that causes kill() call to hang and does not kill greenlets


class ServiceManager(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pool = Pool(MAX_GREENLETS)
        self.services = DEFAULT_SERVICES.copy()
        self._greenlets = {}

    def start(self):
        # handle signals
        for signal_type in (SIGTERM, SIGKILL):
            gevent.signal(signal_type, self.stop)

        # spawn default services
        for service in self.services.values():
            self._greenlets[service.name] = self.pool.spawn(service.job)
            if not self._greenlets[service.name].started:
                raise j.exceptions.Runtime(f"Failed to start {service.name} service")

    # # TODO: Stop greenlets gracefully
    # def stop(self):
    #     try:
    #         # TODO: check all greenlets are stopped
    #         self.pool.join()
    #     except Exception as e:
    #         raise j.exceptions.Runtime(f"Error while stopping services: {str(e)}")

    def kill(self):
        # retries due to bad behaviour of kill (sometimes hangs and doesnot kill greenlets)
        retries = 3
        while retries and self.pool.greenlets:
            self.pool.kill(block=False)
            retries -= 1
            gevent.sleep(1)
        print(retries)

    def add_service(self, service):
        # TODO: check if instance of the service is already running -> kill greenlet and spawn a new one?
        if service.name in self._greenlets:
            raise j.exceptions.Value(f"Service {service.name} is already running")
        self._greenlets[service.name] = self.pool.spawn(service.job)
        if not self._greenlets[service.name].started:
            raise j.exceptions.Runtime(f"Failed to start {service.name} service")
        self.services[service.name] = service

    def stop_service(self, service_name):
        if service_name not in self._greenlets:
            raise j.exceptions.Value(f"Service {service_name} is not running")

        # retries due to bad behaviour of killone (sometimes hangs and doesnot kill greenlet)
        retries = 10
        while retries and not self._greenlets[service_name].dead:
            self.pool.killone(self._greenlets[service_name], block=False)
            retries -= 1
            gevent.sleep(1)

        print(retries)
        self._greenlets.pop(service_name)
