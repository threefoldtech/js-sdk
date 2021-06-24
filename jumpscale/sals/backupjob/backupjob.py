from jumpscale.core.base import Base, fields
from jumpscale.sals import fs


class BackupJob(Base):
    paths = fields.List(fields.String())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def excute(self, client):
        client.repo += f'/{self.instance_name}/{j.data.time.now().format("YYYY-MM-DDTHH-mm-ssZZ")}'
        client.init_repo()
        for path in self.paths:
            exp_path = fs.expanduser(path)
            client.backup(exp_path)
