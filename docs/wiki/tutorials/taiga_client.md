# Taiga client

## Initialization

Using username and  password:
```
client = j.clients.taiga.new('test', host="https://staging.circles.threefold.me/", username='admin', password='123456')
```
OR using a token

```
client = j.clients.taiga.new('test', host="https://staging.circles.threefold.me/", token='extra secret token string')
```
## Listing

### Listing issues

To get the issues of the user with id 123:
```
client.list_all_issues(123)
```
To get the issues of all users:
```
client.list_all_issues()

```
### Listing projects

To list all projects:
```
client.list_all_projects()
```

To list all projects not start with **ARCHIVE**:
```
client.list_all_active_projects()

```
### Listing user stories

To list the user stories of the user with id 123:

```
client.list_all_user_stories(123)
```

To list the user stories of all users:

```
client.list_all_user_stories()
```

### Listing tasks

To list the tasks of the user with id 123:

```
client.list_all_tasks(123)
```

To list the tasks of all users :

```
client.list_all_tasks()
```


### List team circles

```
client.list_team_circles()
```


### List project circles

```
client.list_project_circles()
```

### List funnel circles

```
client.list_funnel_circles()

```

## Custom Fields

### Get

To get issue custom fields for the issue with id 123

```
custom_fields = client.get_issue_custom_fields(123)
```

To get user story custom fields for the story with id 123

```
custom_fields = client.get_story_custom_fields(123)
```

### Validate

To validate custom field according to [specs](https://github.com/threefoldtech/circles_reporting_tool/blob/master/specs/funnel.md#custom-fields)

```
client.validate_custom_fields(custom_fields)
```

## Creating

### Create new circle

if you want full control on the circle creation on priorities, severities, .. etc, you can use `_create_new_circle` method


```
def _create_new_circle(
    self,
    name,
    type_="team",
    description="desc",
    severities=None,
    issues_statuses=None,
    priorities=None,
    issues_types=None,
    user_stories_statuses=None,
    tasks_statuses=None,
    custom_fields=None
    **attrs,
):
```
otherwise you can use `create_new_project_circle,`, `create_new_team_circle`, `create_new_funnel_circle`


### Create new story

```
circle_object.create_story("abc")
```

### Create a new  issue

```
create_issue("my issue")
```

## Exporting

### Export users and circles

```
client.export_as_md("/tmp/taigawiki")
```

### Export users

```
client.export_users_as_md("/tmp/taigawiki")
```
### Export circles
```
client.export_circles_as_md("/tmp/taigawiki")
```

### Export users and circles periodically

To export users and circles periodically each 10 minutes
```
client.export_as_md_periodically("/tmp/taigawiki", period= 600)
```
> **period** use seconds as time unit.

### Export objects as yaml
To export All objects as yaml all you need is

```
client.export_as_yaml("/tmp/exported_taiga_dir")
```

This will export resources (users, projects, issues, stories, tasks) in `/tmp/exported_taiga_dir/$object_type/$object_id.yaml

## Importing

### Importing from yaml files

To import from yaml files _files which exported using export_as_yaml_

```
client.import_from_yaml("/tmp/exported_taiga_dir")
```
This will import resources (projects, issues, stories, tasks) as a new instance _import basic info till now_

## Operations

### Move a story to a project

```
client.move_story_to_circle(789, 123) # story id, project id
```

### Copy and Move Issue using project object
```
project_object.copy_issue(issue_id_or_issue_object, project_id_or_project_object)
project_object.move_issue(issue_id_or_issue_object, project_id_or_project_object)
```
> Keep in mind that move will delete the issue from the original project

### Resources urls
All of resources e.g (user, issue, user_story, circle, task) have `url, as_md and as_yaml` properties
