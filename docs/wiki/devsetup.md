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


## releasing & publishing
- make sure the version is bumped in `pyproject.toml` file
- make sure to call `poetry build`
- then publish to pypi using `poetry publish` (note that this requires to be on the publisher account)



# using js-ng in edit mode

## clone repositories

```
➜  js git clone git@github.com:threefoldtech/js-ng.git
Cloning into 'js-ng'...
remote: Enumerating objects: 419, done.
remote: Counting objects: 100% (419/419), done.
remote: Compressing objects: 100% (207/207), done.
remote: Total 11060 (delta 232), reused 298 (delta 153), pack-reused 10641
Receiving objects: 100% (11060/11060), 4.99 MiB | 3.16 MiB/s, done.
Resolving deltas: 100% (6854/6854), done.
➜  js git clone git@github.com:threefoldtech/js-grid.git    
Cloning into 'js-grid'...
remote: Enumerating objects: 123, done.
remote: Counting objects: 100% (123/123), done.
remote: Compressing objects: 100% (87/87), done.
remote: Total 123 (delta 27), reused 109 (delta 19), pack-reused 0
Receiving objects: 100% (123/123), 105.05 KiB | 860.00 KiB/s, done.
Resolving deltas: 100% (27/27), done.
```

## set the filesystem path for the repositories you want to develop against

Here we will link js-ng dependency to use the filesystem path `/home/xmonader/wspace/js/js-ng`

```
➜  js-grid git:(master) ✗ cat pyproject.toml| grep js-ng
js-ng = { path = "/home/xmonader/wspace/js/js-ng", develop = true }
```


## poetry install

```
➜  js-grid git:(master) ✗ poetry install
Installing dependencies from lock file
Warning: The lock file is not up to date with the latest changes in pyproject.toml. You may be getting outdated dependencies. Run update to update them.

Package operations: 56 installs, 0 updates, 0 removals

  • ...... REMOVED FOR REDABILITY
  • Installing js-ng (11.0b11 /home/xmonader/wspace/js/js-ng)
  • ...... REMOVED FOR REDABILITY
```
Here we notice the installation of js-ng dependency is using the filesystem path `/home/xmonader/wspace/js/js-ng` 



## Errors / Debugging

if still not reflecting, you can go to the virtual env and for `.pth` file. for example in case of `js-ng` 

### Go to venv directory
➜  site-packages git:(master) ✗ pwd
/home/xmonader/wspace/js/js-grid/.venv/lib/python3.8/site-packages

### link manually the js-ng
➜  site-packages git:(master) ✗ cat js_ng.pth 
/home/xmonader/wspace/js/js-ng