from jumpscale.loader import j
import gevent
from jumpscale.core.base import Base, fields


class Snapshot(Base):
    snapshot_name = fields.String(required=True)

    def __init__(self, manager, path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = manager
        self.vdc = self.manager.vdc
        self._snapshot_path = path
        self._creation_time = None

    @property
    def snapshot_path(self):
        if not self._snapshot_path:
            self._snapshot_path = f"{self.manager.snapshots_dir}/{self.snapshot_name}-{j.data.time.utcnow().timestamp}"
        return self._snapshot_path

    @property
    def creation_time(self):
        if not self._creation_time:
            filename = j.sals.fs.basename(self.snapshot_path)
            try:
                date = j.data.text.removeprefix(filename, f"{self.snapshot_name}-")
                if date:
                    self._creation_time = j.data.time.get(float(date))
            except Exception as e:
                j.logger.warning(f"Failed to get creation time from file name due to error: {str(e)}")
        if not self._creation_time:
            self._creation_time = j.data.time.get(j.sals.fs.get_creation_time(self.snapshot_path))
        return self._creation_time

    def restore(self):
        self.vdc.load_info()
        # open ssh connection to all etcds
        etcd_ssh_clients = []

        try:
            for etcd in self.vdc.etcd:
                etcd_ssh_clients.append(self.vdc.get_ssh_client(f"etcd_{etcd.wid}", etcd.ip_address, "root"))

            for client in etcd_ssh_clients:
                # stop all etcd processes running and copy the snap shot there
                rc, out, err = client.sshclient.run("zinit stop etcd")
                # copy snapshot to each node
                client.sshclient.connection.put(self.snapshot_path, f"/tmp/{self.snapshot_name}")
            # wait until etcd process is stopped
            gevent.sleep(3)

            for client in etcd_ssh_clients:
                # move old data file
                client.sshclient.run("rm -rf /tmp/etcd", warn=True)
                rc, out, err = client.sshclient.run("mv /bitnami/etcd /tmp/")
                # restore etcd using etcdctl
                rc, out, err = client.sshclient.run(
                    f"/opt/bitnami/etcd/bin/etcdctl snapshot restore /tmp/{self.snapshot_name} --data-dir=/bitnami/etcd/data --skip-hash-check=true",
                    warn=True,
                )
                if rc:
                    j.logger.error(f"failed to restore snapshot. rc: {rc}, out: {out}, err: {err}")
                    rc, out, err = client.sshclient.run("rm -rf /bitnami/etcd/; mv /tmp/etcd /bitnami/etcd")
                # start etcd process
                rc, out, err = client.sshclient.run("zinit start etcd")
        except Exception as e:
            for client in etcd_ssh_clients:
                rc, out, err = client.sshclient.run("zinit start etcd", warn=True)
                if rc:
                    j.logger.critical(f"failed to restart etcd for client: {client}. rc: {rc}, out: {out}, err: {err}")
            raise e

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


class SnapshotManager:
    def __init__(self, vdc_instance, snapshots_dir=None):
        self.vdc = vdc_instance
        self._snapshots_dir = snapshots_dir or f"{j.core.dirs.CFGDIR}/vdc/snapshots"

    @property
    def snapshots_dir(self):
        if not j.sals.fs.exists(self._snapshots_dir):
            j.sals.fs.mkdirs(self._snapshots_dir)
        return self._snapshots_dir

    def create_snapshot(self, name):
        current_snapshot_names = [snap.snapshot_name for snap in self.list_snapshots()]
        if name in current_snapshot_names:
            raise j.exceptions.Input(f"a snapshot with the same name: {name} already exists")
        snapshot = Snapshot(self, snapshot_name=name)
        snapshot.create()
        return snapshot

    def list_snapshots(self):
        for path in j.sals.fs.walk_files(self.snapshots_dir):
            snapshot_name = j.sals.fs.basename(path)
            snapshot_name = "-".join(snapshot_name.split("-")[:-1])
            snapshot = Snapshot(self, snapshot_name=snapshot_name, path=path)
            yield snapshot
