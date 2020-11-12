from jumpscale.core.base import Base, fields, StoredFactory
from enum import Enum
from .size import K8SNodeFlavor, VDCFlavor
from jumpscale.sals.zos import get as get_zos
from jumpscale.clients.explorer.models import NextAction, WorkloadType
from jumpscale.data import serializers
import hashlib


VDC_WORKLOAD_TYPES = [WorkloadType.Container, WorkloadType.Zdb, WorkloadType.Kubernetes]


class KubernetesRole(Enum):
    MASTER = "master"
    WORKER = "worker"


class KubernetesNode(Base):
    wid = fields.Integer()
    role = fields.Enum(KubernetesRole)
    ip_address = fields.IPAddress()
    size = fields.Enum(K8SNodeFlavor)


class S3Container(Base):
    wid = fields.Integer()
    ip_address = fields.IPAddress()


class S3ZDB(Base):
    wid = fields.Integer()


class S3(Base):
    minio = fields.Object(S3Container)
    zdbs = fields.List(fields.Object(S3ZDB))


class UserVDC(Base):
    vdc_name = fields.String()
    owner_tname = fields.String()
    solution_uuid = fields.String()
    identity_tid = fields.Integer()
    flavor = fields.Enum(VDCFlavor)
    s3 = fields.Object(S3)
    kubernetes = fields.List(fields.Object(KubernetesNode))


class VDCStoredFactory(StoredFactory):
    def find(self, name, owner_tname=None):
        instance = super().find(name)
        if not instance:
            return
        if owner_tname and instance.owner_tname != owner_tname:
            return
        for workload in self._filter_vdc_workloads(instance.identity_tid, instance.solution_uuid):
            instance = self._update_instance(instance, workload)
        return instance

    def list(self, owner_tname):
        _, _, instances = self.find_many(owner_tname=owner_tname)
        result = []
        for instance in instances:
            instance_vdc_workloads = self._filter_vdc_workloads(instance.identity_tid, instance.solution_uuid)
            for workload in instance_vdc_workloads:
                instance = self._update_instance(instance, workload)
            result.append(instance)
        return result

    @staticmethod
    def _filter_vdc_workloads(identity_tid, solution_uuid):
        zos = get_zos()
        user_workloads = zos.workloads.list(identity_tid, next_action=NextAction.DEPLOY)
        result = []
        for workload in user_workloads:
            if workload.info.workload_type not in VDC_WORKLOAD_TYPES:
                continue
            if not workload.info.description:
                continue
            try:
                description = serializers.json.loads(workload.info.description)
            except:
                continue
            if description.get("solution_uuid") != solution_uuid:
                continue
            result.append(workload)
        return result

    @staticmethod
    def _update_instance(instance, workload):
        if workload.info.workload_type == WorkloadType.Kubernetes:
            node = KubernetesNode()
            node.wid = workload.id
            node.ip_address = workload.ipaddress
            if workload.master_ips:
                node.role = KubernetesRole.WORKER
            else:
                node.role = KubernetesRole.MASTER
            instance.kubernetes.append(node)
        elif workload.info.WorkloadType == WorkloadType.Container:
            container = S3Container()
            container.wid = workload.id
            container.ip_address = workload.network_connection[0].ipaddress
            instance.s3.minio = container
        elif workload.info.workload_type == WorkloadType.Zdb:
            zdb = S3ZDB()
            zdb.wid = workload.id
            instance.s3.zdbs.append(zdb)
        return instance


VDCFACTORY = VDCStoredFactory(UserVDC)
VDCFACTORY.always_relaod = True
