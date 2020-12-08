from gevent import monkey

monkey.patch_all(subprocess=False)  # noqa: E402

import os
import requests
from jumpscale.loader import j
from jumpscale.packages.backup.actors.threebot_deployer import Backup


def main():
    BACKUP_ACTOR = Backup()
    instance_name = os.environ.get("INSTANCE_NAME")
    threebot_name = os.environ.get("THREEBOT_NAME")
    domain = os.environ.get("DOMAIN")
    backup_password = os.environ.get("BACKUP_PASSWORD", None)
    test_cert = os.environ.get("TEST_CERT")

    # email settings
    email_host = os.environ.get("EMAIL_HOST")
    email_host_user = os.environ.get("EMAIL_HOST_USER")
    email_host_password = os.environ.get("EMAIL_HOST_PASSWORD")

    tname = f"{threebot_name}_{instance_name}"
    email = f"{tname}@threefold.me"
    words = j.data.encryption.key_to_mnemonic(backup_password.encode().zfill(32))

    new = True

    j.logger.info("Generating guest identity ...")
    identity_main = j.core.identity.get(
        "main", tname=tname, email=email, words=words, explorer_url="https://explorer.grid.tf/api/v1"
    )
    identity_test = j.core.identity.get(
        "test", tname=tname, email=email, words=words, explorer_url="https://explorer.testnet.grid.tf/api/v1"
    )

    identities = [identity_main, identity_test]
    for identity in identities:
        identity.admins.append(f"{threebot_name}.3bot")
        identity.register()
        identity.save()

    default_identity = os.environ.get("DEFAULT_IDENTITY", "main")
    j.core.identity.set_default(default_identity)

    # configure escalation mailing
    if all([email_host, email_host_user, email_host_password]):
        try:
            email_instance = j.clients.mail.get("escalation_instance")
            email_instance.login = email_host_user
            email_instance.smtp_port = 587
            email_instance.smtp_server = email_host
            email_instance.sender_email = email_host_user
            email_instance.password = email_host_password
            email_instance.name = threebot_name
            email_instance.save()
        except Exception as e:
            j.logger.warning("Failed to set escalation mail settings")

    if backup_password:
        # Sanitation for the case user deleted his old backups!
        try:
            BACKUP_ACTOR.init(backup_password, new=False)
        except Exception as e:
            new = True
            j.logger.warning(f"{str(e)}: Reinitalizing backup for new user")

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

    server = j.servers.threebot.get("default")
    if test_cert == "false":
        server.domain = domain
        server.email = email
        server.save()


if __name__ == "__main__":
    main()
