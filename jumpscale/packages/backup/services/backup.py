from os import POSIX_FADV_NOREUSE
from jumpscale.loader import j
from jumpscale.tools.servicemanager.servicemanager import BackgroundService
import gevent


class BackupService(BackgroundService):
    def __init__(self, interval: int = 60 * 60, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    def job(self):
        def _execute(job, restic_client):
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

        # check if there is a configured systembackupclient instance of restic
        if "systembackupclient" not in j.tools.restic.list_all():
            # log and show alret
            j.logger.warning(
                "backup_service: couldn't get instance of restic with name 'systembackupclient'!\nno backup jobs will executed."
            )
            j.tools.alerthandler.alert_raise(
                app_name="backup_service",
                category="backup_service_errors",
                message=f"backup_service: couldn't get instance of restic with name 'systembackupclient'!\nno backup jobs will executed.",
            )
        else:
            restic_client = j.tools.restic.get("systembackupclient")
            # get backup jobs from backup sal
            backup_jobs = j.sals.backupjob.list_all()
            # excute every backup job

            for job_name in backup_jobs:
                job = j.sals.backupjob.get(job_name)
                _ = gevent.spawn(_execute, job, restic_client)


service = BackupService()
