"""
----------------------------------------------------------------------
THE BACKUPJOB SAL
----------------------------------------------------------------------
This sal can be used to create and manage multiple backup jobs with multiple and configured paths.

Examples:
# ---- create new backup job ----
# ---- every package could create its backup job when installed with one or multiple paths
## from jumpscale.sals.backupjob import backupjob
JS-NG> nginxbackup = j.sals.backupjob.new("nginxbackup", paths=["~/sandbox/cfg/nginx/main/"])
JS-NG> nginxbackup.save()

# ---- create another backup job ---
JS-NG> vdcbackup = j.sals.backupjob.new("vdcbackup", paths=["~/.config/jumpscale/secureconfig/jumpscale/sals/vdc/"])
JS-NG> vdcbackup.save()

# ---- list backup jobs
JS-NG> j.sals.backupjob.list_all()

# ---- get and execute a backup job
# first get the preconfigured restic client
system_backup_client_name = j.packages.backup.BackupService().SYSTEM_BACKUP_CLIENT_NAME
JS-NG> restic = j.tools.restic.get(system_backup_client_name)
# ---- second get the backup job
JS-NG> nginxbackup_job = j.sals.backupjob.get('nginxbackup')
# ---- then execute the backup job by sending execute method the preconfigured restic client
JS-NG> nginxbackup_job.execute(restic)

-----------------------------------------------------------------------
# EXAMPLE packages -> <package> -> package.py
-----------------------------------------------------------------------
from jumpscale.loader import j

# this name will used to tag the backup
BACKUPJOB_NAME = "example_backup_job"


class admin:
    def install(self, **kwargs):
        # Called when package is added
        # adding the package backup job if it not exists
        if BACKUPJOB_NAME not in j.sals.backupjob.list_all():
            systembackup = j.sals.backupjob.new(
                BACKUPJOB_NAME, paths=["~/example/path/"])
            systembackup.save()
            j.logger.info(
                f"{BACKUPJOB_NAME} backup job has been added successfully.")
        else:
            j.logger.warning(f"a backup job with name {BACKUPJOB_NAME} already exists!")

    def uninstall(self):
        # Called when package is deleted
        # removing the package backup job if it exists
        if BACKUPJOB_NAME in j.sals.backupjob.list_all():
            j.sals.backupjob.delete(BACKUPJOB_NAME)
            j.logger.info(f"{BACKUPJOB_NAME} backup job has been removed successfully.")

    def start(self):
        # Called when threebot is started
        if BACKUPJOB_NAME not in j.sals.backupjob.list_all():
            j.logger.warning(f"package {__name__} was installed before but its backup job doesn't exist anymore!")
"""
from jumpscale.loader import j
from jumpscale.core.base import Base, fields
from jumpscale.sals import fs


def _path_validator(path):
    import os

    if not fs.is_absolute(os.path.expanduser(path)):
        raise j.core.base.fields.ValidationError(f"The path {path} should be absolute path or begin with a tilde")


class BackupJob(Base):
    paths = fields.List(fields.String(validators=[_path_validator]))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, client):
        exp_path = " ".join([fs.expanduser(path) for path in self.paths])
        client.backup(exp_path, tags=[self.instance_name])

    def list_snapshots(self, client, last=False, path=None):
        return client.list_snapshots(tags=[self.instance_name], last=last, path=path)

    def restore(self, client, target_path="/", snapshot_id=None):
        # check the snapshot id
        if snapshot_id:
            snapshots = self.list_snapshots(client)
            snapshots_ids = [snapshot["id"] for snapshot in snapshots]
            if snapshot_id not in snapshots_ids:
                raise j.exceptions.Value(
                    f"This snapshotid {snapshot_id:.8} is not found for this backup job {self.instance_name}."
                )
        else:
            last_snapshot = client.list_snapshots(tags=[self.instance_name], last=True)
            if last_snapshot:
                assert len(last_snapshot) == 1
                snapshot_id = last_snapshot[0]["id"]
            else:
                raise j.exceptions.Value(f"No previous snapshots found for this backup job: {self.instance_name}.")
        return client.restore(target_path, snapshot_id=snapshot_id)
