from enum import Enum

from jumpscale.core.base import Base, fields
from jumpscale.loader import j
import netaddr

from jumpscale.sals.zos import get as get_zos

from .size import VDC_SIZE
from jumpscale.clients.explorer.models import VMSIZES


K8S_SIZES = VDC_SIZE.K8S_SIZES


class VDCWorkloadBase(Base):
    wid = fields.Integer()
    node_id = fields.String()
    pool_id = fields.Integer()


class VDCHostBase(VDCWorkloadBase):
    ip_address = fields.IPAddress()

    @classmethod
    def from_workload(cls, workload):
        host = cls()
        host.node_id = workload.info.node_id
        host.pool_id = workload.info.pool_id
        host.wid = workload.id
        host.ip_address = workload.network_connection[0].ipaddress
        return host


class KubernetesRole(Enum):
    MASTER = "master"
    WORKER = "worker"


class PublicIP(Base):
    wid = fields.Integer(default=None)
    address = fields.String(default="")


class VMachine(VDCWorkloadBase):
    name = fields.String()
    public_ip = fields.Object(PublicIP)
    size = fields.Integer()
    resources = fields.Typed(dict)
    ip_address = fields.String(default="")

    @classmethod
    def from_workload(cls, workload):
        vmachine = cls()
        vmachine.wid = workload.id
        metadata = j.sals.reservation_chatflow.reservation_chatflow.decrypt_reservation_metadata(workload.info.metadata)
        metadata = j.data.serializers.json.loads(metadata)
        vmachine.name = metadata["form_info"]["name"]
        vmachine.pool_id = workload.info.pool_id
        vmachine.node_id = workload.info.node_id
        vmachine.size = workload.size
        vmachine.resources = VMSIZES.get(workload.size)
        vmachine.ip_address = workload.ipaddress
        if workload.public_ip:
            vmachine.public_ip.wid = workload.public_ip
            zos = get_zos()
            public_ip_workload = zos.workloads.get(workload.public_ip)
            address = str(netaddr.IPNetwork(public_ip_workload.ipaddress).ip)
            vmachine.public_ip.address = address

        return vmachine


class KubernetesNode(VDCHostBase):
    role = fields.Enum(KubernetesRole)
    public_ip = fields.IPRange()
    _size = fields.Integer()

    @property
    def size(self):
        return VDC_SIZE.K8SNodeFlavor(self._size)

    @classmethod
    def from_workload(cls, workload):
        node = cls()
        node.wid = workload.id
        node.ip_address = workload.ipaddress
        if workload.master_ips:
            node.role = KubernetesRole.WORKER
        else:
            node.role = KubernetesRole.MASTER
        node.node_id = workload.info.node_id
        node.pool_id = workload.info.pool_id
        if workload.public_ip:
            zos = get_zos()
            public_ip_workload = zos.workloads.get(workload.public_ip)
            address = str(netaddr.IPNetwork(public_ip_workload.ipaddress).ip)
            node.public_ip = address

        node._size = (
            VDC_SIZE.K8SNodeFlavor(workload.size).value
            if workload.size in [size.value for size in K8S_SIZES]
            else VDC_SIZE.K8SNodeFlavor.SMALL.value
        )
        return node


class S3Container(VDCHostBase):
    pass


class S3ZDB(VDCHostBase):
    size = fields.Integer()
    port = fields.Integer()
    namespace = fields.String()
    proxy_address = fields.String()

    @classmethod
    def from_workload(cls, workload):
        result_json = j.data.serializers.json.loads(workload.info.result.data_json)
        if not result_json:
            j.logger.warning(f"Couldn't get result details for zdb workload: {workload.id}")
            return
        if "IPs" in result_json:
            ip = result_json["IPs"][0]
        else:
            ip = result_json["IP"]
        namespace = result_json["Namespace"]
        port = result_json["Port"]
        zdb = cls()
        zdb.node_id = workload.info.node_id
        zdb.pool_id = workload.info.pool_id
        zdb.wid = workload.id
        zdb.size = workload.size
        zdb.ip_address = ip
        zdb.port = port
        zdb.namespace = namespace
        return zdb


class S3(Base):
    minio = fields.Object(S3Container)
    zdbs = fields.List(fields.Object(S3ZDB))
    domain = fields.String()
    domain_wid = fields.Integer()


class ETCDNode(VDCHostBase):
    pass


class VDCThreebot(VDCHostBase):
    domain = fields.String()


__all__ = ["VDCThreebot", "S3", "VMachine", "S3ZDB", "S3Container", "KubernetesNode", "KubernetesRole", "ETCDNode"]
