from jumpscale.loader import j
from jumpscale.core.base import Base, fields
import shutil


class RedisServer(Base):

    host = fields.String(default="127.0.0.1")
    port = fields.Integer(default=6379)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cmd = j.tools.startupcmd.get(f"redis_{self.instance_name}")

    @property
    def cmd(self):
        self._cmd.start_cmd = f"redis-server --bind {self.host} --port {self.port}"
        self._cmd.ports = [self.port]
        return self._cmd

    @property
    def installed(self) -> bool:
        """check if redis server is installed

        Returns:
            bool: True if redis server is installed
        """
        return shutil.which("redis-server")

    def start(self):
        """start redis server in tmux
        """
        # Port is not busy (Redis is not started)
        if not j.sals.nettools.tcp_connection_test(self.host, self.port, timeout=1):
            self.cmd.start()

    def stop(self):
        """stop redis server
        """
        self.cmd.stop(force=True)

    def restart(self):
        """restart redis server
        """
        self.stop()
        self.start()
