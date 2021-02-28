from jumpscale.loader import j
from tempfile import NamedTemporaryFile


def mc_required(method):
    """a decorator to check if mc is installed or not

    Args:
        method (func): function to be decorated
    """

    def wrapper(self, *args, **kwargs):
        if not j.sals.process.is_installed("mc"):
            raise j.exceptions.NotFound("mc is not installed on the system")
        return method(self, *args, **kwargs)

    return wrapper


class MCAlias:
    def __init__(self, alias) -> None:
        self.alias = alias

    @mc_required
    def _execute(self, cmd):
        rc, out, err = j.sals.process.execute(cmd, showout=True)
        if rc:
            raise j.exceptions.Runtime(f"execution failed. rc: {rc}, out: {out}, err: {err}")
        return out

    def add_user(self, username, password):
        self._execute(f"mc admin user add {self.alias} {username} {password}")
        out = self._execute(f"mc admin user info {self.alias} {username} --json")
        return j.data.serializers.json.loads(out)

    def remove_user(self, username):
        self._execute(f"mc admin user remove {self.alias} {username}")

    def add_policy(self, policy_name, policy_json):
        with NamedTemporaryFile() as temp:
            temp.write(policy_json.encode())
            temp.flush()
            self._execute(f"mc admin policy add {self.alias} {policy_name} {temp.name}")

    def set_user_policy(self, policy_name, username):
        self._execute(f"mc admin policy set {self.alias} {policy_name} user={username}")

    def allow_user_to_bucket(self, username, bucket_name, policy_name=None, prefix=""):
        policy_name = policy_name or f"{username}-{bucket_name}"
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": ["s3:*"], "Resource": [f"arn:aws:s3:::{bucket_name}/{prefix}*"]}
            ],
        }
        self.add_policy(policy_name, j.data.serializers.json.dumps(policy))
        self.set_user_policy(policy_name, username)


class MinioFactory:
    @mc_required
    def _execute(self, cmd):
        rc, out, err = j.sals.process.execute(cmd, showout=True)
        if rc:
            raise j.exceptions.Runtime(f"execution failed. rc: {rc}, out: {out}, err: {err}")
        return out

    def get_alias(self, name, endpoint, ak, sk):
        cmd = f"mc alias set {name} {endpoint} {ak} {sk}"
        self._execute(cmd)
        return MCAlias(name)


def export_module_as():
    return MinioFactory()
