from jumpscale.god import j
from jumpscale.core.base import Base, fields


class NginxServer(Base):
    name = fields.String(default="main")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_path = j.sals.fs.join_paths(j.core.dirs.CFGDIR, "nginx", self.name, "nginx.conf")

    def install(self):
        """
        install nginx and certbot
        """
        j.sals.process.execute(
            "apt-get install -y software-properties-common;"
            "add-apt-repository universe;"
            "add-apt-repository ppa:certbot/certbot;"
            "apt-get update;"
            "apt-get install -y nginx certbot python-certbot-nginx;",
            showout=True,
            die=False,
            env={"DEBIAN_FRONTEND": "noninteractive"},
        )

    def start(self):
        """
        start nginx server using your config path
        """
        nginx = j.sals.nginx.get(self.name)
        nginx.configure()
        nginx.save()
        cmd = j.tools.startupcmd.get(self.name)
        cmd.start_cmd = f"nginx -c {self.config_path}"
        cmd.process_strings_regex = [
            r"nginx.* \-c {CONFIG_PATH}".format(CONFIG_PATH=j.sals.fs.expanduser(self.config_path))
        ]
        if not cmd.is_running():
            cmd.start()

    def stop(self):
        """
        stop nginx server
        """
        cmd = j.tools.startupcmd.get(self.name)
        cmd.stop_cmd = f"nginx -c {self.config_path} -s stop"
        cmd.stop()

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
