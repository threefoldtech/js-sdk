from jumpscale.core.base import Base, fields
from enum import Enum
import hashlib


class ThreebotState(Enum):
    RUNNING = "RUNNING"  # the workloads are deployed and running
    DELETED = "DELETED"  # workloads and backups deleted
    STOPPED = "STOPPED"  # expired or manually stoped (delete workloads only)
    ERROR = "ERROR"  # workloads are deployed but can't reach the threebot


class UserThreebot(Base):
    # instance name is the f"threebot_{solution uuid}"
    solution_uuid = fields.String()
    identity_tid = fields.Integer()
    name = fields.String()
    owner_tname = fields.String()  # owner's tname in ThreeFold Connect after cleaning
    farm_name = fields.String()
    state = fields.Enum(ThreebotState)
    continent = fields.String()
    explorer_url = fields.String()
    threebot_container_wid = fields.Integer()
    trc_container_wid = fields.Integer()  # deprecated for embeding trc # FIXME: Remove
    reverse_proxy_wid = fields.Integer()  # deprecated for embeding trc # FIXME: Remove
    subdomain_wid = fields.Integer()
    secret_hash = fields.String()
    proxy_wid = fields.Integer()

    def verify_secret(self, secret):
        if not self.secret_hash:
            return True
        return self.secret_hash == hashlib.md5(secret.encode()).hexdigest()

    def hash_secret(self, secret):
        self.secret_hash = hashlib.md5(secret.encode()).hexdigest()
