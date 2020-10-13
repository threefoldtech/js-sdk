### test01_github_client_get_access

Test case for get access to client.

**Test Scenario**

- Get client userdata.
- Check client email.

### test02_github_create_repo

Test case for creating a repository.

**Test Scenario**

- Get a github client.
- Create a repository.
- Check that this repository has been created.

### test03_github_delete_repo

Test case for deleting a repository.

**Test Scenario**

- Get a github client.
- Create a repository.
- Delete this repository.
- Check that this repository has been deleted.

### test04_github_set_file

Test case for set a file to repository.

**Test Scenario**

- Get a github client.
- Create repository with auto init.
- Create file and set to repository
- Download directory.
- Check if file has been sent.
- Check downloaded file content.

### test05_github_create_milestoes

Test case for creating a milestones.

**Test Scenario**

- Get a github client.
- Create repository with auto init.
- Create milestones.
- Check if milestones has been created.

### test06_github_create_issue

Test case for creating issue.

**Test Scenario**

- Get a github client
- Create repository with auto init.
- Create issue.
- Check if issue has been created.

### test07_github_issue_with_milestone

Test case for creating issue with milestone.

**Test Scenario**

- Create repository with auto init.
- Create milestone
- Create issue with milestone
- Check if issue have a milestone
