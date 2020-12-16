import datetime
from decimal import Decimal
import uuid

from jumpscale.clients.explorer.models import NextAction, WorkloadType
from jumpscale.core.base import Base, fields
from jumpscale.loader import j
from jumpscale.sals.zos import get as get_zos

from .deployer import VDCDeployer
from .models import *
from .size import VDC_SIZE
from .wallet import VDC_WALLET_FACTORY
import netaddr

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
    flavor = fields.Enum(VDC_SIZE.VDCFlavor)
    s3 = fields.Object(S3)
    kubernetes = fields.List(fields.Object(KubernetesNode))
    threebot = fields.Object(VDCThreebot)
    created = fields.DateTime(default=datetime.datetime.utcnow)
    last_updated = fields.DateTime(default=datetime.datetime.utcnow)
    expiration = fields.DateTime(default=lambda: datetime.datetime.utcnow() + datetime.timedelta(days=30))
    is_blocked = fields.Boolean(default=False)
    explorer_url = fields.String(default=lambda: j.core.identity.me.explorer_url)

    def is_empty(self):
        if any([self.kubernetes, self.threebot.wid, self.threebot.domain, self.s3.minio.wid, self.s3.zdbs]):
            return False
        return True

    @property
    def prepaid_wallet(self):
        wallet_name = f"{self.instance_name}_prepaid_wallet"
        wallet = j.clients.stellar.find(wallet_name)
        if not wallet:
            vdc_wallet = VDC_WALLET_FACTORY.find(wallet_name)
            if not vdc_wallet:
                vdc_wallet = VDC_WALLET_FACTORY.new(wallet_name)
                vdc_wallet.save()
            wallet = vdc_wallet.stellar_wallet
        return wallet

    @property
    def provision_wallet(self):
        wallet_name = f"{self.instance_name}_provision_wallet"
        wallet = j.clients.stellar.find(wallet_name)
        if not wallet:
            vdc_wallet = VDC_WALLET_FACTORY.find(wallet_name)
            if not vdc_wallet:
                vdc_wallet = VDC_WALLET_FACTORY.new(wallet_name)
                vdc_wallet.save()
            wallet = vdc_wallet.stellar_wallet
        return wallet

    def get_deployer(self, password=None, identity=None, bot=None, proxy_farm_name=None):
        if not password:
            identity = identity or j.core.identity.me
        return VDCDeployer(
            vdc_instance=self, password=password, bot=bot, proxy_farm_name=proxy_farm_name, identity=identity
        )

    def load_info(self):
        self.kubernetes = []
        self.s3 = S3()
        self.threebot = VDCThreebot()
        instance_vdc_workloads = self._filter_vdc_workloads()
        subdomains = []
        proxies = []
        for workload in instance_vdc_workloads:
            self._update_instance(workload)
            if workload.info.workload_type == WorkloadType.Subdomain:
                subdomains.append(workload)
            if workload.info.workload_type == WorkloadType.Reverse_proxy:
                proxies.append(workload)
        self._get_s3_subdomains(subdomains)
        self._get_threebot_subdomain(proxies)

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
            if workload.public_ip:
                zos = get_zos()
                public_ip_workload = zos.workloads.get(workload.public_ip)
                address = str(netaddr.IPNetwork(public_ip_workload.ipaddress).ip)
                node.public_ip = address

            node.size = workload.size
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

    def _get_s3_subdomains(self, subdomain_workloads):
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
                self.s3.domain_wid = workload.id

    def _get_threebot_subdomain(self, proxy_workloads):
        # threebot is exposed over gateway
        threebot_wid = self.threebot.wid
        if not threebot_wid:
            return
        for workload in proxy_workloads:
            if not workload.info.description:
                continue
            try:
                desc = j.data.serializers.json.loads(workload.info.description)
            except Exception as e:
                j.logger.warning(f"failed to load workload {workload.id} description due to error {e}")
                continue
            exposed_wid = desc.get("exposed_wid")
            if exposed_wid == threebot_wid:
                self.threebot.domain = workload.domain

    def grace_period_action(self):
        self.load_info()
        j.logger.info(f"VDC: {self.solution_uuid}, GRACE_PERIOD_ACTION: initialization")
        for k8s in self.kubernetes:
            ip_address = k8s.public_ip
            if ip_address == "::/128":
                continue
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
            ip_address = k8s.public_ip
            if ip_address == "::/128":
                continue
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

    def show_vdc_payment(self, bot, expiry=5, wallet_name=None):
        # amount = VDC_SIZE.get_vdc_tft_price(self.flavor)
        amount = VDC_SIZE.PRICES["plans"][self.flavor]
        payment_id, _ = j.sals.billing.submit_payment(
            amount=amount,
            wallet_name=wallet_name or self.prepaid_wallet.instance_name,
            refund_extra=False,
            expiry=expiry,
        )
        return j.sals.billing.wait_payment(payment_id, bot=bot), amount, payment_id

    def show_external_node_payment(self, bot, size, no_nodes=1, expiry=5, wallet_name=None, public_ip=False):
        amount = VDC_SIZE.PRICES["nodes"][size] * no_nodes
        if public_ip:
            amount += VDC_SIZE.PRICES["services"][VDC_SIZE.Services.IP]
        payment_id, _ = j.sals.billing.submit_payment(
            amount=amount,
            wallet_name=wallet_name or self.prepaid_wallet.instance_name,
            refund_extra=False,
            expiry=expiry,
        )
        return j.sals.billing.wait_payment(payment_id, bot=bot), amount, payment_id

    def transfer_to_provisioning_wallet(self, amount, wallet_name=None):
        if wallet_name:
            wallet = j.clients.stellar.get(wallet_name)
        else:
            wallet = self.prepaid_wallet
        a = wallet.get_asset()
        return self.pay_amount(self.provision_wallet.address, amount, wallet)

    def pay_initialization_fee(self, transaction_hashes, initial_wallet_name, wallet_name=None):
        initial_wallet = j.clients.stellar.get(initial_wallet_name)
        if wallet_name:
            wallet = j.clients.stellar.get(wallet_name)
        else:
            wallet = self.provision_wallet
        # get total amount
        amount = 0
        for t_hash in transaction_hashes:
            effects = initial_wallet.get_transaction_effects(t_hash)
            for effect in effects:
                amount += effect.amount
        amount = round(abs(amount), 6)
        if not amount:
            return
        return self.pay_amount(initial_wallet.address, amount, wallet)

    def pay_amount(self, address, amount, wallet):
        j.logger.info(f"transfering amount: {amount} from wallet: {wallet.instance_name} to address: {address}")
        deadline = j.data.time.now().timestamp + 5 * 60
        a = wallet.get_asset()
        has_funds = None
        while j.data.time.now().timestamp < deadline:
            if not has_funds:
                try:
                    balances = wallet.get_balance().balances
                    for b in balances:
                        if b.asset_code != "TFT":
                            continue
                        if amount <= float(b.balance) + 0.1:
                            has_funds = True
                            break
                        else:
                            has_funds = False
                            raise j.exceptions.Validation(
                                f"not enough funds in wallet {wallet.instance_name} to pay amount: {amount}. current balance: {b.balance}"
                            )
                except Exception as e:
                    if has_funds is False:
                        j.logger.error(f"not enough funds in wallet {wallet.instance_name} to pay amount: {amount}")
                        raise e
                    j.logger.warning(f"failed to get wallet {wallet.instance_name} balance due to error: {str(e)}")
                    continue

            try:
                return wallet.transfer(address, amount=amount, asset=f"{a.code}:{a.issuer}")
            except Exception as e:
                j.logger.warning(f"failed to submit payment to stellar due to error {str(e)}")
        j.logger.critical(
            f"failed to submit payment to stellar in time to: {address} amount: {amount} for wallet: {wallet.instance_name}"
        )
        raise j.exceptions.Runtime(
            f"failed to submit payment to stellar in time to: {address} amount: {amount} for wallet: {wallet.instance_name}"
        )
