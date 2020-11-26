import datetime
import uuid

from jumpscale.clients.explorer.models import NextAction, WorkloadType
from jumpscale.core.base import Base, fields
from jumpscale.loader import j
from jumpscale.sals.zos import get as get_zos

from .deployer import VDCDeployer
from .models import *
from .size import VDCFlavor
from .wallet import VDC_WALLET_FACTORY

VDC_WORKLOAD_TYPES = [
    WorkloadType.Container,
    WorkloadType.Zdb,
    WorkloadType.Kubernetes,
    WorkloadType.Subdomain,
    WorkloadType.Reverse_proxy,
]


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
    last_updated = fields.DateTime(default=datetime.datetime.utcnow)
    expiration = fields.DateTime(default=lambda: datetime.datetime.utcnow() + datetime.timedelta(days=30))
    is_blocked = fields.Boolean(default=False)

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
        self.kubernetes = []
        self.s3 = S3()
        self.threebot = VDCThreebot()
        instance_vdc_workloads = self._filter_vdc_workloads()
        subdomains = []
        for workload in instance_vdc_workloads:
            self._update_instance(workload)
            if workload.info.workload_type == WorkloadType.Subdomain:
                subdomains.append(workload)
            self._get_s3_subdomain(subdomains)

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
                description = j.data.serializers.json.loads(workload.info.description)
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
                j.logger.warning(f"failed to load workload {workload.id} description due to error {e}")
                continue
            exposed_wid = desc.get("exposed_wid")
            if exposed_wid == minio_wid:
                self.s3.domain = workload.domain
                return

    def grace_period_action(self):
        self.load_info()
        j.logger.info(f"VDC: {self.solution_uuid}, GRACE_PERIOD_ACTION: initialization")
        for k8s in self.kubernetes:
            # FIXME: replace master ip with the correct public ip when merged
            ip_address = k8s.ip_address
            ssh_key = j.clients.sshkey.get(self.vdc_name)
            vdc_key_path = j.core.config.get("VDC_KEY_PATH", "~/.ssh/id_rsa")
            ssh_key.private_key_path = j.sals.fs.expanduser(vdc_key_path)
            ssh_key.load_from_file_system()
            try:
                ssh_client = j.clients.sshclient.get(
                    self.instance_name, user="rancher", host=str(ip_address), sshkey=self.vdc_name
                )
                rc, out, err = ssh_client.sshclient.run("sudo ip link set cni0 down", warn=True)
                if rc:
                    j.logger.critical(
                        f"VDC: {self.solution_uuid}, GRACE_PERIOD_ACTION: failed to shutdown cni0 wid: {k8s.wid}, rc: {rc}, out: {out}, err: {err}"
                    )
                if k8s.role == KubernetesRole.MASTER:
                    rc, out, err = ssh_client.sshclient.run(
                        "sudo iptables -A INPUT -p tcp --destination-port 6443 -j DROP", warn=True
                    )
                    if rc:
                        j.logger.critical(
                            f"VDC: {self.solution_uuid}, GRACE_PERIOD_ACTION: failed to block kubernetes API wid: {k8s.wid}, rc: {rc}, out: {out}, err: {err}"
                        )

                j.clients.sshclient.delete(self.instance_name)
            except Exception as e:
                j.logger.critical(
                    f"VDC: {self.solution_uuid}, GRACE_PERIOD_ACTION: failed to connect to kubernetes controller due to error {str(e)}"
                )
                raise e
        self.is_blocked = True
        self.save()
        j.logger.info(f"VDC: {self.solution_uuid}, GRACE_PERIOD_ACTION: applied successfully")

    def undo_grace_period_action(self):
        self.load_info()
        j.logger.info(f"VDC: {self.solution_uuid}, REVERT_GRACE_PERIOD_ACTION: intializing")
        self.is_blocked = False
        for k8s in self.kubernetes:
            # FIXME: replace master ip with the correct public ip when merged
            ip_address = k8s.ip_address
            ssh_key = j.clients.sshkey.get(self.vdc_name)
            vdc_key_path = j.core.config.get("VDC_KEY_PATH", "~/.ssh/id_rsa")
            ssh_key.private_key_path = j.sals.fs.expanduser(vdc_key_path)
            ssh_key.load_from_file_system()
            try:
                ssh_client = j.clients.sshclient.get(
                    self.instance_name, user="rancher", host=str(ip_address), sshkey=self.vdc_name
                )
                rc, out, err = ssh_client.sshclient.run("sudo ip link set cni0 up", warn=True)
                if rc:
                    j.logger.critical(
                        f"VDC: {self.solution_uuid}, GRACE_PERIOD_ACTION: failed to bring up cni0 wid: {k8s.wid}, rc: {rc}, out: {out}, err: {err}"
                    )
                if k8s.role == KubernetesRole.MASTER:
                    rc, out, err = ssh_client.sshclient.run(
                        "sudo iptables -D INPUT -p tcp --destination-port 6443 -j DROP", warn=True
                    )
                    if rc:
                        j.logger.critical(
                            f"VDC: {self.solution_uuid}, GRACE_PERIOD_ACTION: failed to unblock kubernetes API wid: {k8s.wid}, rc: {rc}, out: {out}, err: {err}"
                        )

                j.clients.sshclient.delete(self.instance_name)
            except Exception as e:
                j.logger.critical(
                    f"VDC: {self.solution_uuid}, GRACE_PERIOD_ACTION: failed to connect to kubernetes controller due to error {str(e)}"
                )
                self.is_blocked = True
                continue

        self.save()
        j.logger.info(f"VDC: {self.solution_uuid}, REVERT_GRACE_PERIOD_ACTION: reverted successfully")
