from collections import defaultdict
import datetime
from enum import Enum
import random
import uuid

from gevent.lock import BoundedSemaphore
from jumpscale.core.base import Base, fields
from jumpscale.loader import j

from jumpscale.clients.explorer.models import (
    DiskType,
    K8s,
    NextAction,
    PublicIP,
    WorkloadType,
    ZdbNamespace,
)
from jumpscale.clients.stellar import TRANSACTION_FEES
from jumpscale.clients.stellar import TRANSACTION_FEES
from jumpscale.sals.vdc.quantum_storage import QuantumStorage
from jumpscale.sals.vdc.scheduler import CapacityChecker
from jumpscale.sals.zos import get as get_zos

from .deployer import SSH_KEY_PREFIX, VDCDeployer
from .kubernetes_auto_extend import KubernetesMonitor
from .models import *
from .size import FARM_DISCOUNT, PROXY_FARMS, VDC_SIZE, ZDB_STARTING_SIZE
from .snapshot import SnapshotManager
from .wallet import VDC_WALLET_FACTORY
from .zdb_auto_topup import ZDBMonitor

VDC_WORKLOAD_TYPES = [
    WorkloadType.Container,
    WorkloadType.Zdb,
    WorkloadType.Kubernetes,
    WorkloadType.Subdomain,
    WorkloadType.Reverse_proxy,
]


class VDCSTATE(Enum):
    CREATING = "CREATING"
    DEPLOYED = "DEPLOYED"
    ERROR = "ERROR"
    EMPTY = "EMPTY"
    VERIFIED = "VERIFIED"


class UserVDC(Base):
    vdc_name = fields.String()
    owner_tname = fields.String()
    solution_uuid = fields.String(default=lambda: uuid.uuid4().hex)
    identity_tid = fields.Integer()
    s3 = fields.Object(S3)
    kubernetes = fields.List(fields.Object(KubernetesNode))
    etcd = fields.List(fields.Object(ETCDNode))
    threebot = fields.Object(VDCThreebot)
    created = fields.DateTime(default=datetime.datetime.utcnow)
    expiration = fields.Float(default=lambda: j.data.time.utcnow().timestamp + 30 * 24 * 60 * 60)
    last_updated = fields.DateTime(default=datetime.datetime.utcnow)
    is_blocked = fields.Boolean(default=False)  # grace period action is applied
    explorer_url = fields.String(default=lambda: j.core.identity.me.explorer_url)
    _flavor = fields.String()
    state = fields.Enum(VDCSTATE)
    __lock = BoundedSemaphore(1)
    transaction_hashes = []

    @property
    def flavor(self):
        d = self.to_dict()
        oldflavor = d.get("flavor", "silver")
        if not self._flavor:
            flavors = {"silver": "silver", "gold": "gold", "platinum": "platinum", "diamond": "diamond"}
            self._flavor = d.get(flavors[oldflavor])
            self.save()
            # TODO: should we do a save here?
            return VDC_SIZE.VDCFlavor(self._flavor)
        else:
            return VDC_SIZE.VDCFlavor(self._flavor)

    def to_dict(self):
        d = super().to_dict()
        d["flavor"] = self._flavor
        for node in d["kubernetes"]:
            node["size"] = node["_size"]
        return d

    def is_empty(self, load_info=True):
        if load_info:
            self.load_info()
        if any([self.kubernetes, self.threebot.wid, self.threebot.domain, self.s3.minio.wid, self.s3.zdbs]):
            return False
        return True

    def has_minimal_components(self):
        if all([self.kubernetes, self.threebot.wid, self.threebot.domain]):
            return True
        return False

    @property
    def expiration_date(self):
        expiration = self.calculate_expiration_value()
        return j.data.time.get(expiration).datetime

    @property
    def prepaid_wallet(self):
        wallet_name = f"prepaid_wallet_{self.solution_uuid}"
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
        wallet_name = f"provision_wallet_{self.solution_uuid}"
        wallet = j.clients.stellar.find(wallet_name)
        if not wallet:
            vdc_wallet = VDC_WALLET_FACTORY.find(wallet_name)
            if not vdc_wallet:
                vdc_wallet = VDC_WALLET_FACTORY.new(wallet_name)
                vdc_wallet.save()
            wallet = vdc_wallet.stellar_wallet
        return wallet

    @property
    def vdc_workloads(self):
        workloads = []
        workloads += self.kubernetes
        workloads += self.s3.zdbs
        if self.threebot.wid:
            workloads.append(self.threebot)
        if self.s3.minio.wid:
            workloads.append(self.s3.minio)
        return workloads

    @property
    def active_pools(self):
        my_pool_ids = [w.pool_id for w in self.vdc_workloads]
        explorer = j.core.identity.me.explorer
        active_pools = [p for p in explorer.pools.list(customer_tid=self.identity_tid) if p.pool_id in my_pool_ids]
        return active_pools

    def get_deployer(
        self,
        password=None,
        identity=None,
        bot=None,
        proxy_farm_name=None,
        deployment_logs=False,
        ssh_key_path=None,
        restore=False,
        network_farm=None,
        compute_farm=None,
    ):
        proxy_farm_name = proxy_farm_name or random.choice(PROXY_FARMS.get())
        if not password and not identity:
            identity = self._get_identity()

        return VDCDeployer(
            vdc_instance=self,
            password=password,
            bot=bot,
            proxy_farm_name=proxy_farm_name,
            identity=identity,
            deployment_logs=deployment_logs,
            ssh_key_path=ssh_key_path,
            restore=restore,
            network_farm=network_farm,
            compute_farm=compute_farm,
        )

    def get_password(self):
        identity = self._get_identity(default=False)
        if not identity:
            j.logger.error("Couldn't find identity")
            return
        password_hash = j.data.encryption.mnemonic_to_key(identity.words)
        return password_hash.decode()

    def validate_password(self, password):
        password = j.data.hash.md5(password)
        vdc_password = self.get_password()
        if not vdc_password:
            # identity was not generated for this vdc instance
            return True

        if password == vdc_password:
            return True
        return False

    def _get_identity(self, default=True):
        instance_name = f"vdc_ident_{self.solution_uuid}"
        identity = None
        if j.core.identity.find(instance_name):
            identity = j.core.identity.find(instance_name)
        elif default:
            identity = j.core.identity.me
        return identity

    def get_zdb_monitor(self):
        return ZDBMonitor(self)

    def get_kubernetes_monitor(self):
        return KubernetesMonitor(self)

    def get_snapshot_manager(self, snapshots_dir=None):
        return SnapshotManager(self, snapshots_dir)

    def get_quantumstorage_manager(self, ip_version=4):
        return QuantumStorage(self, ip_version)

    def load_info(self, load_proxy=False):
        kubernetes, s3, etcd, threebot = self.get_vdc_workloads(load_proxy=load_proxy)

        self.__lock.acquire()
        try:
            self.kubernetes = kubernetes
            self.etcd = etcd
            self.s3 = s3
            self.threebot = threebot
        finally:
            self.__lock.release()

    def _build_zdb_proxies(self, s3):
        proxies = self._list_socat_proxies()
        for zdb in s3.zdbs:
            zdb_proxies = proxies[zdb.ip_address]
            if not zdb_proxies:
                continue
            proxy = zdb_proxies[0]
            zdb.proxy_address = f"{proxy['ip_address']}:{proxy['listen_port']}"

    def get_public_ip(self):
        if not self.kubernetes:
            self.load_info()
        public_ip = None
        for node in self.kubernetes:
            if node.public_ip != "::/128":
                public_ip = node.public_ip
                break
        return public_ip

    def _list_socat_proxies(self, public_ip=None):
        public_ip = public_ip or self.get_public_ip()
        if not public_ip:
            raise j.exceptions.Runtime(f"Couldn't get a public ip for vdc: {self.vdc_name}")
        ssh_client = self.get_ssh_client("socat_list", public_ip, "rancher")
        result = defaultdict(list)
        rc, out, _ = ssh_client.sshclient.run(f"sudo ps -ef | grep -v grep | grep socat", warn=True)
        if rc != 0:
            return result

        for line in out.splitlines():
            # root      6659     1  0 Feb19 ?        00:00:00 /var/lib/rancher/k3s/data/current/bin/socat tcp-listen:9900,reuseaddr,fork tcp:[2a02:1802:5e:0:c46:cff:fe32:39ae]:9900
            splits = line.split("tcp-listen:")
            if len(splits) != 2:
                continue
            splits = splits[1].split(",")
            if len(splits) < 2:
                continue
            listen_port = splits[0]
            splits = line.split("tcp:")
            if len(splits) != 2:
                continue
            proxy_address = splits[1]
            splits = proxy_address.split(":")
            if len(splits) < 2:
                continue

            port = splits[-1]
            ip_address = ":".join(splits[:-1])
            if ip_address[0] == "[" and ip_address[-1] == "]":
                ip_address = ip_address[1:-1]
            result[ip_address].append({"dst_port": port, "listen_port": listen_port, "ip_address": public_ip})
        return result

    def _filter_vdc_workloads(self):
        zos = get_zos()
        user_workloads = zos.workloads.list_workloads(self.identity_tid, next_action=NextAction.DEPLOY)
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

    def get_vdc_workloads(self, load_proxy=False):
        kubernetes = []
        s3 = S3()
        etcd = []
        threebot = VDCThreebot()

        proxies = []
        for workload in self._filter_vdc_workloads():
            if workload.info.workload_type == WorkloadType.Kubernetes:
                kubernetes.append(KubernetesNode.from_workload(workload))
            elif workload.info.workload_type == WorkloadType.Container:
                if "minio" in workload.flist:
                    container = S3Container.from_workload(workload)
                    s3.minio = container
                elif "js-sdk" in workload.flist:
                    container = VDCThreebot.from_workload(workload)
                    threebot = container
                elif "etcd" in workload.flist:
                    node = ETCDNode.from_workload(workload)
                    etcd.append(node)
            elif workload.info.workload_type == WorkloadType.Zdb:
                zdb = S3ZDB.from_workload(workload)
                s3.zdbs.append(zdb)
            elif workload.info.workload_type == WorkloadType.Subdomain:
                s3_domain = self._check_s3_subdomains(workload)
                if s3_domain:
                    s3.domain = workload.domain
                    s3.domain_wid = workload.id
            elif workload.info.workload_type == WorkloadType.Reverse_proxy:
                proxies.append(workload)

        threebot.domain = self._get_threebot_subdomain(proxies, threebot)
        if load_proxy:
            self._build_zdb_proxies(s3)

        return kubernetes, s3, etcd, threebot

    def _check_s3_subdomains(self, workload):
        minio_wid = self.s3.minio.wid
        if not minio_wid:
            return

        if not workload.info.description:
            return
        try:
            desc = j.data.serializers.json.loads(workload.info.description)
        except Exception as e:
            j.logger.warning(f"Failed to load workload {workload.id} description due to error {e}")
            return
        exposed_wid = desc.get("exposed_wid")
        if exposed_wid == minio_wid:
            return True

    def _get_threebot_subdomain(self, proxy_workloads, threebot):
        threebot_wid = threebot.wid
        if not threebot_wid:
            return
        non_matching_domains = []
        for workload in proxy_workloads:
            if not workload.info.description:
                continue
            try:
                desc = j.data.serializers.json.loads(workload.info.description)
            except Exception as e:
                j.logger.warning(f"Failed to load workload {workload.id} description due to error {e}")
                continue
            exposed_wid = desc.get("exposed_wid")
            if exposed_wid == threebot_wid:
                return workload.domain
            else:
                non_matching_domains.append(workload.domain)
        if not threebot.domain and non_matching_domains:
            return non_matching_domains[-1]

    def apply_grace_period_action(self):
        self.load_info()
        j.logger.info(f"VDC: {self.solution_uuid}, GRACE_PERIOD_ACTION: initialization")
        for k8s in self.kubernetes:
            ip_address = k8s.public_ip
            if ip_address == "::/128":
                continue
            try:
                ssh_client = self.get_ssh_client(self.instance_name, user="rancher", ip_address=str(ip_address))
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

    def revert_grace_period_action(self):
        self.load_info()
        j.logger.info(f"VDC: {self.solution_uuid}, REVERT_GRACE_PERIOD_ACTION: intializing")
        self.is_blocked = False
        for k8s in self.kubernetes:
            ip_address = k8s.public_ip
            if ip_address == "::/128":
                continue
            try:
                ssh_client = self.get_ssh_client(self.instance_name, user="rancher", ip_address=str(ip_address))
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
        discount = FARM_DISCOUNT.get()
        amount = VDC_SIZE.PRICES["plans"][self.flavor] * (1 - discount)

        payment_id, _ = j.sals.billing.submit_payment(
            amount=amount,
            wallet_name=wallet_name or self.prepaid_wallet.instance_name,
            refund_extra=False,
            expiry=expiry,
            description=j.data.serializers.json.dumps(
                {"type": "VDC_INIT", "owner": self.owner_tname, "solution_uuid": self.solution_uuid}
            ),
        )

        if amount > 0:
            notes = []
            if discount:
                notes = ["For testing purposes, we applied a discount of {:.0f}%".format(discount * 100)]
            return j.sals.billing.wait_payment(payment_id, bot=bot, notes=notes), amount, payment_id
        else:
            return True, amount, payment_id

    def show_external_node_payment(self, bot, farm_name, size, no_nodes=1, expiry=5, wallet_name=None, public_ip=False):
        discount = FARM_DISCOUNT.get()
        duration = self.calculate_expiration_value() - j.data.time.utcnow().timestamp
        month = 60 * 60 * 24 * 30
        if duration > month:
            duration = month

        zos = j.sals.zos.get()
        farm_id = zos._explorer.farms.get(farm_name=farm_name).id
        k8s = K8s()
        if isinstance(size, str):
            size = VDC_SIZE.K8SNodeFlavor[size.upper()].value
        k8s.size = size
        amount = j.tools.zos.consumption.cost(k8s, duration, farm_id) + TRANSACTION_FEES

        if public_ip:
            pub_ip = PublicIP()
            amount += j.tools.zos.consumption.cost(pub_ip, duration, farm_id)
        amount *= no_nodes

        prepaid_balance = self._get_wallet_balance(self.prepaid_wallet)
        if prepaid_balance >= amount:
            if bot:
                result = bot.single_choice(
                    f"Do you want to use your existing balance to pay {round(amount,4)} TFT? (This will impact the overall expiration of your plan)",
                    ["Yes", "No"],
                    required=True,
                )
                if result == "Yes":
                    amount = 0
            else:
                amount = 0
        elif not bot:
            # Not enough funds in prepaid wallet and no bot passed to use to view QRcode
            return False, amount, None

        payment_id, _ = j.sals.billing.submit_payment(
            amount=amount,
            wallet_name=wallet_name or self.prepaid_wallet.instance_name,
            refund_extra=False,
            expiry=expiry,
            description=j.data.serializers.json.dumps(
                {"type": "VDC_K8S_EXTEND", "owner": self.owner_tname, "solution_uuid": self.solution_uuid}
            ),
        )
        if amount > 0:
            notes = []
            if discount:
                notes = ["For testing purposes, we applied a discount of {:.0f}%".format(discount * 100)]
            return j.sals.billing.wait_payment(payment_id, bot=bot, notes=notes), amount, payment_id
        else:
            return True, amount, payment_id

    def show_external_zdb_payment(
        self, bot, farm_name, size=ZDB_STARTING_SIZE, no_nodes=1, expiry=5, wallet_name=None, disk_type=DiskType.HDD
    ):
        discount = FARM_DISCOUNT.get()
        duration = self.calculate_expiration_value() - j.data.time.utcnow().timestamp
        month = 60 * 60 * 24 * 30
        if duration > month:
            duration = month

        zos = j.sals.zos.get()
        farm_id = zos._explorer.farms.get(farm_name=farm_name).id
        zdb = ZdbNamespace()
        zdb.size = size
        zdb.disk_type = disk_type
        amount = j.tools.zos.consumption.cost(zdb, duration, farm_id) + TRANSACTION_FEES
        amount *= no_nodes

        prepaid_balance = self._get_wallet_balance(self.prepaid_wallet)
        if prepaid_balance >= amount:
            if bot:
                result = bot.single_choice(
                    f"Do you want to use your existing balance to pay {round(amount,4)} TFT? (This will impact the overall expiration of your plan)",
                    ["Yes", "No"],
                    required=True,
                )
                if result == "Yes":
                    amount = 0
            else:
                amount = 0
        elif not bot:
            # Not enough funds in prepaid wallet and no bot passed to use to view QRcode
            return False, amount, None

        payment_id, _ = j.sals.billing.submit_payment(
            amount=amount,
            wallet_name=wallet_name or self.prepaid_wallet.instance_name,
            refund_extra=False,
            expiry=expiry,
            description=j.data.serializers.json.dumps(
                {"type": "VDC_ZDB_EXTEND", "owner": self.owner_tname, "solution_uuid": self.solution_uuid,}
            ),
        )
        if amount > 0:
            notes = []
            if discount:
                notes = ["For testing purposes, we applied a discount of {:.0f}%".format(discount * 100)]
            return j.sals.billing.wait_payment(payment_id, bot=bot, notes=notes), amount, payment_id
        else:
            return True, amount, payment_id

    def transfer_to_provisioning_wallet(self, amount, wallet_name=None):
        if not amount:
            return True
        if wallet_name:
            wallet = j.clients.stellar.get(wallet_name)
        else:
            wallet = self.prepaid_wallet
        return self.pay_amount(self.provision_wallet.address, amount, wallet)

    def pay_initialization_fee(self, transaction_hashes, initial_wallet_name, wallet_name=None):
        initial_wallet = j.clients.stellar.get(initial_wallet_name)
        if wallet_name:
            wallet = j.clients.stellar.get(wallet_name)
        else:
            wallet = self.provision_wallet
        # get total amount
        amount = self._calculate_initialization_fee(transaction_hashes, initial_wallet)
        if not amount:
            return True
        return self.pay_amount(initial_wallet.address, amount, wallet)

    def _calculate_initialization_fee(self, transaction_hashes, initial_wallet):
        amount = 0
        for t_hash in transaction_hashes:
            effects = initial_wallet.get_transaction_effects(t_hash)
            for effect in effects:
                amount += (
                    abs(float(effect.amount)) + TRANSACTION_FEES
                )  # transaction fees to not drain the initialization wallet
        amount = round(amount, 6)
        return amount

    def _get_wallet_balance(self, wallet):
        balances = wallet.get_balance().balances
        for b in balances:
            if b.asset_code != "TFT":
                continue
            return float(b.balance)
        return 0

    def pay_amount(self, address, amount, wallet, memo_text=""):
        j.logger.info(f"transfering amount: {amount} from wallet: {wallet.instance_name} to address: {address}")
        deadline = j.data.time.now().timestamp + 5 * 60
        a = wallet._get_asset()
        has_funds = None
        while j.data.time.now().timestamp < deadline:
            if not has_funds:
                try:
                    balances = wallet.get_balance().balances
                    for b in balances:
                        if b.asset_code != "TFT":
                            continue
                        if amount <= float(b.balance) + TRANSACTION_FEES:
                            has_funds = True
                            break
                        else:
                            has_funds = False
                            raise j.exceptions.Validation(
                                f"Not enough funds in wallet {wallet.instance_name} to pay amount: {amount}. current balance: {b.balance}"
                            )
                except Exception as e:
                    if has_funds is False:
                        j.logger.error(f"Not enough funds in wallet {wallet.instance_name} to pay amount: {amount}")
                        raise e
                    j.logger.warning(f"Failed to get wallet {wallet.instance_name} balance due to error: {str(e)}")
                    continue

            try:
                return wallet.transfer(
                    address, amount=round(amount, 6), asset=f"{a.code}:{a.issuer}", memo_text=memo_text
                )
            except Exception as e:
                j.logger.warning(f"failed to submit payment to stellar due to error {str(e)}")
        j.logger.critical(
            f"Failed to submit payment to stellar in time to: {address} amount: {amount} for wallet: {wallet.instance_name}"
        )
        raise j.exceptions.Runtime(
            f"Failed to submit payment to stellar in time to: {address} amount: {amount} for wallet: {wallet.instance_name}"
        )

    def get_pools_expiration(self):
        active_pools = self.active_pools
        if not active_pools:
            return 0
        if len(active_pools) < 2:
            return active_pools[0].empty_at
        return min(*[p.empty_at for p in active_pools])

    def get_total_funds(self):
        total_tfts = 0
        for wallet in [self.prepaid_wallet, self.provision_wallet]:
            for balance in wallet.get_balance().balances:
                if balance.asset_code == "TFT":
                    total_tfts += float(balance.balance)
                    break
        return total_tfts

    def get_current_spec(self, load_info=True):
        """
        return
        dict:
            {
                "plan": self.flavor,
                "nodes": [additional_nodes_flavors],
                "services": {
                    "services.IP": count
                }
                "no_nodes": no_nodes # that were not deployed during initial vdc deployment
            }
        """
        if load_info:
            self.load_info()
        result = {"plan": self.flavor, "nodes": [], "services": {VDC_SIZE.Services.IP: 0}}
        no_nodes = VDC_SIZE.VDC_FLAVORS[self.flavor]["k8s"]["no_nodes"]
        node_flavor = VDC_SIZE.VDC_FLAVORS[self.flavor]["k8s"]["size"]
        for k8s in self.kubernetes:
            if k8s.role == KubernetesRole.MASTER:
                continue
            metadata = self._decrypt_metadata(k8s.wid)
            if k8s.size == node_flavor and no_nodes > 0 and not metadata.get("external"):
                no_nodes -= 1
                continue
            result["nodes"].append(k8s.size)
            if k8s.public_ip != "::/128":
                result["services"][VDC_SIZE.Services.IP] += 1
        result["no_nodes"] = no_nodes
        return result

    def _decrypt_metadata(self, wid, workload=None):
        identity = self._get_identity()
        workload = workload or j.sals.zos.get(identity.instance_name).workloads.get(wid)
        metadata = j.sals.reservation_chatflow.deployer.decrypt_metadata(workload.info.metadata, identity.instance_name)
        return j.data.serializers.json.loads(metadata)

    def calculate_spec_price(self, load_info=True):
        discount = FARM_DISCOUNT.get()
        current_spec = self.get_current_spec(load_info)
        total_price = (
            VDC_SIZE.PRICES["plans"][self.flavor]
            + current_spec["services"][VDC_SIZE.Services.IP] * VDC_SIZE.PRICES["services"][VDC_SIZE.Services.IP]
        )
        for size in current_spec["nodes"]:
            total_price += VDC_SIZE.PRICES["nodes"][size]
        return total_price * (1 - discount)

    def calculate_funded_period(self, load_info=True):
        """
        return how many days can the vdc be extended with prepaid + provisioning wallet
        """
        if load_info:
            self.load_info()
        prepaid_wallet_balance = self._get_wallet_balance(self.prepaid_wallet)
        provision_wallet_balance = self._get_wallet_balance(self.provision_wallet)

        days_prepaid_can_fund = (prepaid_wallet_balance / self.calculate_spec_price(load_info)) * 30
        days_provisioning_can_fund = provision_wallet_balance / (self.calculate_active_units_price() * 60 * 60 * 24)
        return days_prepaid_can_fund + days_provisioning_can_fund

    def calculate_active_units_price(self):
        cus = sus = ipv4us = 0
        for pool in self.active_pools:
            cus += pool.active_cu
            sus += pool.active_su
            ipv4us += pool.active_ipv4
        return self._get_identity().explorer.prices.calculate(cus, sus, ipv4us)  # TFTs per second

    def calculate_expiration_value(self, load_info=True):
        funded_period = self.calculate_funded_period(load_info)
        pools_expiration = self.get_pools_expiration()
        return pools_expiration + funded_period * 24 * 60 * 60

    def fund_difference(self, funding_wallet_name, destination_wallet_name=None):
        wallet = j.clients.stellar.find(funding_wallet_name)
        destination_wallet_name = destination_wallet_name or self.provision_wallet.instance_name
        dst_wallet = j.clients.stellar.find(destination_wallet_name)
        current_balance = self._get_wallet_balance(dst_wallet)
        j.logger.info(f"current balance in {destination_wallet_name} is {current_balance}")
        vdc_cost = float(j.tools.zos.consumption.calculate_vdc_price(self.flavor.value)) / 2
        j.logger.info(f"vdc_cost: {vdc_cost}")
        if vdc_cost > current_balance:
            diff = float(vdc_cost) - float(current_balance)
            j.logger.info(f"funding diff: {diff} for vdc {self.vdc_name} from wallet: {funding_wallet_name}")
            self.pay_amount(dst_wallet.address, diff, wallet)

    def get_ssh_client(self, name, ip_address, user, private_key_path=None):
        private_key_path = (
            private_key_path or f"{j.core.dirs.CFGDIR}/vdc/keys/{self.owner_tname}/{self.vdc_name}/id_rsa"
        )
        if not j.sals.fs.exists(private_key_path):
            private_key_path = "/root/.ssh/id_rsa"
        if not j.sals.fs.exists(private_key_path):
            raise j.exceptions.Input(f"couldn't find key at default locations")
        j.logger.info(f"getting ssh_client to: {user}@{ip_address} using key: {private_key_path}")
        client_name = SSH_KEY_PREFIX + name
        j.clients.sshkey.delete(client_name)
        ssh_key = j.clients.sshkey.get(client_name)
        ssh_key.private_key_path = private_key_path
        ssh_key.load_from_file_system()
        j.clients.sshclient.delete(client_name)
        ssh_client = j.clients.sshclient.get(client_name, user=user, host=ip_address, sshkey=client_name)
        return ssh_client

    def find_worker_farm(self, flavor, farm_name=None, public_ip=False):
        if farm_name:
            return farm_name, self._check_added_worker_capacity(flavor, farm_name, public_ip)
        farms = j.config.get("NETWORK_FARMS", []) if public_ip else j.config.get("COMPUTE_FARMS", [])
        for farm in farms:
            if self._check_added_worker_capacity(flavor, farm, public_ip):
                return farm, True
        else:
            self.load_info()
            pool_id = [n for n in self.kubernetes if n.role == KubernetesRole.MASTER][-1].pool_id
            farm_name = j.sals.marketplace.deployer.get_pool_farm_name(pool_id)
            return farm_name, self._check_added_worker_capacity(flavor, farm_name, public_ip)

    def _check_added_worker_capacity(self, flavor, farm_name, public_ip=False):
        if public_ip:
            zos = j.sals.zos.get()
            farm = zos._explorer.farms.get(farm_name=farm_name)
            available_ips = False
            for address in farm.ipaddresses:
                if not address.reservation_id:
                    available_ips = True
                    break
            if not available_ips:
                return False

        old_node_ids = []
        self.load_info()
        for k8s_node in self.kubernetes:
            old_node_ids.append(k8s_node.node_id)
        cc = CapacityChecker(farm_name)
        cc.exclude_nodes(*old_node_ids)
        if isinstance(flavor, str):
            flavor = VDC_SIZE.K8SNodeFlavor[flavor.upper()]
        if not cc.add_query(**VDC_SIZE.K8S_SIZES[flavor]):
            return False
        return True
