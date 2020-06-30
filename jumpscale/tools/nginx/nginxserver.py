from jumpscale.loader import j
from jumpscale.core.base import Base, fields
import shutil


class NginxServer(Base):
    name = fields.String(default="main")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_path = j.sals.fs.join_paths(j.core.dirs.CFGDIR, "nginx", self.name, "nginx.conf")

    @property
    def check_command_string(self):
        return r"nginx.* \-c {CONFIG_PATH}".format(CONFIG_PATH=j.sals.fs.expanduser(self.config_path))

    @property
    def installed(self) -> bool:
        """check if nginx is installed

        Returns:
            bool: True if nginx is installed
        """
        return shutil.which("nginx")

    def start(self):
        """
        start nginx server using your config path
        """
        nginx = j.sals.nginx.get(self.name)
        nginx.configure()
        nginx.save()
        cmd = j.tools.startupcmd.get(f"nginx_{self.name}")
        cmd.start_cmd = f"nginx -c {self.config_path}"
        cmd.stop_cmd = f"nginx -c {self.config_path} -s stop"
        cmd.path = nginx.cfg_dir
        cmd.timeout = 10
        cmd.process_strings_regex = [self.check_command_string]
        cmd.save()
        if not cmd.is_running():
            cmd.start()

    def stop(self):
        """
        stop nginx server
        """
        cmd = j.tools.startupcmd.get(f"nginx_{self.name}")
        cmd.stop()

    def is_running(self):
        """
        Check if nginxserver is running
        """
        return j.tools.startupcmd.get(f"nginx_{self.name}").is_running()

    def reload(self):
        """
        reload nginx server using your config path
        """
        j.sals.process.execute(f"nginx -c {self.config_path} -s reload")

    def restart(self):
        """
        restart nginx server
        """
        self.stop()
        self.start()
