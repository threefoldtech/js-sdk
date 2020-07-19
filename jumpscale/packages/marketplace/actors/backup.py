from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.loader import j
import nacl.secret
import nacl.utils
import  requests
import nacl.signing
import  binascii



BACKUP_SERVER1 = "backup_server1"
BACKUP_SERVER2 = "backup_server2"

class Backup(BaseActor):
    def __init__(self):
        super().__init__()
        self.explorer = j.clients.explorer.get_default()

    @actor_method
    def server_connect(self, threebot_name:str, passwd:str):
        try:
            user = self.explorer.users.get(name=threebot_name)
        except requests.exceptions.HTTPError:
            raise j.exceptions.NotFound(f"Threebot name {threebot_name} is not found")

        public_key = user.pubkey
        public_key_hex = binascii.hexlify(public_key)
        sign = nacl.signing.VerifyKey(public_key_hex)
        password_backup = sign.verify(passwd).decode()

        ssh_server1 = j.clients.sshclient.get(BACKUP_SERVER1)
        ssh_server2 = j.clients.sshclient.get(BACKUP_SERVER2)

        self._htpasswd(ssh_server1, threebot_name, password_backup)
        self._htpasswd(ssh_server2, threebot_name, password_backup)
        return ssh_server1.host, ssh_server2.host

    def _htpasswd(self, server, threebot_name, password_backup):
        server.sshclient.run(f"cd ~/backup; htpasswd -Bb .htpasswd {threebot_name} {password_backup}")

Actor = Backup
