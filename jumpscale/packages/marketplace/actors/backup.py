import binascii
from shlex import quote

import nacl.encoding
import nacl.secret
import nacl.signing
import nacl.utils
import requests
from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from nacl.public import Box

BACKUP_SERVER1 = "backup_server1"
BACKUP_SERVER2 = "backup_server2"


class Backup(BaseActor):
    def __init__(self):
        super().__init__()
        self.PRIVATE_KEY = j.core.identity.me.nacl.private_key

        self.explorer = j.core.identity.me.explorer
        self.ssh_server1 = j.clients.sshclient.get(BACKUP_SERVER1)
        self.ssh_server2 = j.clients.sshclient.get(BACKUP_SERVER2)
        self.pub_key = j.core.identity.me.nacl.public_key.encode(nacl.encoding.Base64Encoder).decode()

    @actor_method
    def init(self, threebot_name: str, passwd: str, new=True) -> list:
        try:
            user = self.explorer.users.get(name=threebot_name)
        except requests.exceptions.HTTPError:
            raise j.exceptions.NotFound(f"3Bot name {threebot_name} is not found")

        verify_key = nacl.signing.VerifyKey(binascii.unhexlify(user.pubkey))
        box = Box(self.PRIVATE_KEY, verify_key.to_curve25519_public_key())
        password_backup = box.decrypt(passwd.encode(), encoder=nacl.encoding.Base64Encoder).decode()
        threebot_name = threebot_name.split(".")[0]
        if new:
            self._htpasswd(self.ssh_server1, threebot_name, password_backup)
            self._htpasswd(self.ssh_server2, threebot_name, password_backup)
        else:
            try:
                self.ssh_server1.sshclient.run(
                    "cd ~/backup; htpasswd -vb  .htpasswd {threebot_name} {password_backup}".format(
                        threebot_name=quote(threebot_name), password_backup=quote(password_backup)
                    )
                )
                self.ssh_server2.sshclient.run(
                    "cd ~/backup; htpasswd -vb  .htpasswd {threebot_name} {password_backup}".format(
                        threebot_name=quote(threebot_name), password_backup=quote(password_backup)
                    )
                )
            except:
                raise j.exceptions.Value(f"3Bot name or password are incorrect")

        return [self.ssh_server1.host, self.ssh_server2.host]

    def _htpasswd(self, server, threebot_name, password_backup):
        server.sshclient.run(
            "cd ~/backup; htpasswd -Bb .htpasswd {threebot_name} {password_backup}".format(
                threebot_name=quote(threebot_name), password_backup=quote(password_backup)
            )
        )

    @actor_method
    def public_key(self) -> str:
        return self.pub_key


Actor = Backup
