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
from jumpscale.core.base import Base, fields
from jumpscale.sals import fs
from jumpscale.data import time


class BackupJob(Base):
    paths = fields.List(fields.String())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, client):
        for path in self.paths:
            exp_path = fs.expanduser(path)
            client.backup(exp_path, tags=[self.instance_name])
