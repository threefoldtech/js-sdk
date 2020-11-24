import datetime
import uuid
from enum import Enum

from jumpscale.clients.explorer.models import NextAction, WorkloadType
from jumpscale.clients.stellar.stellar import Network as StellarNetwork
from jumpscale.core.base import Base, StoredFactory, fields
from jumpscale.data import serializers
from jumpscale.loader import j
from jumpscale.sals.reservation_chatflow.deployer import GATEWAY_WORKLOAD_TYPES
from jumpscale.sals.zos import get as get_zos

from .deployer import VDCDeployer
from .size import K8SNodeFlavor, VDCFlavor

VDC_WORKLOAD_TYPES = [
    WorkloadType.Container,
    WorkloadType.Zdb,
    WorkloadType.Kubernetes,
    WorkloadType.Subdomain,
    WorkloadType.Reverse_proxy,
]

"""# create and deploy a new vdc
JS-NG> vdc = VDCFACTORY.new("vdc02", "magidentfinal.3bot", VDCFlavor.SILVER)
# after funding vdc.wallet.address
JS-NG> deployer = vdc.get_deployer("123456")
JS-NG> deployer.deploy_vdc("123456", "test123456", "test123456")
"""


class VDCWallet(Base):
    vdc_uuid = fields.String()
    wallet_secret = fields.String()
    wallet_network = fields.Enum(StellarNetwork)

    def _init_wallet(self):
        if "testnet" in j.core.identity.me.explorer_url or "devnet" in j.core.identity.me.explorer_url:
            self.wallet_network = StellarNetwork.TEST
        else:
            self.wallet_network = StellarNetwork.STD

        wallet = j.clients.stellar.new(self.instance_name, network=self.wallet_network)
        wallet.save()
        self.wallet_secret = wallet.secret

    @property
    def stellar_wallet(self):
        return j.clients.stellar.get(self.instance_name)


class VDCWalletStoredFactory(StoredFactory):
    def new(self, *args, **kwargs):
        instance = super().new(*args, **kwargs)
        instance._init_wallet()
        instance.save()
        return instance


VDC_WALLET_FACTORY = VDCWalletStoredFactory(VDCWallet)


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


class S3Container(VDCHostBase):
    pass


class S3ZDB(VDCWorkloadBase):
    size = fields.Integer()


class S3Subdomain(VDCWorkloadBase):
    pass


class S3ReverseProxy(VDCWorkloadBase):
    pass


class S3NginxProxy(VDCWorkloadBase):
    pass


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


class VDCThreebot(VDCHostBase):
    pass


class UserVDC(Base):
    vdc_name = fields.String()
    owner_tname = fields.String()
    solution_uuid = fields.String(default=lambda: uuid.uuid4().hex)
    identity_tid = fields.Integer()
    flavor = fields.Enum(VDCFlavor)
    s3 = fields.Object(S3)
    kubernetes = fields.List(fields.Object(KubernetesNode))
    threebot = fields.Object(VDCThreebot)
    created = fields.DateTime(default=datetime.datetime.utcnow)
    updated = fields.DateTime(default=datetime.datetime.utcnow, on_update=datetime.datetime.utcnow)
    expiration = fields.DateTime(default=lambda: datetime.datetime.utcnow() + datetime.timedelta(days=30))

    @property
    def wallet(self):
        # wallet instance name is same as self.instance_name
        wallet = j.clients.stellar.find(self.instance_name)
        if not wallet:
            vdc_wallet = VDC_WALLET_FACTORY.find(self.instance_name)
            if not vdc_wallet:
                vdc_wallet = VDC_WALLET_FACTORY.new(self.instance_name)
            wallet = vdc_wallet.stellar_wallet
        return wallet

    def get_deployer(self, password, bot=None, proxy_farm_name=None, mgmt_kube_config_path=None):
        return VDCDeployer(password, self, bot, proxy_farm_name, mgmt_kube_config_path)

    def load_info(self):
        instance_vdc_workloads = self._filter_vdc_workloads(self.identity_tid, self.solution_uuid)
        proxy_workloads = []
        for workload in instance_vdc_workloads:
            self._update_instance(workload)
            if workload.info.workload_type in GATEWAY_WORKLOAD_TYPES:
                proxy_workloads.append(workload)
            if workload.info.workload_type == WorkloadType.Container and "nginx" in workload.flist:
                proxy_workloads.append(workload)
        self._build_domain_info(proxy_workloads)

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

    def _update_instance(self, workload):
        if workload.info.workload_type == WorkloadType.Kubernetes:
            node = KubernetesNode()
            node.wid = workload.id
            node.ip_address = workload.ipaddress
            if workload.master_ips:
                node.role = KubernetesRole.WORKER
            else:
                node.role = KubernetesRole.MASTER
            node.node_id = workload.info.node_id
            node.pool_id = workload.info.pool_id
            self.size = workload.size
            self.kubernetes.append(node)
        elif workload.info.workload_type == WorkloadType.Container:
            if "minio" in workload.flist:
                container = S3Container()
                container.node_id = workload.info.node_id
                container.pool_id = workload.info.pool_id
                container.wid = workload.id
                container.ip_address = workload.network_connection[0].ipaddress
                self.s3.minio = container
            elif "js-sdk" in workload.flist:
                container = VDCThreebot()
                container.node_id = workload.info.node_id
                container.pool_id = workload.info.pool_id
                container.wid = workload.id
                container.ip_address = workload.network_connection[0].ipaddress
                self.threebot = container
        elif workload.info.workload_type == WorkloadType.Zdb:
            zdb = S3ZDB()
            zdb.node_id = workload.info.node_id
            zdb.pool_id = workload.info.pool_id
            zdb.wid = workload.id
            zdb.size = workload.size
            self.s3.zdbs.append(zdb)

    def _build_domain_info(self, proxy_worklaods):
        healer_proxy_domain = ""
        healer_nginx_domain = ""
        healer_subdomain_domain = ""

        api_proxy_domain = ""
        api_nginx_domain = ""
        api_subdomain_domain = ""

        for workload in proxy_worklaods:
            description = serializers.json.loads(workload.info.description)
            if description.get("exposed_wid") != self.s3.minio.wid:
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
                        self.s3.healer_proxy.nginx.wid = workload.id
                        self.s3.healer_proxy.nginx.node_id = workload.info.node_id
                        self.s3.healer_proxy.nginx.pool_id = workload.info.pool_id
                    else:
                        api_nginx_domain = domain
                        self.s3.api_proxy.nginx.wid = workload.id
                        self.s3.api_proxy.nginx.node_id = workload.info.node_id
                        self.s3.api_proxy.nginx.pool_id = workload.info.pool_id
                else:
                    j.logger.warning(f"couldn't identity the domain of nginx container wid: {workload.id}")
            elif workload.info.workload_type == WorkloadType.Subdomain:
                domain = workload.domain
                if "healing" in domain:
                    healer_subdomain_domain = domain
                    self.s3.healer_proxy.subdomain.wid = workload.id
                    self.s3.healer_proxy.subdomain.node_id = workload.info.node_id
                    self.s3.healer_proxy.subdomain.pool_id = workload.info.pool_id
                else:
                    api_subdomain_domain = domain
                    self.s3.api_proxy.subdomain.wid = workload.id
                    self.s3.api_proxy.subdomain.node_id = workload.info.node_id
                    self.s3.api_proxy.subdomain.pool_id = workload.info.pool_id
            elif workload.info.workload_type == WorkloadType.Reverse_proxy:
                domain = workload.domain
                if "healing" in domain:
                    healer_proxy_domain = domain
                    self.s3.healer_proxy.reverse_proxy.wid = workload.id
                    self.s3.healer_proxy.reverse_proxy.node_id = workload.info.node_id
                    self.s3.healer_proxy.reverse_proxy.pool_id = workload.info.pool_id
                else:
                    api_proxy_domain = domain
                    self.s3.api_proxy.reverse_proxy.wid = workload.id
                    self.s3.api_proxy.reverse_proxy.node_id = workload.info.node_id
                    self.s3.api_proxy.reverse_proxy.pool_id = workload.info.pool_id
            else:
                j.logger.warning(f"workload {workload.id} is not a vaild workload for vdc proxy")

        if api_nginx_domain == api_proxy_domain == api_subdomain_domain:
            self.s3.subdomain = api_nginx_domain
        else:
            j.logger.error(
                f"vdc {self.solution_uuid} s3 api domains are conflicting. subdomain: {api_subdomain_domain}, nginx: {api_nginx_domain}, reverse_proxy: {api_proxy_domain}"
            )

        if healer_nginx_domain == healer_proxy_domain == healer_subdomain_domain:
            self.s3.healer_subdomain = healer_nginx_domain
        else:
            j.logger.error(
                f"vdc {self.solution_uuid} s3 healer domains are conflicting. subdomain: {healer_subdomain_domain}, nginx: {healer_nginx_domain}, reverse_proxy: {healer_proxy_domain}"
            )


VDC_INSTANCE_NAME_FORMAT = "vdc_{}_{}"


class VDCStoredFactory(StoredFactory):
    def new(self, vdc_name, owner_tname, flavor):
        owner_tname = j.data.text.removesuffix(owner_tname, ".3bot")
        instance_name = VDC_INSTANCE_NAME_FORMAT.format(vdc_name, owner_tname)
        return super().new(instance_name, vdc_name=vdc_name, owner_tname=owner_tname, flavor=flavor)

    def find(self, name=None, vdc_name=None, owner_tname=None, load_info=False):
        owner_tname = j.data.text.removesuffix(owner_tname, ".3bot") if owner_tname else None
        instance_name = name or VDC_INSTANCE_NAME_FORMAT.format(vdc_name, owner_tname)
        instance = super().find(instance_name)
        if not instance:
            return
        if owner_tname and instance.owner_tname != owner_tname:
            return
        if load_info:
            instance.load_info()
        return instance

    def list(self, owner_tname, load_info=False):
        owner_tname = j.data.text.removesuffix(owner_tname, ".3bot")
        _, _, instances = self.find_many(owner_tname=owner_tname)
        if not load_info:
            return instances

        result = []
        for instance in instances:
            instance.load_info()
            result.append(instance)
        return result


VDCFACTORY = VDCStoredFactory(UserVDC)
VDCFACTORY.always_relaod = True
