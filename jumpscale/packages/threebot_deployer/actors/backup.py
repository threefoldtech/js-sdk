import binascii

import nacl.encoding
import nacl.secret
import nacl.signing
import nacl.utils
import requests
from nacl.public import Box

from jumpscale.loader import j
from jumpscale.packages.threebot_deployer.models.backup_tokens_sal import BACKUP_MODEL_FACTORY
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method

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
    def init(self, threebot_name: str, passwd: str, new=True, token: str = "") -> list:
        try:
            user = self.explorer.users.get(name=threebot_name)
        except requests.exceptions.HTTPError:
            raise j.exceptions.NotFound(f"3Bot name {threebot_name} is not found")

        # check the user token is valid for new users
        if new:
            verified = False
            for solution_name in BACKUP_MODEL_FACTORY.list_all():
                backup_data = BACKUP_MODEL_FACTORY.get(solution_name)

                if str(backup_data.token) == str(token):
                    verified = True
                    BACKUP_MODEL_FACTORY.delete(solution_name)

            if not verified:
                raise j.exceptions.Permission(
                    f"Invalid token, Unauthorized attempt to create a backup user from {threebot_name}."
                )

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
                    f"cd /root/backup; htpasswd -vb  .htpasswd {threebot_name} {password_backup}"
                )
                self.ssh_server2.sshclient.run(
                    f"cd /root/backup; htpasswd -vb  .htpasswd {threebot_name} {password_backup}"
                )
            except:
                raise j.exceptions.Value(f"3Bot name or password is incorrect")

        return [self.ssh_server1.host, self.ssh_server2.host]

    def _htpasswd(self, server, threebot_name, password_backup):
        server.sshclient.run(f"cd ~/backup; htpasswd -Bb .htpasswd {threebot_name} {password_backup}")

    @actor_method
    def public_key(self) -> str:
        return self.pub_key

    @actor_method
    def backup_exists(self, threebot_name) -> bool:
        """Check if the deployer backup exists on the two backup server

        Args:
            threebot_name(str): name of the threebot that used during backup 
        
        Returns:
            bool: return true if the backup is found else it returns false
        """
        if not threebot_name:
            raise j.exceptions.Value("threebot_name doesn't have value")

        try:
            _, res, _ = self.ssh_server1.sshclient.run(
                f"cd /root/backup;  if [ -f {threebot_name} ] ; then echo 'yes' ; else echo 'no' ; fi"
            )
            _, res, _ = self.ssh_server2.sshclient.run(
                f"cd /root/backup;  if [ -f {threebot_name} ] ; then echo 'yes' ; else echo 'no' ; fi"
            )
        except:
            raise j.exceptions.Value("failed to check 3bot deployer backup is exist or not")

        return True if res.strip() == "yes" else False

    @actor_method
    def list_backup(self) -> list:
        """List all backups

        Returns:
            list : list of string of all available backups
        """
        backup_path = "/root/backup"
        res = []
        try:
            _, res1, _ = self.ssh_server1.sshclient.run(f"ls {backup_path}")
            res.extend(res1.strip().split("\n"))
        except:
            msg = "failed to check 3bot deployer backup is exist or not on server 1"
            j.logger.warning(msg)
            j.tools.alerthandler.alert_raise(
                appname="backup", category="internal_errors", message=msg, alert_type="exception"
            )
        try:
            _, res2, _ = self.ssh_server2.sshclient.run(f"ls {backup_path}")
            res.extend(res2.strip().split("\n"))
        except:
            msg = "failed to check 3bot deployer backup is exist or not on server 2"
            j.logger.warning(msg)
            j.tools.alerthandler.alert_raise(
                appname="backup", category="internal_errors", message=msg, alert_type="exception"
            )
        return list(set(res))


Actor = Backup
