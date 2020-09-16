from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method

INSTANCE_NAME = "minio_backup"
MINIO_URL = "s3:{}/threebotbackup"


class MinioBackup(BaseActor):
    @actor_method
    def repos_exist(self) -> bool:
        return INSTANCE_NAME in j.tools.restic.list_all()

    @actor_method
    def init(self, minio_url, password, access_key, secret_key) -> str:
        minio = j.tools.restic.get(INSTANCE_NAME)
        minio.repo = MINIO_URL.format(minio_url)
        minio.password = password
        minio.extra_env = {"AWS_ACCESS_KEY_ID": access_key, "AWS_SECRET_ACCESS_KEY": secret_key}
        try:
            minio.init_repo()
        except Exception as e:
            j.tools.restic.delete(INSTANCE_NAME)
            raise j.exceptions.Value(f"Couldn't create restic repo with given data {e}")
        else:
            minio.save()

        return j.data.serializers.json.dumps({"data": "backup repos inited"})

    def _get_instance(self):
        if INSTANCE_NAME not in j.tools.restic.list_all():
            raise j.exceptions.Value("Please configure backup first")
        return j.tools.restic.get(INSTANCE_NAME)

    @actor_method
    def backup(self, tags=None) -> str:
        if tags:
            tags = tags.split(",")
        else:
            tags = []

        tags.append(str(j.data.time.now().timestamp))
        instance = self._get_instance()
        instance.backup(j.core.dirs.JSCFGDIR, tags=tags)
        return j.data.serializers.json.dumps({"data": "backup done"})

    @actor_method
    def snapshots(self, tags=None) -> str:
        if tags:
            tags = tags.split(",")
        instance = self._get_instance()
        result = list(reversed(instance.list_snapshots(tags=tags)))
        return j.data.serializers.json.dumps({"data": result})

    @actor_method
    def restore(self) -> str:
        instance = self._get_instance()
        instance.restore("/")
        return j.data.serializers.json.dumps({"data": "data restored"})

    @actor_method
    def enable_auto_backup(self) -> str:
        instance = self._get_instance()
        instance.auto_backup(j.core.dirs.JSCFGDIR)
        return j.data.serializers.json.dumps({"data": "auto backup enabled"})

    @actor_method
    def check_auto_backup(self) -> bool:
        instance = self._get_instance()
        return instance.auto_backup_running(j.core.dirs.JSCFGDIR)

    @actor_method
    def disable_auto_backup(self) -> str:
        instance = self._get_instance()
        instance.disable_auto_backup(j.core.dirs.JSCFGDIR)
        return j.data.serializers.json.dumps({"data": "auto backup disabled"})


Actor = MinioBackup
