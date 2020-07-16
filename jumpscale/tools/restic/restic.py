"""
# Restic client

Tool to create restic repo using different backends.

## prerequisites
Make sure to isntall restic(https://restic.readthedocs.io/en/latest/020_installation.html)
On linux it can be installed as follows:

```bash
apt-get install restic
```

## Usage

### Basic usage

```python
instance = j.clients.restic.get("instance")
instance.path = /path/to/repo  # Where restic will store its data can be local or SFTP or rest check https://restic.readthedocs.io/en/latest/030_preparing_a_new_repo.html
instance.password = pass  # Password for the repo needed to access the data after init
instance.init_repo()
```

### Other Backends

To use backend such as minio you will need to set extra environment for accessing the servers.

```python
instance.extra_env = {'AWS_ACCESS_KEY_ID': 'KEY',
                      'AWS_SECRET_ACCESS_KEY': 'SECRET'}
```

### Backing up

```python
instance.backup("/my/path")
```

### Listing snapshots

```python
instance.list_snapshots()
[{'time': '2020-07-15T13:44:05.767265958Z',
  'tree': '93254cf97720d264d362c9b8d91889643e45886fe0d6b80027d2cef3910bd43d',
  'paths': ['/tmp/stc'],
  'hostname': 'jsng',
  'username': 'root',
  'id': 'e3330cf26ff4ada6c80868c08626f38fa2fc0185b0510c1bb7c5fa880bc67d0c',
  'short_id': 'e3330cf2'}]
```

### Restoring

```python
instance.restore("/path/to/store", "e3330cf26ff4ada6c80868c08626f38fa2fc0185b0510c1bb7c5fa880bc67d0c")  # Will restore specified snapshot to path
instance.restore("/path/to/store", latest=True, path="/tmp/stc", host="jsng")  # Will return latest snapshot with the specified filters
```

### Pruning data

```python
instance.forget(keep_last=10)  # Will prune all snapshots and keep the last 10 taken only
```
"""
from jumpscale.core.base import Base, fields
from jumpscale.core.exceptions import NotFound, Runtime

import subprocess
import json
import os


class ResticRepo(Base):
    path = fields.String(required=True)
    password = fields.Secret(required=True)
    extra_env = fields.Typed(dict, default={})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._check_install()
        self._env = None

    def _check_install(self):
        if subprocess.call(["which", "restic"], stdout=subprocess.DEVNULL):
            raise NotFound("Restic not installed")

    @property
    def env(self):
        if not self._env:
            self.validate()
            self._env = os.environ.copy()
            self._env.update({"RESTIC_PASSWORD": self.password, "RESTIC_REPOSITORY": self.path}, **self.extra_env)
        return self._env

    def _run_cmd(self, cmd, check=True):
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env)
        if check and p.returncode:
            raise Runtime(f"Restic command failed with {p.stderr.decode()}")
        return p

    def init_repo(self):
        """Init restic repo with data specified in the instances
        """
        p = self._run_cmd(["restic", "cat", "config"], False)
        if p.returncode > 0:
            self._run_cmd(["restic", "init"])

    def backup(self, path, tag=None):
        """Backup a path to the repo

        Args:
            path (str): local path to backup
            tag (str): tag to set to the backup
        """
        cmd = ["restic", "backup", path]
        if tag:
            cmd.extend(["--tag", tag])
        self._run_cmd(cmd)

    def restore(self, target_path, snapshot_id=None, latest=True, path=None, host=None):
        """restores a snapshot

        Args:
            target_path (str): path to restore to
            snapshot_id (str, optional): id of the snapshot. Defaults to None.
            latest (bool, optional): if True will use latest snapshot. Defaults to True.
            path (str, optional): Filter on the path when using latest. Defaults to None.
            host (str, optional): Filter on the hostname when using latest. Defaults to None.
        """
        cmd = ["restic", "--target", target_path, "restore"]
        if snapshot_id:
            cmd.append(snapshot_id)
            self._run_cmd(cmd)
        elif latest:
            args = ["latest"]
            if path:
                args.extend(["--path", path])
            if host:
                args.extend(["--host", host])
            self._run_cmd(cmd + args)
        else:
            raise ValueError("Please specify either `snapshot_id` or `latest` flag")

    def list_snapshots(self, tag=None):
        """List all snapshots in the repo
        Returns
            list : all snapshots as dicts
        """
        cmd = ["restic", "snapshots", "--json"]
        if tag:
            cmd.extend(["--tag", tag])
        p = self._run_cmd(cmd)
        return json.loads(p.stdout)

    def forget(self, keep_last=10, prune=True):
        """Deletes data in the repo

        Args:
            keep_last (str, optional): How many items to keep. Defaults to 10.
            prune (bool, optional): Whether to prune the data or not. Defaults to True.
        """
        cmd = ["restic", "forget", "--keep-last", str(keep_last)]
        if prune:
            cmd.append("--prune")
        self._run_cmd(cmd)
