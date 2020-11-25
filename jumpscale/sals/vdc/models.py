import datetime
import uuid
from enum import Enum

from jumpscale.clients.explorer.models import NextAction, WorkloadType
from jumpscale.clients.stellar.stellar import Network as StellarNetwork
from jumpscale.core.base import Base, StoredFactory, fields
from jumpscale.data import serializers
from jumpscale.loader import j
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

    def _init_wallet(self, secret=None):
        if "testnet" in j.core.identity.me.explorer_url or "devnet" in j.core.identity.me.explorer_url:
            self.wallet_network = StellarNetwork.TEST
        else:
            self.wallet_network = StellarNetwork.STD

        wallet = j.clients.stellar.new(self.instance_name, secret=secret, network=self.wallet_network)
        if not secret:
            wallet.activate_through_friendbot()
            wallet.add_known_trustline("TFT")
        wallet.save()
        self.wallet_secret = wallet.secret

    @property
    def stellar_wallet(self):
        if not j.clients.stellar.find(self.instance_name) and self.wallet_secret:
            self._init_wallet(self.wallet_secret)
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


class S3(Base):
    minio = fields.Object(S3Container)
    zdbs = fields.List(fields.Object(S3ZDB))
    domain = fields.String()


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
                vdc_wallet.save()
            wallet = vdc_wallet.stellar_wallet
        return wallet

    def get_deployer(self, password, bot=None, proxy_farm_name=None, mgmt_kube_config_path=None):
        return VDCDeployer(password, self, bot, proxy_farm_name, mgmt_kube_config_path)

    def load_info(self):
        instance_vdc_workloads = self._filter_vdc_workloads()
        subdomains = []
        for workload in instance_vdc_workloads:
            self._update_instance(workload)
            if workload.info.workload_type == WorkloadType.Subdomain:
                subdomains.append(workload)

    def _filter_vdc_workloads(self):
        zos = get_zos()
        user_workloads = zos.workloads.list(self.identity_tid, next_action=NextAction.DEPLOY)
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
            if description.get("vdc_uuid") != self.solution_uuid:
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

    def _get_s3_subdomain(self, subdomain_workloads):
        minio_wid = self.s3.minio.wid
        if not minio_wid:
            return
        for workload in subdomain_workloads:
            if not workload.info.description:
                continue
            try:
                desc = j.data.serializers.json.loads(workload.info.description)
            except Exception as e:
                j.logger.warning(f"failed to load workload {workload.id} description")
                continue
            exposed_wid = desc.get("exposed_wid")
            if exposed_wid == minio_wid:
                self.s3.domain = workload.domain
                return


VDC_INSTANCE_NAME_FORMAT = "vdc_{}_{}"


class VDCStoredFactory(StoredFactory):
    def new(self, vdc_name, owner_tname, flavor):
        if isinstance(flavor, str):
            flavor = VDCFlavor(flavor.lower())
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
