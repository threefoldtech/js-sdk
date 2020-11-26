import hashlib
from jumpscale.clients.explorer.models import ZdbNamespace, K8s, Volume, Container, DiskType
import math

import gevent
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot
from jumpscale.sals.kubernetes import Manager
from jumpscale.sals.reservation_chatflow import deployer, solutions
from jumpscale.sals.zos import get as get_zos

from .kubernetes import VDCKubernetesDeployer
from .proxy import VDCProxy
from .s3 import VDCS3Deployer
from .monitoring import VDCMonitoring
from .threebot import VDCThreebotDeployer
from .scheduler import CapacityChecker, Scheduler
from .size import *

VDC_IDENTITY_FORMAT = "vdc_{}_{}"  # tname, vdc_name
PREFERED_FARM = "freefarm"
IP_VERSION = "IPv4"
IP_RANGE = "10.200.0.0/16"
MARKETPLACE_HELM_REPO_URL = "https://threefoldtech.github.io/marketplace-charts/"
NO_DEPLOYMENT_BACKUP_NODES = 0


class VDCDeployer:
    def __init__(
        self,
        password: str,
        vdc_instance,
        bot: GedisChatBot = None,
        proxy_farm_name: str = None,
        mgmt_kube_config_path: str = None,
    ):
        self.vdc_instance = vdc_instance
        self.vdc_name = self.vdc_instance.vdc_name
        self.flavor = self.vdc_instance.flavor
        self.tname = j.data.text.removesuffix(self.vdc_instance.owner_tname, ".3bot")
        self.bot = bot
        self.identity = None
        self.password = password
        self.password_hash = hashlib.md5(self.password.encode()).hexdigest()
        self.email = f"vdc_{self.vdc_instance.solution_uuid}"
        self.wallet_name = self.vdc_instance.wallet.instance_name
        self.proxy_farm_name = proxy_farm_name
        self.mgmt_kube_config_path = mgmt_kube_config_path
        self.vdc_uuid = self.vdc_instance.solution_uuid
        self.description = j.data.serializers.json.dumps({"vdc_uuid": self.vdc_uuid})
        self._log_format = f"VDC: {self.vdc_uuid} NAME: {self.vdc_name}: OWNER: {self.tname} {{}}"
        self._generate_identity()
        if not self.vdc_instance.identity_tid:
            self.vdc_instance.identity_tid = self.identity.tid
            self.vdc_instance.save()
        self._zos = None
        self._wallet = None
        self._kubernetes = None
        self._s3 = None
        self._proxy = None
        self._ssh_key = None
        self._vdc_k8s_manager = None
        self._threebot = None
        self._monitoring = None

    @property
    def monitoring(self):
        if not self._monitoring:
            self._monitoring = VDCMonitoring(self)
        return self._monitoring

    @property
    def threebot(self):
        if not self._threebot:
            self._threebot = VDCThreebotDeployer(self)
        return self._threebot

    @property
    def vdc_k8s_manager(self):
        if not self._vdc_k8s_manager:
            config_path = f"{j.core.dirs.CFGDIR}/vdc/kube/{self.tname}/{self.vdc_name}.yaml"
            self._vdc_k8s_manager = Manager(config_path)
        return self._vdc_k8s_manager

    @property
    def kubernetes(self):
        if not self._kubernetes:
            self._kubernetes = VDCKubernetesDeployer(self)
        return self._kubernetes

    @property
    def s3(self):
        if not self._s3:
            self._s3 = VDCS3Deployer(self)
        return self._s3

    @property
    def proxy(self):
        if not self._proxy:
            self._proxy = VDCProxy(self, self.proxy_farm_name)
        return self._proxy

    @property
    def wallet(self):
        if not self._wallet:
            wallet_name = self.wallet_name or j.core.config.get("VDC_WALLET")
            self._wallet = j.clients.stellar.get(wallet_name)
        return self._wallet

    @property
    def explorer(self):
        if self.identity:
            return self.identity.explorer
        return j.core.identity.me.explorer

    @property
    def zos(self):
        if not self._zos:
            self._zos = get_zos(self.identity.instance_name)
        return self._zos

    @property
    def ssh_key(self):
        if not self._ssh_key:
            self._ssh_key = j.clients.sshkey.get(self.vdc_name)
            vdc_key_path = j.core.config.get("VDC_KEY_PATH", "~/.ssh/id_rsa")
            self._ssh_key.private_key_path = j.sals.fs.expanduser(vdc_key_path)
            self._ssh_key.load_from_file_system()
        return self._ssh_key

    def _generate_identity(self):
        # create a user identity from an old one or create a new one
        username = VDC_IDENTITY_FORMAT.format(self.tname, self.vdc_name)
        words = j.data.encryption.key_to_mnemonic(self.password_hash.encode())
        identity_name = f"vdc_ident_{self.vdc_uuid}"
        self.identity = j.core.identity.get(
            identity_name, tname=username, email=self.email, words=words, explorer_url=j.core.identity.me.explorer_url
        )
        try:
            self.identity.register()
            self.identity.save()
        except Exception as e:
            j.logger.error(f"failed to generate identity for user {identity_name} due to error {str(e)}")
            raise j.exceptions.Runtime(f"failed to generate identity for user {identity_name} due to error {str(e)}")

    def init_new_vdc(self, scheduler, farm_name, cu, su, pool_id=None):
        """
        create pool if needed and network for new vdc
        """
        self.info(f"initializing vdc on farm {farm_name}")

        # seach if a pool exists that can be used
        self.info(f"searching for an old pool on farm {farm_name}")
        if not pool_id:
            for pool in self.zos.pools.list():
                farm_id = deployer.get_pool_farm_id(pool.pool_id, pool, self.identity.instance_name)
                farm = self.explorer.farms.get(farm_id)
                if farm_name == farm.name:
                    pool_id = pool.pool_id
                    self.info(f"found old pool {pool_id} on farm {farm_name}")
                    break
            if not pool_id:
                self.info(f"couldn't find any old pool on farm {farm_name}")

        if not pool_id:
            # create pool
            self.info(f"creating a new pool on farm {farm_name}")
            pool_info = self.zos.pools.create(math.ceil(cu), math.ceil(su), farm_name)
            self.info(
                f"pool reservation sent. pool id: {pool_info.reservation_id}, escrow: {pool_info.escrow_information}"
            )
            pool_id = pool_info.reservation_id
        else:
            node_ids = [node.node_id for node in self.zos.nodes_finder.nodes_search(farm_name=farm_name)]
            pool = self.zos.pools.get(pool_id)
            required_cus = max(0, cu - pool.cus)
            required_sus = max(0, su - pool.sus)
            self.info(f"extending pool {pool_id} with cus: {required_cus} sus: {required_sus}")
            pool_info = self.zos.pools.extend(pool_id, required_cus, required_sus, node_ids=node_ids)

        self.zos.billing.payout_farmers(self.wallet, pool_info)
        self.info(f"pool {pool_id} paid. waiting resources")
        success = self.wait_pool_payment(pool_id)
        if not success:
            raise j.exceptions.Runtime(
                f"Pool {pool_info.reservation_id} pool_id: {pool_id} resource reservation timedout"
            )
        nv = deployer.get_network_view(self.vdc_name, identity_name=self.identity.instance_name)
        if nv:
            return pool_id
        access_nodes = scheduler.nodes_by_capacity(ip_version=IP_VERSION)
        network_success = False
        for access_node in access_nodes:
            self.info(f"deploying network on node {access_node.node_id}")
            network_success = True
            result = deployer.deploy_network(
                self.vdc_name, access_node, IP_RANGE, IP_VERSION, pool_id, self.identity.instance_name,
            )
            for wid in result["ids"]:
                try:
                    success = deployer.wait_workload(
                        wid,
                        breaking_node_id=access_node.node_id,
                        identity_name=self.identity.instance_name,
                        bot=self.bot,
                    )
                    network_success = network_success and success
                except Exception as e:
                    network_success = False
                    self.error(f"network workload {wid} failed on node {access_node.node_id} due to error {str(e)}")
                    break
            if network_success:
                self.info(
                    f"saving wireguard config to {j.core.dirs.CFGDIR}/vdc/wireguard/{self.tname}/{self.vdc_name}.conf"
                )
                # store wireguard config
                wg_quick = result["wg"]
                j.sals.fs.mkdirs(f"{j.core.dirs.CFGDIR}/vdc/wireguard/{self.tname}")
                j.sals.fs.write_file(f"{j.core.dirs.CFGDIR}/vdc/wireguard/{self.tname}/{self.vdc_name}.conf", wg_quick)
                break
        if not network_success:
            raise j.exceptions.Runtime(
                f"all retries to create a network with ip version {IP_VERSION} on farm {farm_name} failed"
            )

        return pool_id

    def _calculate_new_vdc_pool_units(self, k8s_flavor, duration):
        zdb = ZdbNamespace()
        zdb.size = ZDB_STARTING_SIZE
        deployments = [zdb] * (S3_NO_DATA_NODES + S3_NO_PARITY_NODES)
        k = K8s()
        k.size = k8s_flavor.value
        deployments += [k, k]
        v = Volume()
        v.size = int(MINIO_DISK / 1024)
        v.type = DiskType.SSD
        deployments.append(v)
        minio_container = Container()
        minio_container.capacity.disk_size = 256
        minio_container.capacity.memory = MINIO_MEMORY
        minio_container.capacity.cpu = MINIO_CPU
        minio_container.capacity.disk_type = DiskType.SSD
        deployments.append(minio_container)
        threebot_container = Container()
        threebot_container.capacity.disk_size = THREEBOT_DISK
        threebot_container.capacity.memory = THREEBOT_MEMORY
        threebot_container.capacity.cpu = THREEBOT_CPU
        threebot_container.capacity.disk_type = DiskType.SSD
        deployments.append(threebot_container)

        cus = sus = 0
        for deployment in deployments:
            ru = deployment.resource_units()
            cloud_units = ru.cloud_units()
            cus += cloud_units.cu
            sus += cloud_units.su
        return cus * 60 * 60 * 24 * duration, sus * 60 * 60 * 24 * duration

    def _check_new_vdc_farm_capacity(self, farm_name, k8s_size_dict):
        k8s_query = K8S_SIZES[k8s_size_dict["size"]].copy()
        k8s_query["no_nodes"] = k8s_size_dict["no_nodes"]
        query_details = {
            "k8s": k8s_query,
            "s3_zdb": {
                "sru": ZDB_STARTING_SIZE,
                "no_nodes": S3_NO_DATA_NODES + S3_NO_PARITY_NODES,
                "ip_version": "IPv6",
            },
            "s3_minio": {
                "cru": MINIO_CPU,
                "mru": MINIO_MEMORY / 1024,
                "sru": MINIO_DISK / 1024 + 0.25,
                "no_nodes": 1,
                "ip_version": "IPv6",
            },
            "threebot": {
                "cru": THREEBOT_CPU,
                "mru": THREEBOT_MEMORY / 1024,
                "sru": THREEBOT_DISK / 1024,
                "no_nodes": 1,
            },
        }
        cc = CapacityChecker(farm_name)
        cc.add_query(ip_version=IP_VERSION)
        for query in query_details.values():
            query["backup_no"] = NO_DEPLOYMENT_BACKUP_NODES
            if not cc.add_query(**query):
                return False
        return cc.result

    def deploy_vdc(self, cluster_secret, minio_ak, minio_sk, farm_name=PREFERED_FARM, pool_id=None):
        """deploys a new vdc
        Args:
            cluster_secret: secretr for k8s cluster. used to join nodes in the cluster (will be stored in woprkload metadata)
            minio_ak: access key for minio
            minio_sk: secret key for minio
            farm_name: where to initialize the vdc
        """
        self.info(f"deploying vdc flavor: {self.flavor} farm: {farm_name}")
        if len(minio_ak) < 3 or len(minio_sk) < 8:
            raise j.exceptions.Validation(
                "Access key length should be at least 3, and secret key length at least 8 characters"
            )
        scheduler = Scheduler(farm_name)
        size_dict = VDC_FLAFORS[self.flavor]
        k8s_size_dict = size_dict["k8s"]
        if not self._check_new_vdc_farm_capacity(farm_name, k8s_size_dict):
            raise j.exceptions.Runtime(
                f"farm {farm_name} doesn't have enough capacity to deploy vdc of flavor {self.flavor}"
            )

        cus, sus = self._calculate_new_vdc_pool_units(k8s_size_dict["size"], duration=size_dict["duration"])
        self.info(f"required cus: {cus}, sus: {sus}")
        pool_id = self.init_new_vdc(scheduler, farm_name, cus, sus, pool_id)
        self.info(f"vdc initialization successful")
        storage_per_zdb = ZDB_STARTING_SIZE
        threads = []
        k8s_thread = gevent.spawn(
            self.kubernetes.deploy_kubernetes,
            pool_id,
            scheduler,
            k8s_size_dict,
            cluster_secret,
            [self.ssh_key.public_key.strip()],
        )
        threads.append(k8s_thread)
        zdb_thread = gevent.spawn(
            self.s3.deploy_s3_zdb, pool_id, scheduler, storage_per_zdb, self.password, self.vdc_uuid
        )
        threads.append(zdb_thread)
        gevent.joinall(threads)
        zdb_wids = zdb_thread.value
        k8s_wids = k8s_thread.value
        self.info(f"k8s wids: {k8s_wids}")
        self.info(f"zdb wids: {zdb_wids}")

        if not k8s_wids or not zdb_wids:
            self.error(f"failed to deploy vdc. cancelling workloads with uuid {self.vdc_uuid}")
            self.rollback_vdc_deployment()
            return False

        minio_wid = self.s3.deploy_s3_minio_container(
            pool_id,
            minio_ak,
            minio_sk,
            self.ssh_key.public_key.strip(),
            scheduler,
            zdb_wids,
            self.vdc_uuid,
            self.password,
        )
        self.info(f"minio_wid: {minio_wid}")
        if not minio_wid:
            self.error(f"failed to deploy vdc. cancelling workloads with uuid {self.vdc_uuid}")
            self.rollback_vdc_deployment()
            return False

        threebot_wid = self.threebot.deploy_threebot(minio_wid, pool_id)
        self.info(f"threebot_wid: {threebot_wid}")
        if not threebot_wid:
            self.error(f"failed to deploy vdc. cancelling workloads with uuid {self.vdc_uuid}")
            self.rollback_vdc_deployment()
            return False

        # download kube config from master
        # k8s_workload = self.zos.workloads.get(k8s_wids[0])
        # master_ip = k8s_workload.master_ips[0]
        # kube_config = self.kubernetes.download_kube_config(master_ip)
        # config_dict = j.data.serializers.yaml.loads(kube_config)
        # config_dict["server"] = f"https://{master_ip}:6443"

        # minio_prometheus_job = self.s3.get_minio_prometheus_job(self.vdc_uuid, minio_api_subdomain)
        # return j.data.serializers.yaml.dumps(config_dict)

    def rollback_vdc_deployment(self):
        solutions.cancel_solution_by_uuid(self.vdc_uuid, self.identity.instance_name)
        nv = deployer.get_network_view(self.vdc_name, identity_name=self.identity.instance_name)
        if nv:
            solutions.cancel_solution(
                [workload.id for workload in nv.network_workloads], identity_name=self.identity.instance_name
            )

    def wait_pool_payment(self, pool_id, exp=5, trigger_cus=0, trigger_sus=1):
        expiration = j.data.time.now().timestamp + exp * 60
        while j.data.time.get().timestamp < expiration:
            pool = self.zos.pools.get(pool_id)
            if pool.cus >= trigger_cus and pool.sus >= trigger_sus:
                return True
            gevent.sleep(2)
        return False

    def _log(self, msg, loglevel="info"):
        getattr(j.logger, loglevel)(self._log_format.format(msg))

    def info(self, msg):
        self._log(msg, "info")

    def error(self, msg):
        self._log(msg, "error")

    def renew_plan(self, duration):
        self.vdc_instance.load_info()
        pool_ids = set()
        for zdb in self.vdc_instance.s3.zdbs:
            pool_ids.add(zdb.pool_id)
        for k8s in self.vdc_instance.kubernetes:
            pool_ids.add(k8s.pool_id)
        if self.vdc_instance.s3.minio.pool_id:
            pool_ids.add(self.vdc_instance.s3.minio.pool_id)
        if self.vdc_instance.threebot.pool_id:
            pool_ids.add(self.vdc_instance.threebot.pool_id)
        self.info(f"renew plan with pools: {pool_ids}")
        for pool_id in pool_ids:
            pool = self.zos.pools.get(pool_id)
            sus = pool.active_su * duration * 60 * 60 * 24
            cus = pool.active_cu * duration * 60 * 60 * 24
            pool_info = self.zos.pools.extend(pool_id, cus, sus)
            self.info(
                f"renew plan: extending pool {pool_id}, sus: {sus}, cus: {cus}, reservation_id: {pool_info.reservation_id}"
            )
            self.zos.billing.payout_farmers(self.wallet, pool_info)
        self.vdc_instance.expiration = j.data.time.utcnow().timestamp + duration * 60 * 60 * 24
        self.vdc_instance.updated = j.data.time.utcnow().timestamp
        if self.vdc_instance.is_blocked:
            self.vdc_instance.undo_grace_period_action()
