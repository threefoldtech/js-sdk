from jumpscale.loader import j
import os
from jumpscale.core.base import Base, fields


class Snapshot(Base):
    snapshot_name = fields.String(default=lambda: f"snapshot-{j.data.time.utcnow().timestamp}")
    creation_time = fields.DateTime()

    def __init__(self, manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = manager
        self.vdc = self.manager.vdc

    @property
    def snapshot_path(self):
        return f"{self.manager.snapshots_dir}/{self.snapshot_name}"

    def restore(self):
        pass

    def delete(self):
        return j.sals.fs.rmtree(self.snapshot_path)

    def create(self):
        self.vdc.load_info()
        endpoints = ""
        for etcd in self.vdc.etcd:
            endpoints += f"http://{etcd.ip_address}:2379,"
        etcd_env = {"ETCDCTL_API": "3"}
        j.logger.info(f"creating a snapshot of etcd cluster on endpoints: {endpoints}")
        snapshot_cmd = f"etcdctl --endpoints={endpoints} snapshot save {self.snapshot_path}"
        rc, out, err = j.sals.process.execute(snapshot_cmd, env=etcd_env)
        if rc:
            msg = f"failed to save etcd snapshot. output: {out}, error: {err}"
            j.logger.error(msg)
            j.tools.alerthandler.alert_raise("vdc", msg)
            raise j.exceptions.Runtime(msg)
        self.creation_time = j.sals.fs.get_creation_time(self.snapshot_path)


class SnapshotManager:
    def __init__(self, vdc_instance, snapshots_dir=None):
        self.vdc = vdc_instance
        self._snapshots_dir = snapshots_dir or f"{j.core.dirs.CFGDIR}/vdc/snapshots"

    @property
    def snapshots_dir(self):
        if not j.sals.fs.exists(self._snapshots_dir):
            j.sals.fs.mkdirs(self._snapshots_dir)
        return self._snapshots_dir

    def create_snapshot(self, name=None):
        # use etcdctl to get a snapshot of etcd and back it up using restic
        snapshot = Snapshot(self, snapshot_name=name)
        snapshot.create()
        return snapshot

    def list_snapshots(self):
        for path in j.sals.fs.walk_files(self.snapshots_dir):
            snapshot_name = j.sals.fs.basename(path)
            creation_time = j.sals.fs.get_creation_time(path)
            snapshot = Snapshot(self, snapshot_name=snapshot_name, creation_time=creation_time)
            yield snapshot
