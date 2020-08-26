from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.loader import j
import nacl.secret
import nacl.utils
import requests
import nacl.signing
import binascii
from nacl.public import Box
import nacl.encoding


class Backup(BaseActor):
    def __init__(self):
        super().__init__()
        self.PRIVATE_KEY = j.core.identity.me.nacl.private_key
        self.explorer = j.core.identity.me.explorer
        self.pub_key = j.core.identity.me.nacl.public_key.encode(nacl.encoding.Base64Encoder).decode()

    @property
    def ssh_servers(self):
        servers = []
        for backup_server in j.config.get("BACKUP_SERVERS") or ["backup_server1", "backup_server2"]:
            servers.append(j.clients.sshclient.get(backup_server))
        return servers

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
            for ssh_server in self.ssh_servers:
                self._htpasswd(ssh_server, threebot_name, password_backup)
        else:
            try:
                for ssh_server in self.ssh_servers:
                    ssh_server.sshclient.run(f"cd ~/backup; htpasswd -vb  .htpasswd {threebot_name} {password_backup}")
            except:
                raise j.exceptions.Value(f"3Bot name or password are incorrect")

        return [ssh_server.host for ssh_server in self.ssh_servers]

    @actor_method
    def backup_servers_count(self) -> int:
        return len(self.ssh_servers)

    def _htpasswd(self, server, threebot_name, password_backup):
        server.sshclient.run(f"cd ~/backup; htpasswd -Bb .htpasswd {threebot_name} {password_backup}")

    @actor_method
    def public_key(self) -> str:
        return self.pub_key


Actor = Backup
