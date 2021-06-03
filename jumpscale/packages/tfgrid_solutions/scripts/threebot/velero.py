from jumpscale.loader import j
import os
import gevent
import hashlib

vdc = j.sals.vdc.find(list(j.sals.vdc.list_all())[0])
BACKUP_CONFIG = os.environ.get("BACKUP_CONFIG", "{}")
BACKUP_CONFIG = j.data.serializers.json.loads(BACKUP_CONFIG)
ak = BACKUP_CONFIG.get("ak")
sk = BACKUP_CONFIG.get("sk")
url = BACKUP_CONFIG.get("url")
region = BACKUP_CONFIG.get("region")
bucket = BACKUP_CONFIG.get("bucket")
if all([ak, sk, url, region]):
    j.sals.fs.write_file(
        "/root/credentials",
        f"""
    [default]
    aws_access_key_id={ak}
    aws_secret_access_key={sk}
    """,
    )
    mon = vdc.get_zdb_monitor()
    password = mon.get_password()
    password_hash = hashlib.md5(password.encode()).hexdigest()
    j.sals.process.execute(
        f"/sbin/velero install --provider aws --use-restic --plugins magedmotawea/velero-plugin-for-aws-amd64:main --bucket {bucket} --secret-file /root/credentials --backup-location-config region={region},s3ForcePathStyle=true,s3Url={url},encryptionSecret={password_hash} --prefix {vdc.owner_tname}/{vdc.vdc_name}",
        showout=True,
    )

    j.sals.process.execute(f"/sbin/kubectl rollout status -w deployments velero -n velero", showout=True)

    # wait for backup location to be ready
    now = j.data.time.utcnow().timestamp
    while j.data.time.utcnow().timestamp < now + 200:
        rc, out, _ = j.sals.process.execute("/sbin/velero backup-location get", showout=True)
        if "Available" in out:
            break
        else:
            gevent.sleep(3)

    # get and restore latest backup
    ret, out, _ = j.sals.process.execute("/sbin/velero backup get -o json", showout=True)
    if out:
        backups = j.data.serializers.json.loads(out)
        backup_names = []
        if len(backups.get("items", [])) > 0:
            vdc_backup = ""
            config_backup = ""
            sorted_backups = sorted(
                backups["items"], key=lambda backup: backup.get("metadata", {}).get("name"), reverse=True
            )
            for backup in sorted_backups:
                name = backup.get("metadata", {}).get("name")
                if "vdc" in name and not vdc_backup:
                    vdc_backup = name
                    backup_names.append(name)
                elif "config" in name and not config_backup:
                    config_backup = name
                    backup_names.append(name)
                if len(backup_names) == 2:
                    break
        else:
            backup_name = backups.get("metadata", {}).get("name")
            if backup_name:
                backup_names.append(backup_name)

        for backup_name in backup_names:
            j.sals.process.execute(
                f"/sbin/velero restore create restore-{backup_name}-{j.data.time.utcnow().timestamp} --from-backup {backup_name}",
                showout=True,
            )

    # create backup schedule for automatic backups
    j.sals.process.execute('/sbin/velero create schedule vdc --schedule="@every 12h" -l "backupType=vdc"', showout=True)
    j.sals.process.execute(
        '/sbin/velero create schedule config --schedule="@every 12h" --include-resources secrets,configmaps',
        showout=True,
    )
