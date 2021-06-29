from jumpscale.loader import j
from tests.base_tests import BaseTests
from jumpscale.core.exceptions import NotFound
from jumpscale.sals import fs
from jumpscale.sals.backupjob.backupjob import BackupJob
import tempfile


class TestBackupjob(BaseTests):
    @classmethod
    def setUpClass(cls):
        if not j.sals.process.is_installed("restic"):
            raise NotFound(f"restic not installed")
        # configure the main directory to run all tests
        cls.main_dir = tempfile.TemporaryDirectory()
        # create two restic clients to use in all tests
        cls.restic_client_names = [f"{cls.random_name()}_client1", f"{cls.random_name()}_client2"]
        cls._create_restic_repos()

    @classmethod
    def _create_restic_repos(cls):
        for i, client_name in enumerate(cls.restic_client_names):
            restic_client = j.tools.restic.new(client_name)
            restic_client.repo = fs.join_paths(cls.main_dir.name, f"repo{i}")
            restic_client.password = "password"
            restic_client.save()

    @classmethod
    def tearDownClass(cls):
        for client_name in cls.restic_client_names:
            j.tools.restic.delete(client_name)
        cls.main_dir.cleanup()

    def setUp(self):
        self.backup_dir = tempfile.TemporaryDirectory(dir=self.main_dir.name)
        self.restore_dir = tempfile.TemporaryDirectory(dir=self.main_dir.name)
        self.files = {"include": ["test1.txt", "test2.txt"], "exclude": ["test1.exclude", "test2.exclude"]}
        self._create_dirs_to_backup()

        self.backupjob = None

    def _create_backupjob(self, clients, paths, paths_to_exclude=None):
        self.backupjob = j.sals.backupjob.new(self.random_name())
        self.backupjob.clients = clients
        self.backupjob.paths = paths
        self.backupjob.paths_to_exclude = paths_to_exclude
        self.backupjob.save()
        return self.backupjob

    def _create_dirs_to_backup(self):
        # create some files
        for dir_name, file_names in self.files.items():
            dir_path = fs.join_paths(self.backup_dir.name, dir_name)
            fs.mkdir(dir_path)
            for file_name in file_names:
                fs.touch(fs.join_paths(dir_path, file_name))

    def tearDown(self):
        j.sals.backupjob.delete(self.backupjob.instance_name)
        self.backup_dir.cleanup()

    def test01_create_backupjob(self):
        """Test case for test creating a backup job

        **Test Scenario**
        - create new backup job
        - configure it with existing restic client
        - configure it with valid paths
        """
        clients = self.restic_client_names[:1]
        paths = [self.backup_dir.name]
        backupjob = self._create_backupjob(clients, paths)
        assert isinstance(backupjob, BackupJob)
