from jumpscale.loader import j
from tests.base_tests import BaseTests
from jumpscale.core.exceptions import NotFound
from jumpscale.sals import fs
from jumpscale.sals.backupjob.backupjob import BackupJob

import tempfile
from parameterized import parameterized


def _restic_find(restic_client_name, tag, pattern):
    restic = j.tools.restic.get(restic_client_name)
    proc = restic._run_cmd(["restic", "find", "--tag", tag, pattern, "--json"])
    out = j.data.serializers.json.loads(proc.stdout.decode())
    return bool(out)


class TestBackupjob(BaseTests):
    @classmethod
    def setUpClass(cls):
        if not j.sals.process.is_installed("restic"):
            raise NotFound(f"restic not installed")
        # configure the main directory to run all tests
        cls.main_dir = tempfile.TemporaryDirectory()
        cls.info(f"The main temp directory created successfully with path {cls.main_dir.name}")
        # create two restic clients to use in all tests
        cls.restic_client_names = [f"{cls.random_name()}_client1", f"{cls.random_name()}_client2"]
        cls._create_restic_repos()
        cls.info(f"The random restic test clients created successfully with names: {cls.restic_client_names}")

    @classmethod
    def _create_restic_repos(cls):
        for i, client_name in enumerate(cls.restic_client_names):
            restic_client = j.tools.restic.new(client_name)
            restic_client.repo = fs.join_paths(cls.main_dir.name, f"repo{i}")
            restic_client.password = "password"
            restic_client.init_repo()
            restic_client.save()

    @classmethod
    def tearDownClass(cls):
        for client_name in cls.restic_client_names:
            j.tools.restic.delete(client_name)
        cls.info(f"The restic test clients deleted successfully with names: {cls.restic_client_names}")
        cls.main_dir.cleanup()
        cls.info(f"The main temp directory deleted successfully with path {cls.main_dir.name}")

    def setUp(self):
        super().setUp()
        self.backup_dir = tempfile.TemporaryDirectory(dir=self.main_dir.name)
        self.restore_dir = tempfile.TemporaryDirectory(dir=self.main_dir.name)
        self.files = {"include": ["test1.txt", "test2.txt"], "exclude": ["test1.exclude", "test2.exclude"]}
        self._create_dirs_to_backup()

        self.backupjob = None

    def tearDown(self):
        if self.backupjob:
            j.sals.backupjob.delete(self.backupjob.instance_name)
        self.backup_dir.cleanup()

    def _create_dirs_to_backup(self):
        # create some files
        for dir_name, file_names in self.files.items():
            dir_path = fs.join_paths(self.backup_dir.name, dir_name)
            fs.mkdir(dir_path)
            for file_name in file_names:
                fs.touch(fs.join_paths(dir_path, file_name))

    def _create_backupjob(self, clients, paths, paths_to_exclude=None):
        self.backupjob = j.sals.backupjob.new(self.random_name())
        self.backupjob.clients = clients
        self.backupjob.paths = paths
        self.backupjob.paths_to_exclude = paths_to_exclude
        self.backupjob.save()
        return self.backupjob

    def test01_create_backupjob(self):
        """Test case for test creating a backup job

        **Test Scenario**
        - create new backup job
        - configure it with existing restic client
        - configure it with valid paths
        - assert returned value to be instance of BackupJob
        """
        clients = self.restic_client_names[:1]
        paths = [self.backup_dir.name]
        backupjob = self._create_backupjob(clients, paths)
        self.assertIsInstance(backupjob, BackupJob)

    def test02_create_backupjob_with_non_exists_ResticRepo(self):
        """Test case for test creating a backup job with non exists ResticRepo name

        **Test Scenario**
        - create new backup job
        - configure it with non exists restic client
        - check that saving the instance will raise a ValidationError
        """
        clients = ["Non_exist_client"]
        paths = [self.backup_dir.name]
        with self.assertRaises(j.core.base.fields.ValidationError):
            self._create_backupjob(clients, paths)

    @parameterized.expand([(["./test"],), (["test/"],)])
    def test03_create_backupjob_with_invalid_paths(self, paths):
        """Test case for test creating a backup job with relative paths

        **Test Scenario**
        - create new backup job
        - configure it with relative paths
        - check that saving the instance will raise a ValidationError
        """
        clients = ["Non_exist_client"]
        with self.assertRaises(j.core.base.fields.ValidationError):
            self._create_backupjob(clients, paths)

    def test04_execute_backupjob_with_single_ResticRepo(self):
        """Test case for test creating a backup job and execute it.

        **Test Scenario**
        - create new backup job
        - configure it with existing single ResticRepo
        - configure it with valid paths
        - execute the backup job
        - check we have one snapshot for this BackupJob
        - check the snapshots included the test files
        """
        clients = self.restic_client_names[:1]
        paths = [self.backup_dir.name]
        backupjob = self._create_backupjob(clients, paths)
        backupjob.execute(block=True)
        self.assertEqual(1, len(backupjob.list_snapshots(clients[0])))
        self.assertTrue(_restic_find(clients[0], backupjob.instance_name, "test*.txt"))

    def test05_execute_backupjob_with_multiple_ResticRepo(self):
        """Test case for test creating a backup job, configured it with multiple ResticRepo and execute it.

        **Test Scenario**
        - create new backup job
        - configure it with existing multiple ResticRepo
        - configure it with valid paths
        - execute the backup job
        - check we have one snapshot in every ResticRepo for this BackupJob
        - check the snapshots included the test files
        """
        clients = self.restic_client_names
        paths = [self.backup_dir.name]
        backupjob = self._create_backupjob(clients, paths)
        backupjob.execute(block=True)
        for client in clients:
            self.assertEqual(1, len(backupjob.list_snapshots(client)))
            self.assertTrue(_restic_find(client, backupjob.instance_name, "test*.txt"))

    def test06_execute_backupjob_with_single_ResticRepo_with_excluded_paths(self):
        """Test case for test creating a backup job with excluded paths and execute it.

        **Test Scenario**
        - create new backup job with excluded paths
        - configure it with existing single ResticRepo
        - configure it with valid paths
        - configure it with paths to exclude
        - execute the backup job
        - check we have one snapshot for this BackupJob
        - check the excluded test files not included in the last snapshot
        """
        clients = self.restic_client_names[:1]
        paths = [self.backup_dir.name]
        backupjob = self._create_backupjob(clients, paths, paths_to_exclude=["exclude"])
        backupjob.execute(block=True)
        self.assertEqual(1, len(backupjob.list_snapshots(clients[0])))
        self.assertFalse(_restic_find(clients[0], backupjob.instance_name, "*.exclude"))

    def test07_list_all_snapshots_grouped_by_ResticRepo(self):
        """Test case for test listing the snapshots created by a backup job and grouped by the ResticRepo.

        **Test Scenario**
        - create new backup job
        - configure it with existing multiple ResticRepo
        - configure it with valid paths
        - execute the backup job twice
        - list_all_snapshots
        - check that we have result from the two ResticRepo, dict with two keys inside
        - check there are two snapshots created by the backup for every ResticRepo
        """
        clients = self.restic_client_names
        paths = [self.backup_dir.name]
        backupjob = self._create_backupjob(clients, paths)
        for _ in range(2):
            backupjob.execute(block=True)
        result = backupjob.list_all_snapshots()
        self.assertEqual(2, len(result))
        for client in clients:
            self.assertEqual(2, len(result[client]))

    def test08_restore_latest_snapshots(self):
        """Test case for test restoring the latest snapshots for a backup job.

        **Test Scenario**
        - create new backup job
        - configure it with existing single ResticRepo
        - configure it with valid paths
        - execute the backup job
        - add a new test file to the backup test dir
        - execute the backup job again
        - restore latest snapshot to an empty target dir
        - check the number of restored files in the target directory
        """
        clients = self.restic_client_names[:1]
        paths = [self.backup_dir.name]
        backupjob = self._create_backupjob(clients, paths)
        backupjob.execute(block=True)
        fs.touch(fs.join_paths(self.backup_dir.name, "include", "test3.txt"))
        backupjob.execute(block=True)
        backupjob.restore(clients[0], target_path=self.restore_dir.name)
        restored_files = [path for path in fs.pathlib.Path(self.restore_dir.name).rglob("test*.txt")]
        self.assertEqual(3, len(restored_files))

    def test09_restore_specific_snapshot_by_valid_id(self):
        """Test case for test restoring specific snapshot by id.

        **Test Scenario**
        - create new backup job
        - configure it with existing single ResticRepo
        - configure it with valid paths
        - execute the backup job
        - add a new test file to the backup test dir
        - execute the backup job again
        - get the first snapshot id
        - restore the specified snapshot by id
        - check the number of restored files in the target directory
        """
        clients = self.restic_client_names[:1]
        paths = [self.backup_dir.name]
        backupjob = self._create_backupjob(clients, paths)
        backupjob.execute(block=True)
        fs.touch(fs.join_paths(self.backup_dir.name, "include", "test3.txt"))
        backupjob.execute(block=True)
        snapshots = backupjob.list_snapshots(clients[0])
        backupjob.restore(clients[0], target_path=self.restore_dir.name, snapshot_id=snapshots[0]["id"])
        restored_files = [path for path in fs.pathlib.Path(self.restore_dir.name).rglob("test*.txt")]
        self.assertEqual(2, len(restored_files))

    def test10_restore_snapshot_by_invalid_id(self):
        """Test case for test restoring a backup job giving invalid id.

        **Test Scenario**
        - create new backup job
        - configure it with existing single ResticRepo
        - configure it with valid paths
        - execute the backup job
        - check that restoring the backup job given invalid id will raise a Value error
        """
        clients = self.restic_client_names[:1]
        paths = [self.backup_dir.name]
        backupjob = self._create_backupjob(clients, paths)
        backupjob.execute(block=True)
        with self.assertRaises(j.exceptions.Value):
            backupjob.restore(clients[0], target_path=self.restore_dir.name, snapshot_id="xxxxxxid")

    def test11_restore_with_no_previous_snapshots(self):
        """Test case for test restoring a backup job with no previous snapshots.

        **Test Scenario**
        - create new backup job
        - configure it with existing single ResticRepo
        - configure it with valid paths
        - check that restoring the backup job will raise a Runtime error
        """
        clients = self.restic_client_names[:1]
        paths = [self.backup_dir.name]
        backupjob = self._create_backupjob(clients, paths)
        with self.assertRaises(j.exceptions.Runtime):
            backupjob.restore(clients[0], target_path=self.restore_dir.name, snapshot_id="xxxxxxid")

    @parameterized.expand([(2,), (0,)])
    def test12_clean_snapshots(self, keep_last):
        """Test case for cleaning some/all the snapshots related to a backup job.

        **Test Scenario**
        - create new backup job
        - configure it with existing single ResticRepo
        - configure it with valid paths
        - execute the backup job four times
        - check that there are four snapshots created
        - clean all but n snapshots
        - check whe have n snapshots related to this backup job
        """
        clients = self.restic_client_names[:1]
        paths = [self.backup_dir.name]
        backupjob = self._create_backupjob(clients, paths)
        for _ in range(4):
            backupjob.execute(block=True)

        snapshots = backupjob.list_snapshots(clients[0])
        self.assertEqual(4, len(snapshots))
        backupjob.clean_snapshots(clients[0], keep_last=keep_last)
        snapshots = backupjob.list_snapshots(clients[0])
        self.assertEqual(keep_last, len(snapshots))
