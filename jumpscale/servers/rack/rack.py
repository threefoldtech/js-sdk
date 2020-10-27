from gevent import event

from jumpscale.core.base import Base


class ServerRack(Base):
    def __init__(self):
        super().__init__()
        self._servers = dict()
        self._started = set()
        self._running_event = event.Event()

    def _start(self, server_name: str):
        if server_name not in self._started:
            self._servers[server_name].start()
            self._started.add(server_name)

    def _stop(self, server_name: str):
        if server_name in self._started:
            self._servers[server_name].stop()
            self._started.remove(server_name)

    def add(self, server_name, server):
        """Add new server to the rack

        Args:
            name (str): server name
            server (object): server object
        """
        if server_name in self._servers:
            self._stop(server_name)

        self._servers[server_name] = server

    def remove(self, server_name: str):
        """Remove server (Stop it first if running)

        Args:
            server_name (str): server name
        """
        self._stop(server_name)

        if server_name in self._servers:
            self._servers.pop(server_name)

        if server_name in self._started:
            self._started.remove(server_name)

    def start(self, server_name: str = None, wait: bool = False):
        """Start server by its name or start all servers

        Args:
            server_name (str, optional): server name, if None will start all the servers. Defaults to None.
        """
        self._running_event.clear()
        if server_name:
            self._start(server_name)
        else:
            for server_name in self._servers:
                self._start(server_name)

        if wait:
            try:
                self._running_event.wait()
            except KeyboardInterrupt:
                self.stop()

    def stop(self, server_name: str = None):
        """Stop server by its name or stop all running servers

        Args:
            server_name (str, optional): server name, if None will stop all running servers. Defaults to None.
        """
        if server_name:
            self._stop(server_name)
        else:
            for server_name in self._servers:
                self._stop(server_name)
        self._running_event.set()

    def is_running(self, server_name):
        return server_name in self._started
