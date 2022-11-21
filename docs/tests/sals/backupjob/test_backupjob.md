### test01_create_backupjob

Test case for test creating a backup job

**Test Scenario**
- create new backup job
- configure it with existing restic client
- configure it with valid paths
- assert returned value to be instance of BackupJob

### test02_create_backupjob_with_non_exists_ResticRepo

Test case for test creating a backup job with non exists ResticRepo name

**Test Scenario**
- create new backup job
- configure it with non exists restic client
- check that saving the instance will raise a ValidationError

### test03_create_backupjob_with_invalid_paths_0

Test case for test creating a backup job with relative paths [with paths=['./test']]

**Test Scenario**
- create new backup job
- configure it with relative paths
- check that saving the instance will raise a ValidationError

### test03_create_backupjob_with_invalid_paths_1

Test case for test creating a backup job with relative paths [with paths=['test/']]

**Test Scenario**
- create new backup job
- configure it with relative paths
- check that saving the instance will raise a ValidationError

### test04_execute_backupjob_with_single_ResticRepo

Test case for test creating a backup job and execute it.

**Test Scenario**
- create new backup job
- configure it with existing single ResticRepo
- configure it with valid paths
- execute the backup job
- check we have one snapshot for this BackupJob
- check the snapshots included the test files

### test05_execute_backupjob_with_multiple_ResticRepo

Test case for test creating a backup job, configured it with multiple ResticRepo and execute it.

**Test Scenario**
- create new backup job
- configure it with existing multiple ResticRepo
- configure it with valid paths
- execute the backup job
- check we have one snapshot in every ResticRepo for this BackupJob
- check the snapshots included the test files

### test06_execute_backupjob_with_single_ResticRepo_with_excluded_paths

Test case for test creating a backup job with excluded paths and execute it.

**Test Scenario**
- create new backup job with excluded paths
- configure it with existing single ResticRepo
- configure it with valid paths
- configure it with paths to exclude
- execute the backup job
- check we have one snapshot for this BackupJob
- check the excluded test files not included in the last snapshot

### test07_list_all_snapshots_grouped_by_ResticRepo

Test case for test listing the snapshots created by a backup job and grouped by the ResticRepo.

**Test Scenario**
- create new backup job
- configure it with existing multiple ResticRepo
- configure it with valid paths
- execute the backup job twice
- list_all_snapshots
- check that we have result from the two ResticRepo, dict with two keys inside
- check there are two snapshots created by the backup for every ResticRepo

### test08_restore_latest_snapshots

Test case for test restoring the latest snapshots for a backup job.

**Test Scenario**
- create new backup job
- configure it with existing single ResticRepo
- configure it with valid paths
- execute the backup job
- add a new test file to the backup test dir
- execute the backup job again
- restore latest snapshot to an empty target dir
- check the number of restored files in the target directory

### test09_restore_specific_snapshot_by_valid_id

Test case for test restoring specific snapshot by id.

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

### test10_restore_snapshot_by_invalid_id

Test case for test restoring a backup job giving invalid id.

**Test Scenario**
- create new backup job
- configure it with existing single ResticRepo
- configure it with valid paths
- execute the backup job
- check that restoring the backup job given invalid id will raise a Value error

### test11_restore_with_no_previous_snapshots

Test case for test restoring a backup job with no previous snapshots.

**Test Scenario**
- create new backup job
- configure it with existing single ResticRepo
- configure it with valid paths
- check that restoring the backup job will raise a Runtime error

### test12_clean_snapshots_0

Test case for cleaning some/all the snapshots related to a backup job [with keep_last=2].

**Test Scenario**
- create new backup job
- configure it with existing single ResticRepo
- configure it with valid paths
- execute the backup job four times
- check that there are four snapshots created
- clean all but n snapshots
- check whe have n snapshots related to this backup job

### test12_clean_snapshots_1

Test case for cleaning some/all the snapshots related to a backup job [with keep_last=0].

**Test Scenario**
- create new backup job
- configure it with existing single ResticRepo
- configure it with valid paths
- execute the backup job four times
- check that there are four snapshots created
- clean all but n snapshots
- check whe have n snapshots related to this backup job
