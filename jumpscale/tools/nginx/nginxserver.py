import re
import shutil
from jumpscale.loader import j
from jumpscale.core.base import Base, fields


class NginxServer(Base):
    server_name = fields.String(default="main")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_path = j.sals.fs.join_paths(j.core.dirs.CFGDIR, "nginx", self.server_name, "nginx.conf")

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
        nginx = j.sals.nginx.get(self.server_name)
        nginx.configure()
        cmd = j.tools.startupcmd.get(f"nginx_{self.server_name}")
        cmd.start_cmd = f"nginx -c {self.config_path}"
        cmd.stop_cmd = f"nginx -c {self.config_path} -s stop"
        cmd.path = nginx.cfg_dir
        cmd.timeout = 10
        cmd.check_cmd = f'test -f "{self.get_pid_file_path()}"'
        cmd.process_strings_regex = [self.check_command_string]
        cmd.save()
        if not cmd.is_running():
            cmd.start()

    def stop(self):
        """
        stop nginx server
        """
        cmd = j.tools.startupcmd.get(f"nginx_{self.server_name}")
        cmd.stop()

    def is_running(self):
        """Check if nginxserver is running
        
        Returns:
            bool: True if Nginx master process is running, otherwise False.
        """
        try:
            pid_file_path = self.get_pid_file_path()
        except FileNotFoundError:
            # nginx conf file created after the server run for first time, so this possible first time to run the threebot server.
            j.logger.warning(f"can't find the Nginx configuration file {self.config_path}, not created yet?")
            return False
        return j.sals.fs.exists(pid_file_path)

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

    def get_pid_file_path(self):
        """Return the path to nginx.pid file as specified in the Nginx configuration file
        Raises:
            j.exceptions.Runtime: if pid directive not found in the Nginx configuration file
            FileNotFoundError: if the Nginx configuration file not found
        Returns:
            str: the path to the file that process ID of the Nginx master process is written to.
        """
        with open(j.sals.fs.expanduser(self.config_path), "r") as file:
            for line in file:
                m = re.match(r"^pid\s+(.*);", line)
                if m:
                    pid_file_path = m.group(1)
                    return pid_file_path
            else:
                raise j.exceptions.Runtime(
                    f"can't read the PID directive in the Nginx configuration file {self.config_path}"
                )
