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
        self.ssh_server1 = j.clients.sshclient.get(BACKUP_SERVER1)
        self.ssh_server2 = j.clients.sshclient.get(BACKUP_SERVER2)

    @actor_method
    def server_connect(self, threebot_name:str, passwd:str):
        try:
            user = self.explorer.users.get(name=threebot_name)
        except requests.exceptions.HTTPError:
            raise j.exceptions.NotFound(f"Threebot name {threebot_name} is not found")

        public_key = user.pubkey
        public_key_unhex = binascii.unhexlify(public_key)
        sign = nacl.signing.VerifyKey(public_key_unhex)
        password_backup = sign.verify(passwd.encode()).decode()

        self._htpasswd(self.ssh_server1, threebot_name, password_backup)
        self._htpasswd(self.ssh_server2, threebot_name, password_backup)

        return [self.ssh_server1.host, self.ssh_server2.host]

    def _htpasswd(self, server, threebot_name, password_backup):
        server.sshclient.run(f"cd ~/backup; htpasswd -Bb .htpasswd {threebot_name} {password_backup}")

Actor = Backup