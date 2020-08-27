from jumpscale.core.base import Base, fields
from enum import Enum


class UserPool(Base):
    pool_id = fields.Integer()
    owner = fields.String()


class DeployStatus(Enum):
    FAILURE = 0
    EXPIRED = 1
    DEPLOYING = 2
    DEPLOY = 3


class BackupSolution(Base):
    restic_password = fields.Secret()
    workload_id = fields.String()
    domain = fields.String()
    status = fields.Enum(DeployStatus)
    action_time = fields.DateTime()
