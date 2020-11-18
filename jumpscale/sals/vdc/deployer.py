from .proxy import VDCProxy
from jumpscale.loader import j
import uuid
from jumpscale.sals.zos import get as get_zos
from jumpscale.sals.reservation_chatflow import deployer, solutions
import gevent
from .size import *
from .scheduler import Scheduler
from .s3 import VDCS3Deployer
from .kubernetes import VDCKubernetesDeployer
from .models import VDCFACTORY
import hashlib
from jumpscale.sals.kubernetes import Manager
import math


VDC_IDENTITY_FORMAT = "vdc_{}_{}"  # tname, vdc_name
PREFERED_FARM = "freefarm"
IP_VERSION = "IPv4"
IP_RANGE = "10.200.0.0/16"
MARKETPLACE_HELM_REPO_URL = "https://threefoldtech.github.io/marketplace-charts/"


class VDCDeployer:
    def __init__(
        self,
        vdc_name,
        tname,
        password,
        email,
        wallet_name=None,
        bot=None,
        proxy_farm_name=None,
        mgmt_kube_config_path=None,
        vdc_uuid=None,
        flavor=VDCFlavor.SILVER,
    ):
        self.vdc_name = vdc_name
        self.tname = j.data.text.removesuffix(tname, ".3bot")
        self.bot = bot
        self.identity = None
        self.password = password
        self.email = email
        self.wallet_name = wallet_name
        self.proxy_farm_name = proxy_farm_name
        self.mgmt_kube_config_path = mgmt_kube_config_path
        self.description = j.data.serializers.json.dumps({"vdc_uuid": vdc_uuid})
        self.vdc_uuid = vdc_uuid or uuid.uuid4().hex
        self.flavor = flavor
        self._log_format = f"VDC: {self.vdc_uuid} NAME: {self.vdc_name}: OWNER: {self.tname} {{}}"
        self._generate_identity()
        self._zos = None
        self._wallet = None
        self._kubernetes = None
        self._s3 = None
        self._proxy = None
        self._ssh_key = None
        self._vdc_k8s_manager = None
        self._mgmt_k8s_manager = None

    @property
    def mgmt_k8s_manager(self):
        if not self._mgmt_k8s_manager:
            config_path = self.mgmt_kube_config_path or j.core.config.get(
                "VDC_MGMT_KUBE_CONFIG", f"{j.core.dirs.HOMEDIR}/.kube/config"
            )
            self._mgmt_k8s_manager = Manager(config_path)
        return self._mgmt_k8s_manager

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
        password_hash = hashlib.md5(self.password.encode()).hexdigest()
        words = j.data.encryption.key_to_mnemonic(password_hash.encode())
        identity_name = f"vdc_ident_{uuid.uuid4().hex}"
        self.identity = j.core.identity.get(
            identity_name, tname=username, email=self.email, words=words, explorer_url=j.core.identity.me.explorer_url
        )
        try:
            self.identity.register()
            self.identity.save()
        except Exception as e:
            j.logger.error(f"failed to generate identity for user {identity_name} due to error {str(e)}")
            # TODO: raise alert with traceback
            raise j.exceptions.Runtime(f"failed to generate identity for user {identity_name} due to error {str(e)}")

    def initialize_new_vdc_deployment(self, scheduler, farm_name, cu, su, pool_id=None):
        """
        create pool if needed and network for new vdc
        """
        # create pool
        self.info("initializing vdc")
        if not pool_id:
            pool_info = self.zos.pools.create(math.ceil(cu), math.ceil(su), farm_name)
            self.info(
                f"pool reservation sent. pool id: {pool_info.reservation_id}, escrow: {pool_info.escrow_information}"
            )
            self.zos.billing.payout_farmers(self.wallet, pool_info)
            self.info(f"pool {pool_info.reservation_id} paid. waiting resources")
            success = self.wait_pool_payment(pool_info.reservation_id)
            if not success:
                raise j.exceptions.Runtime(f"Pool {pool_info.reservation_id} resource reservation timedout")
            pool_id = pool_info.reservation_id

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

    def _calculate_new_vdc_pool_units(self, k8s_size_dict, s3_size_dict=None, duration=30):
        total_cus, total_sus = deployer.calculate_capacity_units(**K8S_SIZES[k8s_size_dict["size"]])
        total_cus = total_cus * k8s_size_dict["no_nodes"]
        total_sus = total_sus * k8s_size_dict["no_nodes"]
        if s3_size_dict:
            minio_cus, minio_sus = deployer.calculate_capacity_units(
                cru=MINIO_CPU, mru=MINIO_MEMORY / 1024, sru=MINIO_DISK / 1024
            )
            nginx_cus, nginx_sus = deployer.calculate_capacity_units(cru=1, mru=1, sru=0.25)
            storage_per_zdb = S3_ZDB_SIZES[s3_size_dict["size"]]["sru"] / S3_NO_DATA_NODES
            zdb_cus, zdb_sus = deployer.calculate_capacity_units(sru=storage_per_zdb)

            zdb_sus = zdb_sus * (S3_NO_DATA_NODES + S3_NO_PARITY_NODES)
            zdb_cus = zdb_cus * (S3_NO_DATA_NODES + S3_NO_PARITY_NODES)
            total_cus += zdb_cus + minio_cus + (2 * nginx_cus)
            total_sus += zdb_sus + minio_sus + (2 * nginx_sus)
        return total_cus * 60 * 60 * 24 * duration, total_sus * 60 * 60 * 24 * duration

    def deploy_vdc(self, cluster_secret, minio_ak, minio_sk, farm_name=PREFERED_FARM, pool_id=None):
        """deploys a new vdc
        Args:
            cluster_secret: secretr for k8s cluster. used to join nodes in the cluster (will be stored in woprkload metadata)
            minio_ak: access key for minio
            minio_sk: secret key for minio
            flavor: vdc flavor key
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
        s3_size_dict = size_dict["s3"]
        cus, sus = self._calculate_new_vdc_pool_units(k8s_size_dict, s3_size_dict, duration=size_dict["duration"])
        self.info(f"required cus: {cus}, sus: {sus}")
        pool_id = self.initialize_new_vdc_deployment(scheduler, farm_name, cus, sus, pool_id)
        self.info(f"vdc initialization successful")
        storage_per_zdb = S3_ZDB_SIZES[s3_size_dict["size"]]["sru"] / S3_NO_DATA_NODES
        threads = []
        k8s_thread = gevent.spawn(
            self.kubernetes.deploy_kubernetes,
            pool_id,
            scheduler,
            k8s_size_dict,
            cluster_secret,
            self.ssh_key.public_key.split("\n"),
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
        if not minio_wid:
            self.error(f"failed to deploy vdc. cancelling workloads with uuid {self.vdc_uuid}")
            self.rollback_vdc_deployment()
            return False

        trc_secret = uuid.uuid4().hex
        minio_api_prefix = f"s3-{self.vdc_name}-{self.tname}"
        minio_api_subdomain = self.proxy.proxy_container(
            prefix=minio_api_prefix,
            wid=minio_wid,
            port=9000,
            solution_uuid=self.vdc_uuid,
            pool_id=pool_id,
            secret=trc_secret,
        )

        minio_healing_prefix = f"s3-{self.vdc_name}-{self.tname}-healing"
        minio_healing_subdomain = self.proxy.proxy_container(
            prefix=minio_healing_prefix,
            wid=minio_wid,
            port=9010,
            solution_uuid=self.vdc_uuid,
            pool_id=pool_id,
            secret=f"healing{trc_secret}",
        )

        if not minio_api_subdomain or not minio_healing_subdomain:
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

        # self.mgmt_k8s_manager.add_helm_repo("marketplace", MARKETPLACE_HELM_REPO_URL)
        # self.mgmt_k8s_manager.install_chart(
        #     release=f"vdc_3bot_{self.vdc_uuid}",
        #     chart_name="3bot",
        # )
        self.save_config()
        # return j.data.serializers.yaml.dumps(config_dict)

    def rollback_vdc_deployment(self):
        solutions.cancel_solution_by_uuid(self.vdc_uuid, self.identity.instance_name)
        nv = deployer.get_network_view(self.vdc_name, identity_name=self.identity.instance_name)
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

    def save_config(self):
        vdc_instance = VDCFACTORY.get(f"vdc_{self.tname}_{self.vdc_name}")
        vdc_instance.vdc_name = self.vdc_name
        vdc_instance.solution_uuid = self.vdc_uuid
        vdc_instance.owner_tname = self.tname
        vdc_instance.identity_tid = self.identity.tid
        vdc_instance.flavor = self.flavor
        vdc_instance.save()
        return vdc_instance

    def _log(self, msg, loglevel="info"):
        getattr(j.logger, loglevel)(self._log_format.format(msg))

    def info(self, msg):
        self._log(msg, "info")

    def error(self, msg):
        self._log(msg, "error")

    def __del__(self):
        if self.identity:
            j.core.identity.delete(self.identity.instance_name)
