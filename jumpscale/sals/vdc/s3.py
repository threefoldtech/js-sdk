import math
from jumpscale.loader import j
from jumpscale.clients.explorer.models import DiskType, ZDBMode
from jumpscale.sals.reservation_chatflow import deployer
from jumpscale.sals.reservation_chatflow.deployer import DeploymentFailed
from jumpscale.clients.explorer.models import NextAction
import datetime

from .base_component import VDCBaseComponent
from .size import MINIO_CPU, MINIO_MEMORY, MINIO_DISK, S3_NO_DATA_NODES, S3_NO_PARITY_NODES


class VDCS3Deployer(VDCBaseComponent):
    def deploy_s3_minio_container(self, pool_id, ak, sk, ssh_key, scheduler, zdb_wids, solution_uuid, password):
        zdb_configs = []
        self.vdc_deployer.info(f"deploying minio for zdbs: {zdb_wids}")
        for zid in zdb_wids:
            zdb_configs.append(deployer.get_zdb_url(zid, password, identity_name=self.identity.instance_name))
        self.vdc_deployer.info(f"zdb_configs: {zdb_configs}")

        network_view = deployer.get_network_view(self.vdc_name, identity_name=self.identity.instance_name)
        for node in scheduler.nodes_by_capacity(
            cru=MINIO_CPU, mru=MINIO_MEMORY / 1024, sru=MINIO_DISK / 1024, ip_version="IPv6"
        ):
            self.vdc_deployer.info(f"node {node.node_id} selected for minio")
            try:
                result = deployer.add_network_node(
                    self.vdc_name, node, pool_id, network_view, self.bot, self.identity.instance_name
                )
                if result:
                    for wid in result["ids"]:
                        success = deployer.wait_workload(
                            wid, self.bot, 5, identity_name=self.identity.instance_name, cancel_by_uuid=False
                        )
                        if not success:
                            self.vdc_deployer.error(f"workload {wid} failed when adding node to network")
                            raise DeploymentFailed()
            except DeploymentFailed:
                self.vdc_deployer.error(f"failed to deploy minio network on node {node.node_id}.")
                continue

            network_view = network_view.copy()
            ip_address = network_view.get_free_ip(node)
            self.vdc_deployer.info(f"minio ip address {ip_address}")
            try:
                result = deployer.deploy_minio_containers(
                    pool_id,
                    self.vdc_name,
                    [node.node_id],
                    [ip_address],
                    zdb_configs,
                    ak,
                    sk,
                    ssh_key,
                    MINIO_CPU,
                    MINIO_MEMORY,
                    S3_NO_DATA_NODES,
                    S3_NO_PARITY_NODES,
                    public_ipv6=True,
                    disk_size=int(MINIO_DISK / 1024),
                    bot=self.bot,
                    identity_name=self.identity.instance_name,
                    # form_info={"chatflow": "minio"},
                    # name=self.vdc_name,
                    solution_uuid=solution_uuid,
                    description=self.vdc_deployer.description,
                )
            except DeploymentFailed as e:
                if e.wid:
                    workload = self.zos.workloads.get(e.wid)
                    self.vdc_deployer.error(
                        f"failed to deploy minio volume wid: {e.wid} on node {workload.info.node_id}"
                    )
                else:
                    self.vdc_deployer.error(f"failed to deploy minio volume due to error {str(e)}")
                continue
            wid = result[0]
            try:
                success = deployer.wait_workload(
                    wid, self.bot, identity_name=self.identity.instance_name, cancel_by_uuid=False
                )
                if not success:
                    raise DeploymentFailed()
                self.vdc_deployer.info(f"minio container deployed successfully wid: {wid}")
                return wid
            except DeploymentFailed:
                self.vdc_deployer.error(f"failed to deploy minio container wid: {wid}")
                continue
        self.vdc_deployer.error("no nodes available to deploy minio container")

    def deploy_s3_zdb(self, pool_id, scheduler, storage_per_zdb, password, solution_uuid, no_nodes=None):
        open("/tmp/times", "a").write(f"TIMESTAMP: start_one_zdb_batch {datetime.datetime.now()}\n")
        deployment_nodes = []
        wids = []
        no_nodes = no_nodes or S3_NO_DATA_NODES + S3_NO_PARITY_NODES
        for node in scheduler.nodes_by_capacity(pool_id=pool_id, hru=math.ceil(storage_per_zdb), ip_version="IPv6"):
            self.vdc_deployer.info(f"node {node.node_id} selected for zdb")
            deployment_nodes.append(node)
            if len(deployment_nodes) < no_nodes - len(wids):
                continue
            self.vdc_deployer.info(f"staring zdb deployment on nodes {[node.node_id for node in deployment_nodes]}")
            result = []
            for node in deployment_nodes:
                self.vdc_deployer.info(f"deploying zdb on node: {node.node_id}")
                result.append(
                    deployer.deploy_zdb(
                        pool_id=pool_id,
                        node_id=node.node_id,
                        size=int(storage_per_zdb),
                        disk_type=DiskType.HDD,
                        mode=ZDBMode.Seq,
                        password=password,
                        # form_info={"chatflow": "minio"},
                        # name=self.vdc_name,
                        solution_uuid=solution_uuid,
                        identity_name=self.identity.instance_name,
                        description=self.vdc_deployer.description,
                    )
                )
            for wid in result:
                try:
                    success = deployer.wait_workload(
                        wid, bot=self.bot, expiry=5, identity_name=self.identity.instance_name, cancel_by_uuid=False
                    )
                    if not success:
                        raise DeploymentFailed()
                    wids.append(wid)
                    self.vdc_deployer.info(f"zdb deployed successfully wid: {wid}")
                except DeploymentFailed:
                    self.vdc_deployer.error(f"failed to deploy zdb wid: {wid}")
                    continue
            if len(wids) == no_nodes:
                self.vdc_deployer.info(f"{no_nodes} zdbs deployed successfully on pool {pool_id}")
                open("/tmp/times", "a").write(f"TIMESTAMP: end_one_zdb_batch {datetime.datetime.now()}\n")
                return wids
            deployment_nodes = []
        self.vdc_deployer.error("no nodes available to deploy zdb")

    def expose_zdbs(self, starting_port=9910):
        if not self.vdc_instance.s3.zdbs:
            self.vdc_instance.load_info(load_proxy=True)
        for zdb in self.vdc_instance.s3.zdbs:
            if zdb.proxy_address:
                self.vdc_deployer.info(f"zdb: {zdb.wid} is already exposed at address: {zdb.proxy_address}")
            else:
                try:
                    self.vdc_deployer.info(f"exposing zdb: {zdb.wid} on port: {starting_port}")
                    public_ip = self.vdc_deployer.proxy.socat_proxy(
                        f"zdb_{zdb.wid}", starting_port, 9900, f"[{zdb.ip_address}]"
                    )
                    zdb.proxy_address = f"{public_ip}:{starting_port}"
                    self.vdc_deployer.info(f"zdb: {zdb.wid} is exposed successfully on address: {zdb.proxy_address}")
                except Exception as e:
                    self.vdc_deployer.error(f"failed to proxy zdb: {zdb.wid} due to error: {str(e)}")
            starting_port += 1

    def delete_zdb(self, wid):
        workload = self.zos.workloads.get(wid)
        if workload.info.next_action == NextAction.DEPLOY:
            self.zos.workloads.decomission(wid)

        return workload
