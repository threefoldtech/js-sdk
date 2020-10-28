"""
### Description

Service manager is the service that monitors and manages background services through gevent greenlets.
Each service defines an interval to define the period of the service and defines also a job method that is run each period.
Any service should:
- Inherit from `BackgroundService` class defined here: `from jumpscale.tools.servicemanager.servicemanager import BackgroundService`
- Define a name and interval in the constructor
- Implement the abtsract `job` method of the `BackgroundService` base class.

### How it schedules services

The service manager uses gevent greenlets to run jobs. It spawns the job in a greenlet after its interval period.
Rescheduling the service job is done in by linking a callback to the greenlet which is run after the greenlet finishes.
After the greenlet finishes execution the callback is fired which schedules the job to be run again after anothre interval.

To add a service  to the service manager you should call the `add_service` method which takes the package path as a parameter.
It loads the file in this path as a module and gets the service object defined in the service.py file.

### Example service

```python3
from jumpscale.tools.servicemanager.servicemanager import BackgroundService

class TestService(BackgroundService):
    def __init__(self, name="test", interval=20, *args, **kwargs):
        '''
            Test service that runs every 1 hour
        '''
        super().__init__(name, interval, *args, **kwargs)

    def job(self):
        print("[Test Service] Done")

service = TestService()
```
"""


from abc import ABC, abstractmethod
import gevent
from signal import SIGTERM, SIGKILL

from jumpscale.loader import j
from jumpscale.core.base import Base


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
# TODO: add support for cron time string format (day of the week, month, day of the month, hour, minute)
# TODO: configurable services
# TODO: add support for services not in packages
class ServiceManager(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.services = {}
        self._scheduled = {}
        self._running = {}

    def __callback(self, greenlet):
        """Callback runs after greenlet finishes execution

        Arguments:
            greenlet {Greenlet}: greenlet object
        """
        greenlet.unlink(self.__callback)
        self._running.pop(greenlet.service.name)

    def _schedule_service(self, service):
        """Runs a service job and schedules it to run again every period (interval) specified by the service

        Arguments:
            service {BackgroundService}: background service object
        """
        greenlet = gevent.spawn(service.job)
        greenlet.link(self.__callback)
        self._running[service.name] = greenlet
        self._running[service.name].service = service
        self._scheduled[service.name] = gevent.spawn_later(service.interval, self._schedule_service, service=service)

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
            service_path {str}: absolute path of the service file
        """

        module = j.tools.codeloader.load_python_module(service_path)
        service = module.service

        if service.name in self.services:
            raise j.exceptions.Value(f"Service with name {service.name} already exists")

        # TODO: check if instance of the service is already running -> kill greenlet and spawn a new one?
        for service_obj in self.services.values():
            # better way?
            if isinstance(service, type(service_obj)):
                raise j.exceptions.Runtime(f"A {type(service).__name__} instance is already running")

        self._schedule_service(service)
        self.services[service.name] = dict(path=service_path)

    def stop_service(self, service_name, block=True):
        """Stop a running background service gracefully and unschedules it if it's scheduled to run again

        Arguments:
            service_name {str}: name of the service to be stopped
            block {bool}: wait for service job to finish. if False, service job will be killed without waiting
        """
        if service_name not in self.services:
            raise j.exceptions.Value(f"Service {service_name} is not running")

        # wait for service to finish if it's already running
        if service_name in self._running:
            greenlet = self._running[service_name]
            if block:
                try:
                    greenlet.join()
                except Exception as e:
                    raise j.exceptions.Runtime(f"Exception on waiting for greenlet: {str(e)}")
            else:
                try:
                    greenlet.kill()
                except Exception as e:
                    raise j.exceptions.Runtime(f"Exception on killing greenlet: {str(e)}")
                if not greenlet.dead:
                    raise j.exceptions.Runtime("Failed to kill running greenlet")

        # unschedule service if it's scheduled to run again
        if service_name in self._scheduled:
            greenlet = self._scheduled[service_name]
            greenlet.kill()
            if not greenlet.dead:
                raise j.exceptions.Runtime("Failed to unschedule greenlet")
            self._scheduled.pop(service_name)

        self.services.pop(service_name)
