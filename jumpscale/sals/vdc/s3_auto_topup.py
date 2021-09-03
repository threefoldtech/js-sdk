from collections import defaultdict
import random
import re
from urllib.parse import urljoin

import gevent
from jumpscale.data import serializers
from jumpscale.loader import j
from jumpscale.tools import http

from jumpscale.clients.explorer.models import DiskType, WorkloadType, ZDBMode
from jumpscale.sals.reservation_chatflow import deployer, solutions
from jumpscale.sals.reservation_chatflow.deployer import DeploymentFailed
from jumpscale.sals.zos import get as get_zos

from .scheduler import GlobalScheduler

METRIC_KEYS = {"used": "minio_zerostor_data_size", "free": "minio_zerostor_data_free_space"}

MINIO_CONFIG_DICT = {
    "password": "",
    "namespace": "",
    "datastor": {
        "shards": [],  # set to zdb_dicts
        "spreading": "random",
        "pipeline": {
            "block_size": 4194304,
            "hashing": {"type": "blake2b_256", "private_key": ""},
            "compression": {"mode": "", "type": "snappy"},
            "encryption": {"private_key": "", "type": "aes"},
            "distribution": {"data_shards": 2, "parity_shards": 1},
        },
        "tls": {"enabled": False, "server": "", "root_ca": "", "min_version": "", "max_version": ""},
    },
    "jobs": 0,
    "minio": {"healer": {"listen": ""}},
}


def get_target_s3_zdb_config(target_name):
    zos = get_zos()
    for sol_dict in solutions.list_minio_solutions():
        if sol_dict["Name"] != target_name:
            continue
        minio_wid = sol_dict["wids"][0]
        workload = zos.workloads.get(minio_wid)
        sol_uuid = solutions.get_solution_uuid(workload)
        if not sol_uuid:
            continue
        solution_workloads = solutions.get_workloads_by_uuid(sol_uuid)
        cluster_zdb_configs = []
        for workload in solution_workloads:
            if workload.info.workload_type != WorkloadType.Zdb:
                continue
            # check the password
            # if no password, then it is old not supported

            # metadata is json serializable as the workload was identitified by solution_uuid
            metadata = serializers.json.loads(deployer.decrypt_metadata(workload.info.metadata))
            password = metadata.get("password")
            if not password:
                j.logger.error(
                    f"AUTO_TOPUP: zdb workload {workload.id} doesn't include password in metadata in s3 solution {sol_dict['Name']}"
                )
                raise j.exceptions.Validation(
                    f"AUTO_TOPUP: zdb workload {workload.id} doesn't include password in metadata in s3 solution {sol_dict['Name']}"
                )
            zdb_url = deployer.get_zdb_url(workload.id, password, workload=workload)
            splits = zdb_url.split("@")
            zdb_dict = {"address": splits[1], "namespace": splits[0].split(":")[0], "password": password}
            cluster_zdb_configs.append(zdb_dict)

        if not cluster_zdb_configs:
            j.logger.error(
                f"AUTO_TOPUP: can't retrive zdb config of s3 solution {sol_dict['Name']} because of invalid zdb metadata"
            )
            raise j.exceptions.Runtime(
                f"AUTO_TOPUP: can't retrive zdb config of s3 solution {sol_dict['Name']} because of invalid zdb metadata"
            )

        return cluster_zdb_configs


def _parse_zerostor_metric(line):
    splits = line.split()
    if len(splits) > 2:
        raise j.exceptions.Validation(f"AUTO TOPUP: invalid zerostor data size metric length {line}")
    zdb, size = splits[0], splits[1]
    pattern = 'namespace="(.*?)-1'
    zdb_wid = re.search(pattern, zdb).group(1)
    return zdb_wid, size


def fetch_zero_stor_metrics(url, bearer_token=None):
    headers = {}
    if bearer_token:
        headers = {"name": "Authorization", "content": f"Bearer {bearer_token}"}
    url = urljoin(url, "/minio/prometheus/metrics")
    metrics_response = http.get(url, headers=headers)
    metrics_response.raise_for_status()
    zdb_stats = defaultdict(list)
    for line in metrics_response.text.splitlines():
        for key, val in METRIC_KEYS.items():
            if line.startswith(val):
                zdb_stats[key].append(line[len(val) :])
    zdbs = defaultdict(dict)
    for stat in zdb_stats["free"]:
        zdb, size = _parse_zerostor_metric(stat)
        zdbs[zdb]["free"] = float(size)
    for stat in zdb_stats["used"]:
        zdb, size = _parse_zerostor_metric(stat)
        zdbs[zdb]["used"] = float(size)
    return zdbs


def check_s3_utilization(url, threshold=0.7, clear_threshold=0.4, max_storage=None, bearer_token=None):
    """
    Args:
        clear_threshold: the required utilization after extension # TODO: choose a better a name
    return utilization ratio, required capacity to add in GB
    """
    max_storage = max_storage * (1024 ** 3)
    used_storage = 0
    total_storage = 0
    zdbs_usage = fetch_zero_stor_metrics(url, bearer_token)
    for zdb_wid, usage in zdbs_usage.items():
        free_space = (
            usage["free"] / 1024
        )  # TODO: remove when zerostor metrics are fixed (https://github.com/threefoldtech/minio/issues/124)
        used_space = (
            usage["used"] / 1024
        )  # TODO: remove when zerostor metrics are fixed (https://github.com/threefoldtech/minio/issues/124)
        used_storage += used_space
        total_storage += used_space + free_space
        zdb_utilization = float(used_space / (free_space + used_space))
        j.logger.info(f"AUTO TOPUP: zdb {zdb_wid} utilization is {zdb_utilization} trigger: {threshold}")
    if max_storage and total_storage >= max_storage:
        j.logger.warning(f"AUTO TOPUP: maximum storage capacity has been reached. skipping extension")
        return 0, 0

    disk_utilization = used_storage / total_storage

    if disk_utilization < threshold:
        return disk_utilization, 0

    required_capacity = (used_storage / clear_threshold) - total_storage

    j.logger.info(
        f"AUTO TOPUP: zdbs disk reached utilization: {disk_utilization} required capacity: {required_capacity}"
    )

    if required_capacity + total_storage > max_storage:
        required_capacity = max_storage - total_storage

    return disk_utilization, (required_capacity / (1024 ** 3))


def extend_zdbs(
    name, pool_ids, solution_uuid, password, duration, size=10, wallet_name=None, nodes_ids=None, disk_type=DiskType.HDD
):
    """
    1- create/extend pools with enough cloud units for the new zdbs
    2- deploy a zdb with the same size and password for each wid
    3- build the newly installed zdbs config
    4- return wids, password

    """
    description = j.data.serializers.json.dumps({"vdc_uuid": solution_uuid})
    wallet_name = wallet_name or j.core.config.get("S3_AUTO_TOPUP_WALLET")
    wallet = j.clients.stellar.get(wallet_name)
    zos = get_zos()
    reservations = []

    storage_query = {"hru": size}
    if disk_type == DiskType.SSD:
        storage_query = {"sru": size}

    pool_total_sus = defaultdict(int)
    for _, pool_id in enumerate(pool_ids):
        cloud_units = deployer.calculate_capacity_units(**storage_query)
        su = cloud_units.su
        pool_total_sus[pool_id] += su

    for pool_id, su in pool_total_sus.items():
        su = su * duration
        pool_info = zos.pools.extend(pool_id, 0, su, 0)
        j.logger.info(
            f"AUTO TOPUP: extending pool {pool_id} with sus: {su}, reservation_id: {pool_info.reservation_id}"
        )
        zos.billing.payout_farmers(wallet, pool_info)
        reservations.append({"pool_id": pool_id, "reservation_id": pool_info.reservation_id})

    for reservation in reservations:
        if not wait_pool_reservation(reservation["reservation_id"]):
            j.logger.warning(
                f"pool {reservation['pool_id']} extension timedout for reservation: {reservation['reservation_id']}"
            )
            continue

    gs = GlobalScheduler()
    wids = []
    for pool_id in pool_ids:
        nodes_generator = gs.nodes_by_capacity(pool_id=pool_id, ip_version="IPv6", **storage_query)
        if nodes_ids:
            nodes_generator = list(nodes_generator)
            nodes_generator_ids = [node.node_id for node in nodes_generator]
            unavailable_nodes_ids = set(nodes_ids) - set(nodes_generator_ids)
            if unavailable_nodes_ids:
                raise j.exceptions.Validation(
                    f"Some nodes: {unavailable_nodes_ids} are not in the farm or don't have capacity"
                )
            nodes_generator = [node for node in nodes_generator if node.node_id in nodes_ids]
        for node in nodes_generator:
            wid = deployer.deploy_zdb(
                pool_id=pool_id,
                node_id=node.node_id,
                size=size,
                disk_type=disk_type,
                mode=ZDBMode.Seq,
                password=password,
                form_info={"chatflow": "minio"},
                name=name,
                solution_uuid=solution_uuid,
                description=description,
            )
            try:
                success = deployer.wait_workload(wid, cancel_by_uuid=False)
                if not success:
                    raise DeploymentFailed()
                wids.append(wid)
                j.logger.info(f"AUTO TOPUP: ZDB workload {wid} deployed successfully")
                break
            except DeploymentFailed:
                j.logger.error(f"AUTO TOPUP: ZDB workload {wid} failed to deploy")
                continue
    return wids, password


def get_zdb_farms_distribution(solution_uuid, farm_names, required_len):
    """
    get a farm distribution based on the total used storage of each farm
    """
    zdb_workloads = [
        workload
        for workload in solutions.get_workloads_by_uuid(solution_uuid)
        if workload.info.workload_type == WorkloadType.Zdb
    ]
    pool_farm_name = {}
    farm_used_storage = {farm_name: 1 for farm_name in farm_names}
    for workload in zdb_workloads:
        farm_name = pool_farm_name.get(workload.info.pool_id)
        if not farm_name:
            farm_id = deployer.get_pool_farm_id(workload.info.pool_id)
            farm_name = deployer._explorer.farms.get(farm_id).name
            pool_farm_name[workload.info.pool_id] = farm_name
        if farm_name in farm_names:
            farm_used_storage[farm_name] += workload.size

    """
    1- use total storage / farm_storage as weight for each farm
    2- do wieghted random choices
    """
    farm_weights = {}
    total_Storage = sum(farm_used_storage.values())
    for farm_name, used_storage in farm_used_storage.items():
        farm_weights[farm_name] = total_Storage / used_storage

    return random.choices(list(farm_weights.keys()), list(farm_weights.values()), k=required_len)


def get_farm_pool_id(farm_name):
    """
    returns a pool_id associated on the farm or create an empty pool and return its id
    """
    zos = get_zos()
    for pool in zos.pools.list():
        farm_id = deployer.get_pool_farm_id(pool.pool_id, pool)
        pool_farm_name = zos._explorer.farms.get(farm_id).name
        if farm_name == pool_farm_name:
            return pool.pool_id
    pool_info = zos.pools.create(0, 0, 0, farm_name)
    return pool_info.reservation_id


def wait_pool_payment(pool_id, exp=5, trigger_cus=0, trigger_sus=1):
    zos = get_zos()
    expiration = j.data.time.now().timestamp + exp * 60
    while j.data.time.get().timestamp < expiration:
        pool = zos.pools.get(pool_id)
        if pool.cus >= trigger_cus and pool.sus >= trigger_sus:
            return True
        gevent.sleep(2)
    return False


def wait_pool_reservation(reservation_id, exp=5):
    zos = get_zos()
    expiration = j.data.time.now().timestamp + exp * 60
    while j.data.time.get().timestamp < expiration:
        payment_info = zos.pools.get_payment_info(reservation_id)
        if payment_info.paid and payment_info.released:
            return True
        gevent.sleep(2)
    return False
