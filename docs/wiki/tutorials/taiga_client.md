# Taiga client

This client is used to interact with Taiga API.

## Initialization

Using username and  password:
> client = j.clients.taiga.new('test', username='7mada', password='123456')

OR using a token
> client = j.clients.taiga.new('test', token='extra secret token string')

## Listing

### Listing issues

To get the issues of the user with id 123:
> client.list_all_issues(123)
To get the issues of all users:
> client.list_all_issues(123)

### Listing projects

To list all projects:
> client.list_all_projects()

### Listing milestones

To list all projects:
> client.list_all_milestones()

### Listing user stories

To list the user stories of the user with id 123:
> client.list_all_user_stories(123)
To list the user stories of all users:
> client.list_all_user_stories()

## Exporting

### Exporting issues
To export all issues details to the file /tmp/issues.md:
> client.export_all_issues_details('/tmp/issues.md')
it accepts the parameter with_description upon which is decided whether to print the description with the issues or not

### Exporting issues per project
To export all issues details grouped by the project to the file /tmp/issues.md:
> client.export_issues_per_project('/tmp/issues.md')
It accepts with_details to tell whether to print only the issue title or its full details

### Exporting issues for a user
To export all issues details for the username 7mada to the file /tmp/issues.md:
> client.export_issues_per_user(username='7mada', '/tmp/issues.md')
Accepts with_description

### Exporting user stories
To export all user stories to the file /tmp/stories.md:
> client.export_all_user_stories(username='7mada', '/tmp/stories.md')

## Fetching data

### Fetching user circles
> client.fetch_user_circles('7mada')

### Fetching project issues
> client.fetch_circles_issues(123) # project id

### Fetching user stories
> client.get_user_stories('7mada')

### Fetching user tasks
> client.get_user_tasks('7mada')

### Fetch issue description
> client.get_issue_description(567) # issue id

## Operations

### Move a story to a porject
> client.move_story_to_cirlce(789, 123) # story id, project id
