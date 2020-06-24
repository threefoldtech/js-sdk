from jumpscale.god import j
from jumpscale.core.base import Base, fields
import shutil


class RedisServer(Base):
    name = fields.String(default="redis")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cmd = j.tools.startupcmd.get(self.name)

    @property
    def installed(self) -> bool:
        """check if redis server is installed

        Returns:
            bool: True if redis server is installed
        """
        return shutil.which("redis-server")

    def start(self, host: str = "127.0.0.1", port: int = 6379):
        """start redis server in tmux

        Args:
            host (str, optional): redis bind address. Defaults to "127.0.0.1".
            port (int, optional): redis port. Defaults to 6379.
        """
        # Port is not busy (Redis is not started)
        if not j.sals.nettools.tcp_connection_test("127.0.0.1", 6379, timeout=1):
            self.cmd.start_cmd = f"redis-server --bind {host} --port {port}"
            self.cmd.ports = [port]
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
