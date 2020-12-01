import datetime
import gevent
import uuid

from jumpscale.clients.explorer.models import NextAction, WorkloadType
from jumpscale.core.base import Base, fields
from jumpscale.loader import j
from jumpscale.sals.zos import get as get_zos

from .deployer import VDCDeployer
from .models import *
from .size import VDCFlavor, get_kubernetes_tft_price, get_vdc_tft_price
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

    def get_deployer(self, password, bot=None, proxy_farm_name=None):
        return VDCDeployer(password, self, bot, proxy_farm_name)

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
            if workload.public_ip:
                zos = get_zos()
                public_ip_workload = zos.workloads.get(workload.public_ip)
                address = str(netaddr.IPNetwork(public_ip_workload.ipaddress).ip)
                node.public_ip = address

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

    def _show_payment(self, bot, amount, wallet_name=None):
        if wallet_name:
            wallet = j.clients.stellar.get(wallet_name)
            wallet_address = wallet.address
        else:
            wallet_address = self.wallet.address
        # TODO: properly generate and save memo text
        memo_text = j.data.idgenerator.chars(28)
        qr_code = f"TFT:{wallet_address}?amount={amount}&message={memo_text}&sender=me"
        qr_encoded = j.tools.qrcode.base64_get(qr_code, scale=2)
        msg_text = f"""Please scan the QR Code below for the payment details if you missed it from the previous screen
        <div class="text-center">
            <img style="border:1px dashed #85929E" src="data:image/png;base64,{qr_encoded}"/>
        </div>
        <h4> Destination Wallet Address: </h4>  {wallet_address} \n
        <h4> Currency: </h4>  TFT \n
        <h4> Memo Text: </h4>  {memo_text} \n
        <h4> Total Amount: </h4> {amount} TFT \n

        <h5>Inserting the memo-text is an important way to identify a transaction recipient beyond a wallet address. Failure to do so will result in a failed payment. Please also keep in mind that an additional Transaction fee of 0.1 TFT will automatically occurs per transaction.</h5>
        """
        bot.md_show_update(msg_text, html=True)
        return memo_text

    def _wait_payment(self, bot, amount, memo_text, expiry=5, wallet_name=None):
        if wallet_name:
            wallet = j.clients.stellar.get(wallet_name)
        else:
            wallet = self.wallet

        deadline = j.data.time.now().timestamp + expiry * 60
        while j.data.time.now().timestamp < deadline:
            # get transactions and identify memo text and amount
            for transaction in wallet.list_transactions():
                transaction_hash = transaction.hash
                trans_memo_text = transaction.memo_text
                if memo_text != trans_memo_text:
                    continue
                try:
                    effects = wallet.get_transaction_effects(transaction_hash)
                except Exception as e:
                    j.logger.warning(
                        f"failed to get transaction effects of hash {transaction_hash} due to error {str(e)}"
                    )
                    continue
                trans_amount = 0
                for effect in effects:
                    trans_amount += effect.amount
                if trans_amount >= amount:
                    diff = trans_amount - amount
                    if diff > 0:
                        self.refund_payment(transaction_hash, wallet_name, diff)
                    return transaction_hash
                else:
                    self.refund_payment(transaction_hash, wallet_name)

    def show_vdc_payment(self, bot, expiry=5, wallet_name=None):
        amount = get_vdc_tft_price(self.flavor)
        memo_text = self._show_payment(bot, amount, wallet_name)
        return self._wait_payment(bot, amount, memo_text, expiry, wallet_name)

    def show_external_node_payment(self, bot, size, no_nodes=1, expiry=5, wallet_name=None):
        amount = get_kubernetes_tft_price(size) * no_nodes
        memo_text = self._show_payment(bot, amount, wallet_name)
        return self._wait_payment(bot, amount, memo_text, expiry, wallet_name)

    def refund_payment(self, transaction_hash, wallet_name=None, amount=None):
        j.logger.critical(
            f"refunding amount: {amount} transaction hash: {transaction_hash} from wallet: {wallet_name} for vdc {self.vdc_name} owner {self.owner_tname}"
        )
        if wallet_name:
            wallet = j.clients.stellar.get(wallet_name)
        else:
            wallet = self.wallet
        effects = wallet.get_transaction_effects(transaction_hash)
        trans_amount = amount or 0
        if not amount:
            for effect in effects:
                trans_amount += effect.amount
        trans_amount -= 0.1
        if trans_amount > 0:
            a = wallet.get_asset()
            sender_address = wallet.get_sender_wallet_address(transaction_hash)
            try:
                wallet.transfer(sender_address, amount=trans_amount, asset=f"{a.code}:{a.issuer}")
            except Exception as e:
                j.logger.critical(
                    f"failed to refund transaction hash: {transaction_hash} from wallet: {wallet_name} for vdc {self.vdc_name} owner {self.owner_tname} due to error {str(e)}"
                )
                return False
        return True
