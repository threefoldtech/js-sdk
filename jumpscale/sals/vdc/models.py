from enum import Enum

from jumpscale.core.base import Base, fields

from .size import K8SNodeFlavor


class VDCWorkloadBase(Base):
    wid = fields.Integer()
    node_id = fields.String()
    pool_id = fields.Integer()


class VDCHostBase(VDCWorkloadBase):
    ip_address = fields.IPAddress()


class KubernetesRole(Enum):
    MASTER = "master"
    WORKER = "worker"


class KubernetesNode(VDCHostBase):
    role = fields.Enum(KubernetesRole)
    size = fields.Enum(K8SNodeFlavor)
    public_ip = fields.IPRange()


class S3Container(VDCHostBase):
    pass


class S3ZDB(VDCWorkloadBase):
    size = fields.Integer()


class S3(Base):
    minio = fields.Object(S3Container)
    zdbs = fields.List(fields.Object(S3ZDB))
    domain = fields.String()


class VDCThreebot(VDCHostBase):
    domain = fields.String()


__all__ = ["VDCThreebot", "S3", "S3ZDB", "S3Container", "KubernetesNode", "KubernetesRole"]
