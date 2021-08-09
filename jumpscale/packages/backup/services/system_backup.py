"""
----------------------------------------------------------------------
# THE SYSTEM BACKUP SERVICE
----------------------------------------------------------------------
this service will run in the background and execute a backup job for the system paths every hour

Examples:
## run the backup service jobs once manually
JS-NG> j.packages.backup.SystemBackupService().job()

## adding the backup service manually to the servicemanager, although this would done automatically when threebot start
```python
JS-NG> service_manager = j.tools.servicemanager.new('system_backup_service')
JS-NG> service_manager.add_service('system_backup_service', j.sals.fs.expanduser('~/projects/js-sdk//jumpscale/packages/backup/services/system_backup.py'))
```
## for how to create a backup jobs, check backupjob sal docs
"""

from jumpscale.loader import j
from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.tools.notificationsqueue.queue import LEVEL


class SystemBackupService(BackgroundService):
    # we will use this  pre defined BackupJop if exists, else we will define it using the info from next section
    BACKUP_JOB_NAME = "systembackupjob"

    # system BackupJob info
    ## this ResticRepo instance must be preconfigured and exist.
    RESTIC_CLIENT_NAMES = ["systembackupclient"]
    ## paths to include in the BackupJob
    BACKUP_JOB_PATHS = ["~/.config/jumpscale/", "~/sandbox/cfg/", "~/.ssh/"]
    ## paths to exclude. absolute paths will not work as the exclude path should be inside one of the specified backup paths.
    PATHS_TO_EXCLUDE = [".config/jumpscale/logs"]

    def __init__(self, interval=60 * 60, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    @classmethod
    def _create_system_backup_job(cls):
        repos_are_ready = all([client in j.tools.restic.list_all() for client in cls.RESTIC_CLIENT_NAMES])
        if repos_are_ready:
            backupjob = j.sals.backupjob.new(
                cls.BACKUP_JOB_NAME,
                clients=cls.RESTIC_CLIENT_NAMES,
                paths=cls.BACKUP_JOB_PATHS,
                paths_to_exclude=cls.PATHS_TO_EXCLUDE,
            )
            backupjob.save()
            return True
        else:
            return False

    def job(self):
        """Background backup job to be scheduled.
        """
        j.logger.info(f"[Backup Package - System Backup Service] Backup job {self.BACKUP_JOB_NAME} started.")
        if self.BACKUP_JOB_NAME not in j.sals.backupjob.list_all():
            j.logger.warning(
                f"[Backup Package - System Backup Service] couldn't get instance of BackupJob with name {self.BACKUP_JOB_NAME}!"
            )

            if not SystemBackupService._create_system_backup_job():
                j.logger.error(
                    f"[Backup Package - System Backup Service] There is no preconfigure restic repo/s. Backup job won't executed!"
                )
                return
            j.logger.info(
                f"[Backup Package - System Backup Service] {self.BACKUP_JOB_NAME} job successfully created\npaths to backup: {self.BACKUP_JOB_PATHS}\npaths excluded: {self.PATHS_TO_EXCLUDE}."
            )

        backupjob = j.sals.backupjob.get(self.BACKUP_JOB_NAME)
        job_completed = backupjob.execute(block=True)
        if job_completed:
            j.logger.info(
                f"[Backup Package - System Backup Service] Backup job {self.BACKUP_JOB_NAME} completed successfully."
            )
            j.tools.notificationsqueue.push(
                f"the System backup job completed successfully.", category="SystemBackupService", level=LEVEL.INFO
            )
        else:
            j.logger.error(f"[Backup Package - System Backup Service] Backup job {self.BACKUP_JOB_NAME} failed.")
            j.tools.notificationsqueue.push(
                f"the System backup job failed.", category="SystemBackupService", level=LEVEL.ERROR
            )


service = SystemBackupService()
