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


class BackupSolutionInfo(Base):
    solution_name = fields.String()
    gateway_id = fields.String()
    domain = fields.String()
    addresses = fields.List(fields.String())
    vol_size = fields.Integer()
    secret_env = fields.Secret()
    solution_port = fields.Integer()
    enforce_https = fields.String()
    # email = fields.String() # j.core.identity.me.email
    # network_name = fields.String() # workload.network_connection[0].network_id
    # node_id = fields.String() # workload.info.node_id
    # pool_id = fields.String() # workload.info.pool_id
    # capacity = fields.Typed(dict) # workload.capacity
    # flist_url = fields.String() # workload.flist
    # vol_mount_points = fields.List() # workload.volumes
    # env = fields.Typed(dict) # workload.environment
    # entrypoint = fields.String() # workload.entrypoint


class BackupSolution(Base):
    restic_password = fields.Secret()
    workload_ids = fields.Typed(dict)
    domain = fields.String()
    status = fields.Enum(DeployStatus)
    action_time = fields.DateTime()
    secret_env = fields.Secret()
