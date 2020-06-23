from jumpscale.god import j
from jumpscale.core.base import Base, fields


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
        return j.sals.process.execute('which redis-server')[0] == 0

    def start(self, host: str = "127.0.0.1", port: int = 6379):
        """start redis server in tmux

        Args:
            host (str, optional): redis bind address. Defaults to "127.0.0.1".
            port (int, optional): redis port. Defaults to 6379.
        """
        self.cmd.start_cmd = f"redis-server --bind {host} --port {port}"
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
