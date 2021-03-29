from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.loader import j
import os


class ETCDBackupService(BackgroundService):
    def __init__(self, interval=60 * 60 * 24, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    def job(self):
        # not needed to run periodically
        return
        # use etcdctl to get a snapshot of etcd and back it up using restic
        url = os.environ.get("S3_URL")
        bucket = os.environ.get("S3_BUCKET")
        ak = os.environ.get("S3_AK")
        sk = os.environ.get("S3_SK")
        if not all([url, bucket]):
            j.logger.warning(f"etcd backup is not configured. url: {url}, bucket: {bucket}")
            return
        if not j.sals.vdc.list_all():
            raise j.exceptions.Value(
                "Couldn't find any vdcs on this machine, Please make sure to have it configured properly"
            )
        vdc = j.sals.vdc.get(list(j.sals.vdc.list_all())[0])
        vdc.load_info()
        snapshot_path = "/tmp/vdc_etcd.db"
        snapshot_manager = vdc.get_snapshot_manager("/tmp")
        snapshot_manager.create_snapshot("vdc_etcd.db")
        j.logger.info(f"backing up etcd snapshot at location: {snapshot_path} to restic")
        # backup with restic to s3
        restic = j.tools.restic.get("vdc")
        restic.extra_env = {
            "AWS_ACCESS_KEY_ID": ak,
            "AWS_SECRET_ACCESS_KEY": sk,
        }
        vdc_zdb_monitor = vdc.get_zdb_monitor()
        password = vdc_zdb_monitor.get_password()
        restic.repo = f"s3:{url}/{bucket}/{vdc.owner_tname}/{vdc.vdc_name}"
        restic.password = password
        if not j.core.config.get("RESTIC_INITIALIZED"):
            restic.init_repo()
            j.core.config.set("RESTIC_INITIALIZED", True)
        restic.backup(snapshot_path)


service = ETCDBackupService()
