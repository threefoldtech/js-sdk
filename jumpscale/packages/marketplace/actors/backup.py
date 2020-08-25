from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.loader import j
import nacl.secret
import nacl.utils
import requests
import nacl.signing
import binascii
from nacl.public import Box
import nacl.encoding

BACKUP_SERVER1 = "backup_server1"
# BACKUP_SERVER2 = "backup_server2" # TODO: RESTORE THE SECOND BACKUP SERVER


class Backup(BaseActor):
    def __init__(self):
        super().__init__()
        self.PRIVATE_KEY = j.core.identity.me.nacl.private_key

        self.explorer = j.core.identity.me.explorer
        self.ssh_server1 = j.clients.sshclient.get(BACKUP_SERVER1)
        # self.ssh_server2 = j.clients.sshclient.get(BACKUP_SERVER2) # TODO: RESTORE THE SECOND BACKUP SERVER
        self.pub_key = j.core.identity.me.nacl.public_key.encode(nacl.encoding.Base64Encoder).decode()

    @actor_method
    def init(self, threebot_name: str, passwd: str, new: bool = True, restic_username: str = None) -> list:
        try:
            user = self.explorer.users.get(name=threebot_name)
        except requests.exceptions.HTTPError:
            raise j.exceptions.NotFound(f"3Bot name {threebot_name} is not found")

        verify_key = nacl.signing.VerifyKey(binascii.unhexlify(user.pubkey))
        box = Box(self.PRIVATE_KEY, verify_key.to_curve25519_public_key())
        password_backup = box.decrypt(passwd.encode(), encoder=nacl.encoding.Base64Encoder).decode()
        threebot_name = threebot_name.split(".")[0]
        username = threebot_name if not restic_username else restic_username
        if new:
            self._htpasswd(self.ssh_server1, username, password_backup)
            # self._htpasswd(self.ssh_server2, username, password_backup) # TODO: RESTORE THE SECOND BACKUP SERVER
        else:
            try:
                self.ssh_server1.sshclient.run(f"cd ~/backup; htpasswd -vb  .htpasswd {username} {password_backup}")
                # self.ssh_server2.sshclient.run(f"cd ~/backup; htpasswd -vb  .htpasswd {username} {password_backup}") # TODO: RESTORE THE SECOND BACKUP SERVER
            except:
                raise j.exceptions.Value(f"3Bot name or password are incorrect")

        return [self.ssh_server1.host]  # , self.ssh_server2.host] # TODO: RESTORE THE SECOND BACKUP SERVER

    def _htpasswd(self, server, threebot_name, password_backup):
        server.sshclient.run(f"cd ~/backup; htpasswd -Bb .htpasswd {threebot_name} {password_backup}")

    @actor_method
    def public_key(self) -> str:
        return self.pub_key


Actor = Backup
