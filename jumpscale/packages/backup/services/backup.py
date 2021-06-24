from os import POSIX_FADV_NOREUSE
from jumpscale.loader import j
from jumpscale.tools.servicemanager.servicemanager import BackgroundService


class BackupService(BackgroundService):
    def __init__(self, interval: int = 30, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    def job(self):
        # check if there is a configured systembackupclient instance of restic
        if "systembackupclient" not in j.tools.restic.list_all():
            # log and show alret
            j.logger.warning("")
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
            for job in backup_jobs:
                job.excute(restic_client)
