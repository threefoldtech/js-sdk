#Taiga client

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
client.list_all_issues(123)

```
### Listing projects

To list all projects:
```
client.list_all_projects()
```


### Listing milestones

To list all projects:
```
client.list_all_milestones()

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


### List team circles

```
client.ist_team_circles()
```


### List project circles

```
client.list_project_circles()  ## list_team_circles, list_funnel_circles
```

### List funnel circles

```
client.list_funnel_circles()

```

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
    **attrs,
):
```

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
## Operations

### Move a story to a project

```
client.move_story_to_cirlce(789, 123) # story id, project id
```

or using a project object
```
project_object.move_issue(issue_id_or_issue_object, project_id_or_project_object)
```

### Resources urls
All of resources e.g (user, issue, user_story, circle) have `url` property


## Export objects as yaml
to export All objects as yaml all you need is

```
client.export_as_yaml("/tmp/exported_taiga_dir")

```
this will export resources (users, projects, issues, stories, milestones) in `/tmp/exported_taiga_dir/$object_type/$object_id.yaml`
