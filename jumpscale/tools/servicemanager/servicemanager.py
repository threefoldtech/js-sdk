import gevent
from signal import SIGTERM, SIGKILL

from .services import StellarService, DiskCheckService

from jumpscale.loader import j
from jumpscale.core.base import Base

DEFAULT_SERVICES = {"stellar": StellarService(), "test": DiskCheckService()}

# TODO: add support for non-periodic tasks


class ServiceManager(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.services = DEFAULT_SERVICES.copy()
        self._greenlets = {}

    def __callback(self, greenlet):
        """Callback runs after greenlet finishes execution

        Arguments:
            greenlet {Greenlet} -- greenlet object
        """
        g = self._greenlets.pop(greenlet.name)
        service = g.service
        self._schedule_service(service)

    def _schedule_service(self, service):
        """Schedule a service to run its job after interval specified by the service

        Arguments:
            service {BackgroundService} -- background service object
        """
        greenlet = gevent.spawn_later(service.interval, service.job)
        greenlet.link(self.__callback)
        self._greenlets[greenlet.name] = greenlet
        self._greenlets[greenlet.name].service = service

    def start(self):
        """Start the service manager and schedule default services
        """
        # handle signals
        for signal_type in (SIGTERM, SIGKILL):
            gevent.signal(signal_type, self.stop)

        # schedule default services
        for service in self.services.values():
            self._schedule_service(service)

    def stop(self):
        """Stop all background services
        """
        for service in self.services:
            self.stop_service(service)

    def add_service(self, service):
        """Add a new background service to be managed and scheduled by the service manager

        Arguments:
            service {BackgroundService} -- background service object to be scheduled
        """
        if service.name in self.services:
            raise j.exceptions.Value(f"Service with name {service.name} already exists")

        # TODO: check if instance of the service is already running -> kill greenlet and spawn a new one?
        for service_obj in self.services:
            # TODO: better way?
            if type(service) == type(service_obj):
                raise j.exceptions.Value(f"Service {service.name} is already running")

        self._schedule_service(service)
        self.services[service.name] = service

    def stop_service(self, service_name):
        """Stop a background service

        Arguments:
            service_name {str} -- name of the service to be stopped
        """
        if service_name not in self.services:
            raise j.exceptions.Value(f"Service {service_name} is not running")

        for key, greenlet in self._greenlets.items():
            if greenlet.service.name == service_name:
                greenlet.unlink(self.__callback)
                self._greenlets.pop(key)
                break
