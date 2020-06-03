from jumpscale.god import j
from jumpscale.core.base import Base, fields


class NginxServer(Base):
    name = fields.String(default="main")
    path = fields.String(default="~/sandbox/cfg/nginx/main/nginx.conf")

    def install(self):
        j.sals.process.execute("apt install nginx", showout=True, die=False)

    def start(self):
        nginx = j.sals.nginx.get(self.name)
        nginx.configure()
        nginx.save()
        cmd = j.tools.startupcmd.get(self.name)
        cmd.start_cmd = f"nginx -c {self.path}"
        cmd.stop_cmd = "service nginx stop"
        cmd.start()

    def stop(self):
        cmd = j.tools.startupcmd.get(self.name)
        cmd.stop()
        j.sals.process.execute("pkill -9 nginx")

    def reload(self):
        j.sals.process.execute("service nginx reload")

    def restart(self):
        j.sals.process.execute("service nginx restart")
