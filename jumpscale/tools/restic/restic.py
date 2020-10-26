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
instance.repo = /path/to/repo  # Where restic will store its data can be local or SFTP or rest check https://restic.readthedocs.io/en/latest/030_preparing_a_new_repo.html
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
from io import BytesIO

import subprocess
import json
import os


CRON_SCRIPT = """
epoch=$(date +%s)

export RESTIC_REPOSITORY={repo}
export RESTIC_PASSWORD={password}

restic unlock &
wait $!

restic backup --one-file-system --tag $epoch {path} &
wait $!

restic forget --keep-last {keep_last} --prune &
wait $!

restic check &
wait $!
"""

WATCHDOG_SCRIPT = """
epoch=$(date +%s)

export RESTIC_REPOSITORY={repo}
export RESTIC_PASSWORD={password}
export AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID}
export AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY}


latest_backup=`restic snapshots --last -c -q | sed -n 3p |cut -d " " -f3`
latest_backup_epoch=`date "+%s" -d "$latest_backup"`
wait $!

current_date=`date +"%s"`

if [[ $(( (current_date - latest_backup_epoch) / 86400 )) > 2 ]]
then
    echo "No backups is being taken since 2 days, sending escalation mail..."
    jsng 'j.clients.mail.escalation_instance.send("{ESCALATION_MAIL}", subject="{THREEBOT_NAME} 3Bot backups warning", message="We noticed that there were no backups taken since 2 days for {THREEBOT_NAME} 3Bot. Please check the support")'
fi

"""


class ResticRepo(Base):

    repo = fields.String(required=True)
    password = fields.Secret(required=True)
    extra_env = fields.Typed(dict, default={})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._check_install("restic")
        self._env = None

    def _check_install(self, binary):
        if subprocess.call(["which", binary], stdout=subprocess.DEVNULL):
            raise NotFound(f"{binary} not installed")

    @property
    def env(self):
        self.validate()
        self._env = os.environ.copy()
        self._env.update({"RESTIC_PASSWORD": self.password, "RESTIC_REPOSITORY": self.repo}, **self.extra_env)
        return self._env

    def _run_cmd(self, cmd, check=True):
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env)
        if check and proc.returncode:
            raise Runtime(f"Restic command failed with {proc.stderr.decode()}")
        return proc

    def init_repo(self):
        """Init restic repo with data specified in the instances
        """
        proc = self._run_cmd(["restic", "cat", "config"], False)
        if proc.returncode > 0:
            self._run_cmd(["restic", "init"])

    def backup(self, path, tags=None):
        """Backup a path to the repo

        Args:
            path (str): local path to backup
            tags (list): list of tags to set to the backup
        """
        tags = tags or []
        cmd = ["restic", "backup", path]
        for tag in tags:
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

    def list_snapshots(self, tags=None, last=False, path=None):
        """List all snapshots in the repo

        Args:
            tags (list): list of tags to filter on
            last (bool): if True will get last snapshot only while respecting the other filters
            path (str): path to filter on

        Returns
            list : all snapshots as dicts
        """
        tags = tags or []
        cmd = ["restic", "snapshots", "--json"]
        for tag in tags:
            cmd.extend(["--tag", tag])

        if path:
            cmd.extend(["--path", path])
        if last:
            cmd.append("--last")
        proc = self._run_cmd(cmd)
        return json.loads(proc.stdout)

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

    def _get_script_path(self, path):
        return os.path.join(path, f"{self.instance_name}_restic_cron")

    def _get_crons_jobs(self):
        proc = subprocess.run(["crontab", "-l"], stderr=subprocess.DEVNULL, stdout=subprocess.PIPE)
        return proc.stdout.decode()

    def auto_backup(self, path, keep_last=20):
        """Runs a cron job that backups the repo and prunes the last specified backups

        Args:
            path (str): local path to backup
            keep_last (int, optional): How many items to keep in every forgot opertaion. Defaults to 20.
        """
        self._check_install("crontab")
        script_path = self._get_script_path(path)
        cronjobs = self._get_crons_jobs()
        if not self.auto_backup_running(path):  # Check if cron job already running
            cron_script = CRON_SCRIPT.format(repo=self.repo, password=self.password, path=path, keep_last=keep_last)
            with open(script_path, "w") as rfd:
                rfd.write(cron_script)

            cron_cmd = cronjobs + f"0 0 * * * bash {script_path} \n"
            proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            proc_res = proc.communicate(input=cron_cmd.encode())
            if proc.returncode > 0:
                raise Runtime(f"Couldn't start cron job, failed with {proc_res[1]}")

    def auto_backup_running(self, path):
        """Checks if auto backup for the specified path is running or not

        Args:
            path (str): local path to backup in the cron job

        Returns:
            bool: Whether it is running or not
        """
        script_path = self._get_script_path(path)
        cronjobs = self._get_crons_jobs()
        return cronjobs.find(script_path) >= 0

    def disable_auto_backup(self, path):
        """Removes cron jon based on the path being backed

        Args:
            path (str): local path to backup in the cron job
        """
        script_path = self._get_script_path(path)
        cronjobs = self._get_crons_jobs()
        other_crons = []
        for cronjob in cronjobs.splitlines():
            if script_path not in cronjob:
                other_crons.append(cronjob)
        proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        cron_cmd = "\n".join(other_crons) + "\n"
        proc_res = proc.communicate(input=cron_cmd.encode())
        if proc.returncode > 0:
            raise Runtime(f"Couldn't remove cron job, failed with {proc_res[1]}")

    def backup_watchdog_running(self, script_path) -> bool:
        """watches a cronjob to watch backups using last snapshot time

        Args:
            script_path (str): path to the script to run the cronjob
        Returns:
            bool: True if the backup watchdog running
        """
        script_path = self._get_script_path(script_path)
        cronjobs = self._get_crons_jobs()
        return cronjobs.find(script_path) >= 0

    def start_watch_backup(self, path):
        """Runs a cron job that backups the repo and prunes the last specified backups

        Args:
            path (str): local path to backup
            keep_last (int, optional): How many items to keep in every forgot opertaion. Defaults to 20.
        """
        self._check_install("crontab")
        script_path = self._get_script_path(path)
        cronjobs = self._get_crons_jobs()
        if not self.backup_watchdog_running(path):  # Check if cron job already running
            cron_script = WATCHDOG_SCRIPT.format(
                repo=self.repo,
                password=self.password,
                path=path,
                AWS_SECRET_ACCESS_KEY=self.extra_env.get("AWS_SECRET_ACCESS_KEY"),
                AWS_ACCESS_KEY_ID=self.extra_env.get("AWS_ACCESS_KEY_ID"),
                THREEBOT_NAME=os.environ.get("THREEBOT_NAME"),
                ESCALATION_MAIL=os.environ.get("ESCALATION_MAIL"),
            )

            with open(script_path, "w") as rfd:
                rfd.write(cron_script)

            cron_cmd = cronjobs + f"0 0 */2 * * bash {script_path} \n"
            proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            proc_res = proc.communicate(input=cron_cmd.encode())
            if proc.returncode > 0:
                raise Runtime(f"Couldn't start cron job, failed with {proc_res[1]}")
