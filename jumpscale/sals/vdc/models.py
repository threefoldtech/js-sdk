from enum import Enum

from jumpscale.core.base import Base, fields

from .size import VDC_SIZE


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
    public_ip = fields.IPRange()
    _size = fields.Integer()

    @property
    def size(self):
        return VDC_SIZE.K8SNodeFlavor(self._size)


class S3Container(VDCHostBase):
    pass


class S3ZDB(VDCHostBase):
    size = fields.Integer()
    port = fields.Integer()
    namespace = fields.String()
    proxy_address = fields.String()


class S3(Base):
    minio = fields.Object(S3Container)
    zdbs = fields.List(fields.Object(S3ZDB))
    domain = fields.String()
    domain_wid = fields.Integer()


class VDCThreebot(VDCHostBase):
    domain = fields.String()


__all__ = ["VDCThreebot", "S3", "S3ZDB", "S3Container", "KubernetesNode", "KubernetesRole"]
