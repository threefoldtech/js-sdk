from jumpscale.core.base import Base, fields
from jumpscale.sals import fs
from jumpscale.data import time


class BackupJob(Base):
    paths = fields.List(fields.String())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def excute(self, client):
        for path in self.paths:
            exp_path = fs.expanduser(path)
            client.backup(exp_path, tags=[self.instance_name])
