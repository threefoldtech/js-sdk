# Development environment
Here we discuss preparing developer's machine for js-ng development

- install [poetry](https://poetry.eustace.io)
- clone this repository, then
    - `poetry install`

## Accessing the virtualenv
To access the virtual env `poetry shell`

## Interacting with js-ng Environment
if you are out of the virtualenv shell, make sure to prefix all of your commands with `poetry run`


## Accessing jsng (custom shell)

just type `jsng`.

if you have any problems related to `setuptools`, just try to upgrade it before starting `jsng`.

```bash
python3 -m pip install setuptools -U
```

# Running tests
- `make tests`

# Generating docs
- `make docs`


# building dists
- `poetry build`

# publishing
- `poetry publish`

