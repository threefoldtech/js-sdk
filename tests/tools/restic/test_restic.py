from jumpscale.loader import j
from jumpscale.core.exceptions import NotFound, Runtime
from unittest import TestCase


class TempDir:
    def __init__(self):
        self.name = j.data.random_names.random_name()
        while j.sals.fs.exists(self.name):
            self.name = j.data.random_names.random_name()
        self.name = j.sals.fs.join_paths(j.sals.fs.cwd(), self.name)
        j.sals.fs.mkdir(self.name)

    def cleanup(self):
        """Remove the directory"""
        j.sals.fs.rmtree(self.name)

    def clear_contents(self):
        """Keep the directory but remove its contents"""
        dir_name = self.name
        for file_path in j.sals.fs.walk_non_recursive(dir_name):
            if j.sals.fs.is_file(file_path):
                j.sals.fs.unlink(file_path)
            elif j.sals.fs.is_dir(file_path):
                j.sals.fs.rmtree(file_path)


class TestRestic(TestCase):
    @classmethod
    def setUpClass(cls):
        if not j.sals.process.is_installed("restic"):
            raise NotFound(f"restic not installed")

    def setUp(self):
        """Initialize a repo and change current directory to a newly created temp directory"""
        self.original_dir = j.sals.fs.cwd()
        self.temps = []
        self.repos_temp_dir = self._create_temp_dir()
        j.sals.fs.change_dir(self.repos_temp_dir.name)
        self.instance_name = j.data.random_names.random_name()
        self.password = self._random_name()
        self.instance = j.tools.restic.new(self.instance_name, password=self.password, repo=self.instance_name)
        self.instance.init_repo()

    def _create_temp_dir(self):
        """Return a new temp directory"""
        temp_dir = TempDir()
        self.temps.append(temp_dir)
        return temp_dir

    def _create_random_dir(self, n=21):
        """Create a directory with n items

        Args:
            n (int, optional): The number of nested items (files and directories)

        Returns:
            TempDir: The created temp directory
        """
        d = self._create_temp_dir()
        d_dict = self._create_random_dir_dict()
        self._fill_dir(d.name, d_dict)
        return d

    def _random_name(self):
        """Return a random name"""
        return str(j.data.idgenerator.uuid.uuid4())

    def _random_content(self):
        """Return a random string with length between 10 and 100"""
        length = j.data.idgenerator.random_int(10, 100)
        res = ""
        for _ in range(length):
            res += chr(j.data.idgenerator.random_int(97, 123))
        return res

    def _generate_random_tree(self, n):
        """Generate a random rooted directed tree to be used as a representation for a directory

        Args:
            n (int, optional): The number of nested items (files and directories)

        Returns:
            TempDir: The adjacency list of the tree
        """
        adjacency_list = [[] for i in range(n)]
        for i in range(1, n):
            parent = j.data.idgenerator.random_int(0, i - 1)
            adjacency_list[parent].append(i)
        return adjacency_list

    def _get_file_object(self, node, adjacency_list):
        """Return a dict if the node represents a dir, otherwise it returns a string with the file content

        Args:
            node (int): The node to be processed in the tree
            adjacency_list (list[list]): The adjacency list of the tree

        Returns:
            (dict | string)
        """
        if len(adjacency_list[node]) == 0:
            return self._random_content()
        res = {}
        for i in adjacency_list[node]:
            res[self._random_name()] = self._get_file_object(i, adjacency_list)
        return res

    def _create_random_dir_dict(self, n=21):
        """Create a directory dict with n items

        Args:
            n (int, optional): The number of nested items (files and directories)

        Returns:
            TempDir: The created temp directory
        """
        tree = self._generate_random_tree(n)
        return self._get_file_object(0, tree)

    def _fill_dir(self, dir_name, dir_dict):
        """Fill the directory at the given path with directory dict

        Args:
            dir_name  (str): The path of the directory
            dir_dict (dict): The dict representation of the directory
        """
        for k, v in dir_dict.items():
            if isinstance(v, dict):
                self._fill_dir(j.sals.fs.join_paths(dir_name, k), v)
            else:
                j.sals.fs.mkdirs(dir_name, exist_ok=True)
                file_path = j.sals.fs.join_paths(dir_name, k)
                with open(file_path, "w+") as f:
                    f.write(v)

    def _canonicalize(self, path):
        """Return a cononical form of the directory, used for comparison

        Args:
            path (str): The directory path
        """
        res = {}  # path: content
        for f in j.sals.fs.walk(path):
            if j.sals.fs.is_file(f):
                # basename can be used here, no need to use full path
                # as the output can be different with different restic versions
                # and basenames are already UUIDs
                res[j.sals.fs.basename(f)] = j.sals.fs.read_file(f)
        return res

    def _check_dirs_equal(self, first_dir, second_dir):
        """Check if the two directories have the same content

        Args:
            first_dir (str): The first directory path
            second_dir (str): The second directory path
        """
        return self._canonicalize(first_dir) == self._canonicalize(second_dir)

    def test01_backup_restore(self):
        """Test case for simple directory backup and restore.

        **Test Scenario**

        - Create a directory with random content.
        - Create another empty directory to restore the backup in it.
        - Use restic to back it up.
        - Use restic to restore it to the backup directory.
        - Check that the restored content and the original are the same.
        """
        original_dir = self._create_random_dir()
        j.logger.info(f"Created a random directory in {original_dir.name}")
        backup_dir = self._create_temp_dir()
        j.logger.info("Creating a backup of this directory")
        self.instance.backup(original_dir.name, tags=["tag1", "tag2"])
        j.logger.info(f"Restoring and checking the backup in {backup_dir.name}")
        self.instance.restore(backup_dir.name, path=original_dir.name)
        self.assertTrue(self._check_dirs_equal(original_dir.name, backup_dir.name))

    def test02_multiple_restores(self):
        """Test case for directory backup and restore with modifications.

        **Test Scenario**

        - Create a directory with random content.
        - Create another directory with random content.
        - Use restic to make a backup of the first directory.
        - Change the contents of the first directory.
        - Make another backup of the first directory.
        - Backup the new version of the first directory.
        - Check that the backup and the new version are the same.
        - Backup the old version of the first directory
        - Check that the backup and the old version are the same.
        - Restore the latest backup using host name.
        - Check that the backup and the new version are the same.
        """
        second_dir_dict = self._create_random_dir_dict()
        original_dir = self._create_random_dir()
        j.logger.info(f"Created a random directory in {original_dir.name}")
        first_dir_copy = self._create_temp_dir()
        backup_dir = self._create_temp_dir()
        j.logger.info("Creating a backup of this directory")
        self.instance.backup(original_dir.name, tags=["tag1", "tag2"])
        j.logger.info(f"Creating a manual copy of this directory in {first_dir_copy.name}")
        j.sals.fs.copy_tree(original_dir.name, first_dir_copy.name)
        original_dir.clear_contents()
        j.logger.info("Overriding the original directory with new content")
        self._fill_dir(original_dir.name, second_dir_dict)
        j.logger.info("Creating another backup of this directory")
        self.instance.backup(original_dir.name, tags=["tag3", "tag4"])
        snapshots = self.instance.list_snapshots()
        j.logger.info(f"Restoring and checking the new version in {backup_dir.name}")
        self.instance.restore(backup_dir.name, snapshot_id=snapshots[1]["id"])
        self.assertTrue(self._check_dirs_equal(original_dir.name, backup_dir.name))

        backup_dir.clear_contents()
        j.logger.info(f"Restoring and checking the old version in {backup_dir.name}")
        self.instance.restore(backup_dir.name, snapshot_id=snapshots[0]["id"])
        self.assertTrue(self._check_dirs_equal(first_dir_copy.name, backup_dir.name))

        backup_dir.clear_contents()
        j.logger.info(f"Restoring and checking the latest version of the original directory using the hostname")
        self.instance.restore(backup_dir.name, host=j.sals.nettools.get_host_name())
        self.assertTrue(self._check_dirs_equal(original_dir.name, backup_dir.name))

    def test03_snapshot_listing(self):
        """Test case for snapshots listing.

        **Test Scenario**

        - Make two directories with random content.
        - Backup the first then the second then the third with tags: [tag1, tag2], [tag2, tag3], [tag2, tag3].
        - List the snapshots using the tag name [(tag1), (tag2), (tag3), (tag1, tag3)].
        - Check that any snapshot that had a tag that was passed is included in the result.
        - Check listing with the path.
        """
        first_dir = self._create_random_dir()
        second_dir = self._create_random_dir()
        j.logger.info(f"Created two random directories in {first_dir.name} and {second_dir.name}")
        self.instance.backup(first_dir.name, tags=["tag1", "tag2"])
        self.instance.backup(second_dir.name, tags=["tag2", "tag3"])
        self.instance.backup(first_dir.name, tags=["tag2", "tag3"])
        j.logger.info("Created multiple backups with different tags")

        snapshots = self.instance.list_snapshots()
        tag1_snapshot = self.instance.list_snapshots(tags=["tag1"])
        tag2_snapshot = self.instance.list_snapshots(tags=["tag2"])
        tag3_snapshot = self.instance.list_snapshots(tags=["tag3"])
        tag13_snapshot = self.instance.list_snapshots(tags=["tag1", "tag3"])
        latest_tag2_snapshots = self.instance.list_snapshots(tags=["tag2"], last=True)
        working_dir_snapshots = self.instance.list_snapshots(path=first_dir.name)
        j.logger.info("Fetching various combination of tags and checking them")
        self.assertEqual(len(tag1_snapshot), 1)
        self.assertEqual(len(tag2_snapshot), 3)
        self.assertEqual(len(tag3_snapshot), 2)
        self.assertEqual(len(tag13_snapshot), 3)
        self.assertEqual(tag1_snapshot[0]["id"], snapshots[0]["id"])
        self.assertEqual(tag2_snapshot[0]["id"], snapshots[0]["id"])
        self.assertEqual(tag2_snapshot[1]["id"], snapshots[1]["id"])
        self.assertEqual(tag3_snapshot[0]["id"], snapshots[1]["id"])
        self.assertEqual(latest_tag2_snapshots[0]["id"], snapshots[1]["id"])
        self.assertEqual(latest_tag2_snapshots[1]["id"], snapshots[2]["id"])
        self.assertEqual(working_dir_snapshots[0]["id"], snapshots[0]["id"])

    def test04_autobackup(self):
        """Test case for auto backup.

        **Test Scenario**

        - Make a directory with random content.
        - Check that there's no backup running.
        - Turn on auto backup and check it's turned on.
        - Turn it off and check it's off.
        """
        working_dir = self._create_random_dir()
        j.logger.info(f"Created a random directory in {working_dir.name}")
        j.logger.info("Checking no autobackup is running initially")
        self.assertFalse(self.instance.auto_backup_running(working_dir.name))
        j.logger.info("Making an autobackup of this dir")
        self.instance.auto_backup(working_dir.name)
        j.logger.info("Checking the autobackup job is running")
        self.assertTrue(self.instance.auto_backup_running(working_dir.name))
        j.logger.info("Disabling the autobackup")
        self.instance.disable_auto_backup(working_dir.name)
        j.logger.info("Checking the autobackup job is not running")
        self.assertFalse(self.instance.auto_backup_running(working_dir.name))

    def test05_remove_snapshots(self):
        """Test case for snapshot removal.

        **Test Scenario**

        - Create multiple snapshots.
        - Check all of them are created.
        - Remove all but the last one.
        - Check only one snapshot remains.
        """
        working_dir = self._create_random_dir()
        j.logger.info(f"Created a random directory in {working_dir.name}")
        j.logger.info("Creating muliple snapshots of it")
        self.instance.backup(working_dir.name)
        self.instance.backup(working_dir.name)
        self.instance.backup(working_dir.name)
        j.logger.info("Making sure all of them are listed")
        snapshots = self.instance.list_snapshots()
        latest = snapshots[-1]
        self.assertEqual(len(snapshots), 3)
        j.logger.info("Forget all but the last")
        self.instance.forget(keep_last=1, prune=True)
        j.logger.info("Ensuring the last one is the only one remaining")
        snapshots = self.instance.list_snapshots()
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(latest["id"], snapshots[0]["id"])

    def test06_raises(self):
        """Test case for unusual inputs.

        **Test Scenario**

        - Call restore without passing it any info.
        - Restore a directory that wasn't backed up.
        """
        j.logger.info("Testing restoring with no sufficient data")
        with self.assertRaises(ValueError):
            self.instance.restore("./asd", latest=False)
        j.logger.info("Restoring a non-existent backup")
        with self.assertRaises(Runtime):
            self.instance.restore("./asd", path="sadf")

    def tearDown(self):
        """Clean up all created temp directories and removes the restic instance"""
        self.instance.forget(keep_last=0)
        j.tools.restic.delete(self.instance_name)
        for temp_dir in self.temps:
            temp_dir.cleanup()
        j.sals.fs.change_dir(self.original_dir)
