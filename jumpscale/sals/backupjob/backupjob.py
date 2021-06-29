"""
----------------------------------------------------------------------
THE BACKUPJOB SAL
----------------------------------------------------------------------
This sal can be used to create and manage multiple backup jobs with multiple and configured paths.

Examples:
# ---- create new backup job ----
# ---- every package could create its backup job when installed with one or multiple paths
JS-NG> nginxbackup = j.sals.backupjob.new("nginxbackup", clients = ["restic_client_1", "restic_client_2"], paths=["~/sandbox/cfg/nginx/main/"])
JS-NG> nginxbackup.save()

# ---- create another backup job ---
JS-NG> vdcbackup = j.sals.backupjob.new("vdcbackup", clients = ["restic_client_3", "restic_client_4"], paths=["~/.config/jumpscale/secureconfig/jumpscale/sals/vdc/"])
JS-NG> vdcbackup.save()

# ---- list backup jobs
JS-NG> j.sals.backupjob.list_all()

# ---- get and execute a backup job
JS-NG> nginxbackup_job = j.sals.backupjob.get('nginxbackup')
# ---- then execute the backup job
JS-NG> nginxbackup_job.execute()

-----------------------------------------------------------------------
# EXAMPLE packages -> <package> -> package.py
for creating and removing a backup job when a package get installed or uninstalled.
Note: This will need a background service to excute this backup job automatically every interval of time.
check the system backup service as an example: jumpscale/packages/backup/services/backup.py
-----------------------------------------------------------------------
from jumpscale.loader import j

# this name will used to tag the backup
BACKUPJOB_NAME = "example_backup_job"
BACKUPJOB_PATHS = ["~/example/path/"]  # The path/s should be absolute path/s or begin with a tilde
RESTIC_CLIENT_NAMES = ["CLIENT1", "CLIENT2"]  # should be preconfigured client/s

class admin:
    def install(self, **kwargs):
        # Called when package is added
        # adding the package backup job if it not exists
        if BACKUPJOB_NAME not in j.sals.backupjob.list_all():
            backupjob = j.sals.backupjob.new(
                BACKUPJOB_NAME, RESTIC_CLIENT_NAMES, BACKUPJOB_PATHS)
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
from jumpscale.loader import j
from jumpscale.core.base import Base, fields
from jumpscale.sals import fs
import gevent


def _path_validator(path):
    """Raises a ValidationError if a path Neither an absolute path nor begin with a tilde.

    Args:
        path (str): a path represent a directory/file.

    Raises:
        j.core.base.fields.ValidationError: If a path Neither an absolute path nor begin with a tilde.
    """
    if not fs.is_absolute(fs.os.path.expanduser(path)):
        raise j.core.base.fields.ValidationError(f"The path {path} should be absolute path or begin with a tilde")


def _client_validator(restic_client_name):
    """Raises a ValidationError if a restic client instance with given name can not be found.

    Args:
        restic_client_name (str): a restic client instance name.

    Raises:
        j.core.base.fields.ValidationError: If a restic client instance with given name can not be found.
    """
    if restic_client_name not in j.tools.restic.list_all():
        raise j.core.base.fields.ValidationError(f"The restic client: {restic_client_name} not found!")


class BackupJob(Base):
    paths = fields.List(fields.String(validators=[_path_validator]))
    paths_to_exclude = fields.List(fields.String())
    clients = fields.List(fields.String(validators=[_client_validator]))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def _get_client(restic_client_name):
        """Gets a ResticRepo object with a given instance name.

        Args:
            restic_client_name (str): Restic instance name.

        Raises:
            j.expections.Runtime: If restic instance not found.

        Returns:
            ResticRepo: jumpscale.tools.restic.restic.ResticRepo instance.
        """
        if restic_client_name in j.tools.restic.list_all():
            return j.tools.restic.get(restic_client_name)
        raise j.expections.Runtime(f"The restic client: {restic_client_name} not found!")

    def execute(self):
        """Backups the preconfigured paths with the preconfigured restic clients.
        All snapshots created with a Backupjob will be tagged with the BackupJob instance name for easy referencing, manageing, cleaning and restoring.
        """

        def _excute(client, paths, tags, exclude):
            try:
                client.backup(paths, tags=tags, exclude=exclude)
            except Exception as e:
                j.logger.exception(
                    f"BackupJob name: {self.instance_name} - Error happened during Backing up using this ResticRepo: {client.instance_name}`",
                    exception=e,
                )
            else:
                j.logger.info(
                    f"BackupJob name: {self.instance_name} - ResticRepo: {client.instance_name} snapshot successfully saved."
                )

        paths = [fs.os.path.expanduser(path) for path in self.paths]
        paths_to_exclude = [fs.os.path.expanduser(path) for path in self.paths_to_exclude]
        for restic_client_name in self.clients:
            client = self._get_client(restic_client_name)
            _ = gevent.spawn(_excute, client, paths, tags=[self.instance_name], exclude=paths_to_exclude)

    def list_all_snapshots(self, last=False, path=None):
        """Returns a dictionary of restic snapshots lists that are related to to this BackupJob instance,
        where the keys are the ResticRepo instance name.

        Args:
            last (bool, optional): If True will get last snapshot only while respecting the other filters. Defaults to False.
            path (str, optional): Path to filter on. Defaults to None.

        Returns:
            Dict of lists: a dictionary of restic snapshots lists
        """
        snapshots = {}
        for restic_client_name in self.clients:
            snapshots[restic_client_name] = self.list_snapshots(restic_client_name, last=last, path=path)
        return snapshots

    def list_snapshots(self, restic_client_name, last=False, path=None):
        """Returns a list of restic snapshots that are related to to this BackupJob instance from a ResticRepo with a given instance name

        Args:
            restic_client_name (str): Restic instance name.
            last (bool, optional): If True will get last snapshot only while respecting the other filters. Defaults to False.
            path (str, optional): Path to filter on. Defaults to None.

        Returns:
            list of dictionaries: list of restic snapshots.
                Example: [{'time': '2021-06-27T19:18:00.203093762+02:00', 'parent': 'ded571a29dfa8f3db1c455ee5714acf5b248a90f9b5103235a682737eba583b3',
                'tree': 'dae692c71558aa6f1f632dc805dd614a8d35ecb8c5053bc32665506d7a4a066c', 'paths': ['/home/ayoub/play.txt'],
                'hostname': 'ayoub', 'username': 'ayoub', 'uid': 1000, 'gid': 1000, 'tags': ['admin_sameh'],
                'id': 'e3d5d9dd2e252d0cf55ff66aabe839af312c4fdc6119e08a72984086664ef3b0', 'short_id': 'e3d5d9dd'}]
        """
        client = self._get_client(restic_client_name)
        return client.list_snapshots(tags=[self.instance_name], last=last, path=path) or []

    def restore(self, restic_client_name, target_path="/", snapshot_id=None, host=None):
        """Restore a specifc or latest snapshot for this BackupJob from a ResticRepo with a given instance name.

        Args:
            restic_client_name (str): Restic instance name.
            target_path (str, optional): path to restore to. Defaults to "/".
            snapshot_id (str, optional):  id or short_id of the snapshot.
                if not specified will use tha latest snapshot/s taken for this BackupJob instead. Defaults to None.
            host (str, optional): Filter on the hostname when using latest. Defaults to None.

        Raises:
            j.exceptions.Value: if the specified snapshot id is not found for this BackupJob.
            j.exceptions.Runtime: if no previous snapshots found for this BackupJob.
        """
        client = self._get_client(restic_client_name)
        if snapshot_id:
            if len(snapshot_id) < 8:
                raise j.exceptions.Value(f"The length of snapshot id ({snapshot_id}) should be at least 8 characters.")
            snapshots = self.list_snapshots(restic_client_name)
            snapshots_ids = [snapshot["id"] for snapshot in snapshots if snapshot["id"].startswith(snapshot_id)]
            if not snapshots_ids:
                raise j.exceptions.Value(
                    f"This snapshot id {snapshot_id:.8} is not found for this backup job {self.instance_name}."
                )

        client.restore(target_path, snapshot_id=snapshot_id, tags=[self.instance_name], host=host)

    def clean_snapshots(self, restic_client_name, keep_last=0, prune=True):
        """Deletes the snapshots data if `prune` is True otherwise remove the)reference to the data (snapshots) in a ResticRepo with a given instance name.

        Args:
            restic_client_name (str): Restic instance name.
            keep_last (int, optional): How many snapshots to keep. Passing 0 will remove all snapshots for this BackupJob instance. Defaults to 0.
            prune (bool, optional):  Whether to delete the data or not. Defaults to True.
        """
        client = self._get_client(restic_client_name)
        if not keep_last:
            # first forget all snapshots but last as restic will not allow values less than 1.
            client.forget(keep_last=1, tags=[self.instance_name], prune=prune)
            # then get snapshots ids of last snapshots and forget them
            last_snapshots = self.list_snapshots(restic_client_name, last=True)
            last_snapshots_ids = [snapshot["id"] for snapshot in last_snapshots]
            return client.forget(keep_last=0, tags=[self.instance_name], prune=prune, snapshots=last_snapshots_ids)
        client.forget(keep_last=keep_last, tags=[self.instance_name], prune=prune)
