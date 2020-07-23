from gevent import monkey

monkey.patch_all(subprocess=False)  # noqa: E402

import os
from jumpscale.loader import j
from jumpscale.packages.backup.actors.marketplace import Backup

BACKUP_ACTOR = Backup()

instance_name = os.environ.get("INSTANCE_NAME")
threebot_name = os.environ.get("THREEBOT_NAME")
domain = os.environ.get("DOMAIN")
backup_password = os.environ.get("BACKUP_PASSWORD", None)

tname = f"{threebot_name}_{instance_name}"
email = f"{tname}@threefold.me"
words = j.data.encryption.key_to_mnemonic(backup_password.encode().zfill(32))

new = True
explorer = j.clients.explorer.get_default()
try:
    if explorer.users.get(name=tname):
        new = False
except j.exceptions.NotFound:
    pass

j.logger.info("Generating guest identity ...")
identity = j.core.identity.new("default", tname=tname, email=email, words=words)
identity.admins.append(f"{threebot_name}.3bot")
identity.register()
identity.save()
j.core.identity.set_default("default")

if backup_password:
    try:
        BACKUP_ACTOR.init(backup_password, new=new)
        if not new:
            snapshots = j.data.serializers.json.loads(BACKUP_ACTOR.snapshots())
            if snapshots.get("data"):
                j.logger.info("Restoring backup ...")
                BACKUP_ACTOR.restore()
        else:
            j.logger.info("Taking backup ...")
            BACKUP_ACTOR.backup(tags="init")
    except Exception as e:
        j.logger.error(str(e))

j.logger.info("Starting threebot ...")
j.servers.threebot.start_default(wait=True, local=False, domain=domain, email=email)
