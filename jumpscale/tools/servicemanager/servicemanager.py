from abc import ABC, abstractmethod
import gevent
from signal import SIGTERM, SIGKILL

from jumpscale.loader import j
from jumpscale.core.base import Base, fields


class BackgroundService(ABC):
    def __init__(self, service_name, interval=60, *args, **kwargs):
        """Abstract base class for background services managed by the service manager

        Arguments:
            service_name {str} -- identifier of the service
            interval {int} -- scheduled job is executed every interval (in seconds)
        """
        self.name = service_name
        self.interval = interval

    @abstractmethod
    def job(self):
        """
        Background job to be scheduled.
        Should be implemented by any service that inherits from this class
        """
        pass


# TODO: add support for non-periodic tasks
# TODO: configurable services
# TODO: add support for services not in packages
class ServiceManager(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.services = {}
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
            module = j.tools.codeloader.load_python_module(service["path"])
            self._schedule_service(module.service)

    def stop(self):
        """Stop all background services
        """

        for service in list(self.services.keys()):
            self.stop_service(service)

    def add_service(self, service_path):
        """Add a new background service to be managed and scheduled by the service manager

        Arguments:
            service_path {str} -- absolute path of the service file
        """

        module = j.tools.codeloader.load_python_module(service_path)
        service = module.service

        if service.name in self.services:
            raise j.exceptions.Value(f"Service with name {service.name} already exists")

        # TODO: check if instance of the service is already running -> kill greenlet and spawn a new one?
        for service_obj in self.services.values():
            # better way?
            if isinstance(service, type(service_obj)):
                raise j.exceptions.Value(f"A {type(service).__name__} instance is already running")

        self._schedule_service(service)
        self.services[service.name] = dict(path=service_path)

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
        self.services.pop(service_name)
