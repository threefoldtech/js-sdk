from jumpscale.core.base import Base, fields
from enum import Enum


class ThreebotState(Enum):
    RUNNING = "RUNNING"  # the workloads are deployed and running
    DELETED = "DELETED"  # workloads and backups deleted
    STOPPED = "STOPPED"  # expired or manually stoped (delete workloads only)


class UserThreebot(Base):
    # instance name is the f"threebot_{solution uuid}"
    solution_uuid = fields.String()
    identity_tid = fields.Integer()
    name = fields.String()
    owner_tname = fields.String()  # owner's tname in 3bot connect after cleaning
    farm_name = fields.String()
    state = fields.Enum(ThreebotState)
    continent = fields.String()
    explorer_url = fields.String()
    threebot_container_wid = fields.Integer()
    trc_container_wid = fields.Integer()
    reverse_proxy_wid = fields.Integer()
    subdomain_wid = fields.Integer()
