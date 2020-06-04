from jumpscale.god import j
from jumpscale.core.base import Base, fields


class NginxServer(Base):
    name = fields.String(default="main")
    config_path = fields.String(default="~/sandbox/cfg/nginx/main/nginx.conf")

    def install(self):
        j.sals.process.execute("add-apt-repository ppa:certbot/certbot", showout=True, die=False)
        j.sals.process.execute(
            "apt-get install -y nginx certbot python-certbot-nginx ", showout=True, die=False,
        )

    def start(self):
        nginx = j.sals.nginx.get(self.name)
        nginx.configure()
        nginx.save()
        cmd = j.tools.startupcmd.get(self.name)
        cmd.start_cmd = f"nginx -c {self.config_path}"
        cmd.stop_cmd = f"nginx -c {self.config_path} -s stop"
        cmd.start()

    def stop(self):
        cmd = j.tools.startupcmd.get(self.name)
        cmd.stop()

    def reload(self):
        j.sals.process.execute(f"nginx -c {self.config_path} -s reload")

    def restart(self):
        self.stop()
        self.start()
