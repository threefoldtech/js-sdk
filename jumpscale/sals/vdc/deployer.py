from jumpscale.sals.reservation_chatflow.deployer import DeploymentFailed
from jumpscale.loader import j
import uuid
from jumpscale.sals.zos import get as get_zos
from jumpscale.sals.reservation_chatflow import deployer, solutions
import gevent
from .size import *
from .scheduler import Scheduler
from jumpscale.clients.explorer.models import ZDBMode, DiskType
import uuid
from .s3 import VDCS3Deployer
from .kubernetes import VDCKubernetesDeployer


VDC_IDENTITY_FORMAT = "vdc_{}_{}"  # tname, vdc_name
PREFERED_FARM = "freefarm"
IP_VERSION = "IPv4"
IP_RANGE = "10.200.0.0/16"


class VDCDeployer:
    def __init__(self, vdc_name, tname, password, email, wallet_name=None, bot=None):
        self.vdc_name = vdc_name
        self.tname = tname
        self.bot = bot
        self.identity = None
        self._generate_identity(password, email)
        self._zos = None
        self.wallet_name = wallet_name
        self._wallet = None
        self._kubernetes = None
        self._s3 = None

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

    def _generate_identity(self, password, email):
        # create a user identity from an old one or create a new one
        username = VDC_IDENTITY_FORMAT.format(self.tname, self.vdc_name)
        words = j.data.encryption.key_to_mnemonic(password.encode().zfill(32))
        identity_name = f"vdc_ident_{uuid.uuid4().hex}"
        self.identity = j.core.identity.get(
            identity_name, tname=username, email=email, words=words, explorer_url=j.core.identity.me.explorer_url
        )
        try:
            self.identity.register()
            self.identity.save()
        except Exception as e:
            j.logger.error(f"failed to generate identity for user {identity_name} due to error {str(e)}")
            # TODO: raise alert with traceback
            raise j.exceptions.Runtime(f"failed to generate identity for user {identity_name} due to error {str(e)}")

    def initialize_new_vdc_deployment(self, scheduler, farm_name, cu, su):
        """
        create pool and network for new vdc
        """
        # create pool
        pool_info = self.zos.pools.create(int(cu), int(su), farm_name)
        self.zos.billing.payout_farmers(self.wallet, pool_info)
        success = self.wait_pool_payment(pool_info.reservation_id)
        if not success:
            raise j.exceptions.Runtime(f"Pool {pool_info.reservation_id} resource reservation timedout")
        access_nodes = scheduler.nodes_by_capacity(ip_version=IP_VERSION)
        network_success = False
        for access_node in access_nodes:
            network_success = True
            result = deployer.deploy_network(
                self.vdc_name, access_node, IP_RANGE, IP_VERSION, pool_info.reservation_id, self.identity.instance_name,
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
                    j.logger.error(f"network workload {wid} failed on node {access_node.node_id} due to error {str(e)}")
                    break
            if network_success:
                # store wireguard config
                wg_quick = result["wg"]
                j.sals.fs.mkdirs(f"{j.core.dirs.CFGDIR}/vdc/wireguard/{self.tname}")
                j.sals.fs.write_file(f"{j.core.dirs.CFGDIR}/vdc/wireguard/{self.tname}/{self.vdc_name}.conf", wg_quick)
                break
        if not network_success:
            raise j.exceptions.Runtime(
                f"all retries to create a network with ip version {IP_VERSION} on farm {farm_name} failed"
            )

        return pool_info.reservation_id

    def _calculate_new_vdc_pool_units(self, k8s_size_dict, s3_size_dict=None):
        total_cus, total_sus = deployer.calculate_capacity_units(**K8S_SIZES[k8s_size_dict["size"]])
        total_cus = total_cus * k8s_size_dict["no_nodes"]
        total_sus = total_sus * k8s_size_dict["no_nodes"]
        if s3_size_dict:
            minio_cus, minio_sus = deployer.calculate_capacity_units(
                cru=MINIO_CPU, mru=MINIO_MEMORY / 1024, sru=MINIO_DISK / 1024
            )
            total_cus += minio_cus
            total_sus += minio_sus
            storage_per_zdb = S3_ZDB_SIZES[s3_size_dict["size"]]["sru"] / S3_NO_DATA_NODES
            zdb_cus, zdb_sus = deployer.calculate_capacity_units(sru=storage_per_zdb)
            zdb_cus = zdb_sus * (S3_NO_DATA_NODES + S3_NO_PARITY_NODES)
            total_cus += zdb_cus
            total_sus += zdb_sus
        return total_cus, total_sus

    def deploy_vdc(
        self, cluster_secret, minio_ak, minio_sk, ssh_keys, flavor=VDCFlavor.SILVER, farm_name=PREFERED_FARM
    ):
        """deploys a new vdc
        Args:
            cluster_secret: secretr for k8s cluster. used to join nodes in the cluster (will be stored in woprkload metadata)
            minio_ak: access key for minio
            minio_sk: secret key for minio
            flavor: vdc flavor key
            farm_name: where to initialize the vdc
        """
        vdc_uuid = uuid.uuid4().hex
        scheduler = Scheduler(farm_name)
        size_dict = VDC_FLAFORS[flavor]
        k8s_size_dict = size_dict["k8s"]
        s3_size_dict = size_dict["s3"]
        cus, sus = self._calculate_new_vdc_pool_units(k8s_size_dict, s3_size_dict)
        cus = cus * 60 * 60 * 24 * 30
        sus = sus * 60 * 60 * 24 * 30
        pool_id = self.initialize_new_vdc_deployment(scheduler, farm_name, cus, sus)
        storage_per_zdb = S3_ZDB_SIZES[s3_size_dict["size"]]["sru"] / S3_NO_DATA_NODES
        k8s_thread = gevent.spawn(
            self.kubernetes.deploy_kubernetes, pool_id, scheduler, k8s_size_dict, cluster_secret, ssh_keys, vdc_uuid
        )
        zdb_thread = gevent.spawn(self.s3.deploy_s3_zdb, pool_id, scheduler, storage_per_zdb, vdc_uuid, vdc_uuid)
        gevent.joinall([k8s_thread, zdb_thread])
        zdb_wids = zdb_thread.value
        k8s_wids = k8s_thread.value

        if not zdb_wids or not k8s_wids:
            solutions.cancel_solution_by_uuid(vdc_uuid, self.identity.instance_name)
            return False
        try:
            minio_wid = self.s3.deploy_s3_minio_container(
                pool_id, minio_ak, minio_sk, ssh_keys, scheduler, zdb_wids, vdc_uuid
            )
            if not minio_wid:
                solutions.cancel_solution_by_uuid(vdc_uuid, self.identity.instance_name)
                return False
        except IndexError:
            raise j.exceptions.Runtime("all tries to deploy minio container has failed")

        # start wireguard
        rc, out, err = j.sals.process.execute(
            f"wg-quick up {j.core.dirs.CFGDIR}/vdc/wireguard/{self.tname}/{self.vdc_name}.conf"
        )
        if rc:
            # what to do
            pass
        # download wireguard config from master

    def wait_pool_payment(self, pool_id, exp=5, trigger_cus=0, trigger_sus=1):
        expiration = j.data.time.now().timestamp + exp * 60
        while j.data.time.get().timestamp < expiration:
            pool = self.zos.pools.get(pool_id)
            if pool.cus >= trigger_cus and pool.sus >= trigger_sus:
                return True
            gevent.sleep(2)
        return False

    def __del__(self):
        if self.identity:
            j.core.identity.delete(self.identity.instance_name)
