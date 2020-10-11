### test01_backup_restore

Test case for simple directory backup and restore.

**Test Scenario**

- Create a directory with random content.
- Create another empty directory to restore the backup in it.
- Use restic to back it up.
- Use restic to restore it to the backup directory.
- Check that the restored content and the original are the same.

### test02_multiple_restores

Test case for directory backup and restore with modifications.

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

### test03_snapshot_listing

Test case for snapshots listing.

**Test Scenario**

- Make two directories with random content.
- Backup the first then the second then the third with tags: [tag1, tag2], [tag2, tag3], [tag2, tag3].
- List the snapshots using the tag name [(tag1), (tag2), (tag3), (tag1, tag3)].
- Check that any snapshot that had a tag that was passed is included in the result.
- Check listing with the path.

### test04_autobackup

Test case for auto backup.

**Test Scenario**

- Make a directory with random content.
- Check that there's no backup running.
- Turn on auto backup and check it's turned on.
- Turn it off and check it's off.

### test05_remove_snapshots

Test case for snapshot removal.

**Test Scenario**

- Create multiple snapshots.
- Check all of them are created.
- Remove all but the last one.
- Check only one snapshot remains.

### test06_raises

Test case for unusual inputs.

**Test Scenario**

- Call restore without passing it any info.
- Restore a directory that wasn't backed up.
