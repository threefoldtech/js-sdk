from jumpscale.core.base import Base, fields, StoredFactory
from enum import Enum
from .size import K8SNodeFlavor, VDCFlavor
from jumpscale.sals.zos import get as get_zos
from jumpscale.clients.explorer.models import NextAction, WorkloadType
from jumpscale.data import serializers
from jumpscale.sals.reservation_chatflow.deployer import GATEWAY_WORKLOAD_TYPES
from jumpscale.loader import j


VDC_WORKLOAD_TYPES = [
    WorkloadType.Container,
    WorkloadType.Zdb,
    WorkloadType.Kubernetes,
    WorkloadType.Subdomain,
    WorkloadType.Reverse_proxy,
]


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


class S3Subdomain(Base):
    wid = fields.Integer()


class S3ReverseProxy(Base):
    wid = fields.Integer()


class S3NginxProxy(Base):
    wid = fields.Integer()


class S3Proxy(Base):
    reverse_proxy = fields.Object(S3ReverseProxy)
    subdomain = fields.Object(S3Subdomain)
    nginx = fields.Object(S3NginxProxy)


class S3(Base):
    subdomain = fields.String()
    healer_subdomain = fields.String()
    minio = fields.Object(S3Container)
    zdbs = fields.List(fields.Object(S3ZDB))
    api_proxy = fields.Object(S3Proxy)
    healer_proxy = fields.Object(S3Proxy)


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
        instance_vdc_workloads = self._filter_vdc_workloads(instance.identity_tid, instance.solution_uuid)
        proxy_workloads = []
        for workload in instance_vdc_workloads:
            instance = self._update_instance(instance, workload)
            if workload.info.workload_type in GATEWAY_WORKLOAD_TYPES:
                proxy_workloads.append(workload)
            if workload.info.workload_type == WorkloadType.Container and "nginx" in workload.flist:
                proxy_workloads.append(workload)
        instance = self._build_domain_info(instance, proxy_workloads)
        return instance

    def list(self, owner_tname):
        _, _, instances = self.find_many(owner_tname=owner_tname)
        result = []
        proxy_workloads = []
        for instance in instances:
            instance_vdc_workloads = self._filter_vdc_workloads(instance.identity_tid, instance.solution_uuid)
            for workload in instance_vdc_workloads:
                instance = self._update_instance(instance, workload)
                if workload.info.workload_type in GATEWAY_WORKLOAD_TYPES:
                    proxy_workloads.append(workload)
                if workload.info.workload_type == WorkloadType.Container and "nginx" in workload.flist:
                    proxy_workloads.append(workload)
            instance = self._build_domain_info(instance, proxy_workloads)
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
            if description.get("vdc_uuid") != solution_uuid:
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
            instance.size = workload.size
            instance.kubernetes.append(node)
        elif workload.info.workload_type == WorkloadType.Container:
            if "minio" in workload.flist:
                container = S3Container()
                container.wid = workload.id
                container.ip_address = workload.network_connection[0].ipaddress
                instance.s3.minio = container
        elif workload.info.workload_type == WorkloadType.Zdb:
            zdb = S3ZDB()
            zdb.wid = workload.id
            instance.s3.zdbs.append(zdb)
        return instance

    @staticmethod
    def _build_domain_info(instance, proxy_worklaods):
        healer_proxy_domain = ""
        healer_nginx_domain = ""
        healer_subdomain_domain = ""

        api_proxy_domain = ""
        api_nginx_domain = ""
        api_subdomain_domain = ""

        for workload in proxy_worklaods:
            description = serializers.json.loads(workload.info.description)
            if description.get("exposed_wid") != instance.s3.minio.wid:
                j.logger.warning(
                    f"proxy workload {workload.id} of type {workload.info.workload_type} skipped because of incorrect exposed wid"
                )
                continue
            # check exposed_id in description. make sure it is pointing to the instance minio container
            if workload.info.workload_type == WorkloadType.Container:
                domain = workload.environment.get("DOMAIN")
                if domain:
                    if "healing" in domain:
                        healer_nginx_domain = domain
                        instance.s3.healer_proxy.nginx.wid = workload.id
                    else:
                        api_nginx_domain = domain
                        instance.s3.api_proxy.nginx.wid = workload.id
                else:
                    j.logger.warning(f"couldn't identity the domain of nginx container wid: {workload.id}")
            elif workload.info.workload_type == WorkloadType.Subdomain:
                domain = workload.domain
                if "healing" in domain:
                    healer_subdomain_domain = domain
                    instance.s3.healer_proxy.subdomain.wid = workload.id
                else:
                    api_subdomain_domain = domain
                    instance.s3.api_proxy.subdomain.wid = workload.id
            elif workload.info.workload_type == WorkloadType.Reverse_proxy:
                domain = workload.domain
                if "healing" in domain:
                    healer_proxy_domain = domain
                    instance.s3.healer_proxy.reverse_proxy.wid = workload.id
                else:
                    api_proxy_domain = domain
                    instance.s3.api_proxy.reverse_proxy.wid = workload.id
            else:
                j.logger.warning(f"workload {workload.id} is not a vaild workload for vdc proxy")

        if api_nginx_domain == api_proxy_domain == api_subdomain_domain:
            instance.s3.subdomain = api_nginx_domain
        else:
            j.logger.error(
                f"vdc {instance.solution_uuid} s3 api domains are conflicting. subdomain: {api_subdomain_domain}, nginx: {api_nginx_domain}, reverse_proxy: {api_proxy_domain}"
            )

        if healer_nginx_domain == healer_proxy_domain == healer_subdomain_domain:
            instance.s3.healer_subdomain = healer_nginx_domain
        else:
            j.logger.error(
                f"vdc {instance.solution_uuid} s3 healer domains are conflicting. subdomain: {healer_subdomain_domain}, nginx: {healer_nginx_domain}, reverse_proxy: {healer_proxy_domain}"
            )

        return instance


VDCFACTORY = VDCStoredFactory(UserVDC)
VDCFACTORY.always_relaod = True
