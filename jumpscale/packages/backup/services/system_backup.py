"""
----------------------------------------------------------------------
THE SYSTEM BACKUP SERVICE
----------------------------------------------------------------------
this service will run in the background and execute a backup job for the system paths every hour

Examples:
# ---- run the backup service jobs once manually
JS-NG> j.packages.backup.SystemBackupService().job()

# ---- adding the backup service manually to the servicemanager, although this would done automatically when threebot start
JS-NG> service_manager = j.tools.servicemanager.new('system_backup_service')
JS-NG> service_manager.add_service('system_backup_service', j.sals.fs.expanduser('~/projects/js-sdk//jumpscale/packages/backup/services/system_backup.py'))

# for how to create a backup jobs, check backupjob sal docs
"""

from jumpscale.loader import j
from jumpscale.tools.servicemanager.servicemanager import BackgroundService


class SystemBackupService(BackgroundService):
    # we will use this  pre defined BackupJop if exists, else we will define it using the info from next section
    BACKUP_JOP_NAME = "systembackupjob"

    # system BackupJob info
    ## this ResticRepo instance must be preconfigured and exist.
    RESTIC_CLIENT_NAMES = ["systembackupclient"]
    ## paths to include in the BackupJob
    BACKUP_JOP_PATHS = ["~/.config/jumpscale/", "~/sandbox/cfg/"]
    ## paths to exclude. absolute paths will not work as the exclude path should be inside one of the specified backup paths.
    PATHS_TO_EXCLUDE = [".config/jumpscale/logs"]

    def __init__(self, interval=60 * 60, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    @classmethod
    def _create_system_backup_job(cls):
        backupjob = j.sals.backupjob.new(
            cls.BACKUP_JOP_NAME,
            clients=cls.RESTIC_CLIENT_NAMES,
            paths=cls.BACKUP_JOP_PATHS,
            paths_to_exclude=cls.PATHS_TO_EXCLUDE,
        )
        backupjob.save()

    def job(self):
        """Background backup job to be scheduled.
        """
        if self.BACKUP_JOP_NAME not in j.sals.backupjob.list_all():
            j.logger.warning(
                f"system_backup_service: couldn't get instance of BackupJob with name {self.BACKUP_JOP_NAME}!"
            )
            SystemBackupService._create_system_backup_job()
            j.logger.info(
                f"system_backup_service: {self.BACKUP_JOP_NAME} job successfully created\npaths included: {self.BACKUP_JOP_PATHS}\npaths excluded: {self.PATHS_TO_EXCLUDE}."
            )
        backupjob = j.sals.backupjob.get(self.BACKUP_JOP_NAME)
        backupjob.execute()
        j.logger.info(f"system_backup_service: {self.BACKUP_JOP_NAME} job started.")


service = SystemBackupService()
