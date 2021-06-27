"""
----------------------------------------------------------------------
THE SYSTEM BACKUP SERVICE
----------------------------------------------------------------------
this service will run in the background and execute all backup jobs configured in the system every hour asynchronously in separated gevent threads

Examples:
# ---- run the backup service jobs once manually
JS-NG> j.packages.backup.BackupService().job()

# ---- adding the backup service manually to the servicemanager, although this would done automatically when threebot start
JS-NG> service_manager = j.tools.servicemanager.new('backupservice')
JS-NG> service_manager.add_service('backupservice', j.sals.fs.expanduser('~/projects/js-sdk//jumpscale/packages/backup/services/backup.py'))

# for how to create a backup jobs, check backupjob sal docs
"""

from os import POSIX_FADV_NOREUSE
from jumpscale.loader import j
from jumpscale.tools.servicemanager.servicemanager import BackgroundService
import gevent


class BackupService(BackgroundService):
    SYSTEM_BACKUP_CLIENT_NAME = "systembackupclient"

    def __init__(self, interval: int = 60, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    def job(self):
        """Background backup job to be scheduled.
        """

        def _execute(job, restic_client):
            """executing backup job using preconfigure client

            Args:
                job (BackupJob): the backup job to execute.
                restic_client (ResticRepo): the preconfigured restic client to use.
            """
            try:
                job.execute(restic_client)
            except Exception as e:
                j.logger.exception(f"backup_service: {job.instance_name} job failed", exception=e)
                j.tools.alerthandler.alert_raise(
                    app_name="backup_service",
                    category="backup_service_errors",
                    message=f"backup_service: {job.instance_name} job failed.",
                )
            else:
                j.logger.info(f"backup_service: {job.instance_name} job successfully executed")

        # check if there isn't a configured systembackupclient instance of restic
        if self.SYSTEM_BACKUP_CLIENT_NAME not in j.tools.restic.list_all():
            j.logger.warning(
                "backup_service: couldn't get instance of restic with name 'systembackupclient'!\nno backup jobs will executed."
            )
            j.tools.alerthandler.alert_raise(
                app_name="backup_service",
                category="backup_service_errors",
                message=f"backup_service: couldn't get instance of restic with name 'systembackupclient'!\nno backup jobs will executed.",
            )
        else:
            restic_client = j.tools.restic.get(self.SYSTEM_BACKUP_CLIENT_NAME)
            # get all backup job names from the backupjob sal
            backup_jobs = j.sals.backupjob.list_all()

            # excute every backup job in seprated gevent thread
            for job_name in backup_jobs:
                job = j.sals.backupjob.get(job_name)
                _ = gevent.spawn(_execute, job, restic_client)


service = BackupService()
