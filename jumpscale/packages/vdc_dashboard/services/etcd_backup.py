from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.loader import j
from jumpscale.packages.backup.actors.threebot_deployer import Backup


class ETCDBackupService(BackgroundService):
    def __init__(self, interval=60 * 5, *args, **kwargs):
        super().__init__(interval, *args, **kwargs)

    def job(self):
        # use etcdctl to get a snapshot of etcd and back it up using restic
        vdc = j.sals.vdc.get(list(j.sals.vdc.list_all())[0])
        vdc.load_info()
        endpoints = ""
        for etcd in vdc.etcd:
            endpoints += f"http://{etcd.ip_address}:2379,"
        etcd_env = {"ETCDCTL_API": 3}
        snapshot_path = "/tmp/vdc_etcd.db"
        j.logger.info(f"creating a snapshot of etcd cluster on endpoints: {endpoints}")
        snapshot_cmd = f"etcdctl endpoints={endpoints} snapshot save {snapshot_path}"
        rc, out = j.sals.process.execute(snapshot_cmd, env=etcd_env)
        if rc:
            msg = f"failed to save etcd snapshot. output: {out}"
            j.logger.error(msg)
            j.tools.alerthandler.alert_raise("vdc", msg)
            return
        j.logger.info(f"backing up etcd snapshot at location: {snapshot_path} to restic")
        backup_actor = Backup()
        backup_actor.backup(paths=[snapshot_path])


service = ETCDBackupService()
