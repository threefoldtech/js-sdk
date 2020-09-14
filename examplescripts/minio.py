from jumpscale.loader import j
from time import sleep
import random
import uuid
import os

zos = j.sals.zos

FREEFARM_ID = 71
MAZR3A_ID = 13619
DATA_NODES = 7
PARITY_NODES = 3
ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
PASSWORD = "supersecurepassowrd"
network_name = str(uuid.uuid4())
BAD_NODES = set(["3dAnxcykEDgKVQdTRKmktggL2MZbm3CPSdS9Tdoy4HAF"])
UP_FOR = 60 * 30  # number of seconds
### FOR TESTING
fp = [2044, 2036, 2031, 2015, 1985, 1982, 1979, 1958, 1957, 195]
mp = [1966, 1977, 1980, 1983, 1986, 1990, 2016, 2032, 2037, 2045]
fp.reverse()
###


def remove_bad_nodes(nodes):
    return list(filter(lambda x: x.node_id not in BAD_NODES, nodes))


def wait_workload(wid):
    workload = zos.workloads.get(wid)
    while not workload.info.result.workload_id:
        sleep(1)
        workload = zos.workloads.get(wid)


def wait_pools(pools):
    for pool in pools:
        while pool.cus == 0:
            pool = get_pool(pool.pool_id)
            sleep(1)


def wait_workloads(wids):
    for wid in wids:
        wait_workload(wid)


def create_pool(cus=100, sus=100, farm="freefarm", wait=True):
    # ### FOR TESTING
    # if farm == "freefarm":
    #     return zos.pools.get(fp.pop(-1))
    # else:
    #     return zos.pools.get(mp.pop(-1))
    # ###
    payment_detail = zos.pools.create(cu=cus, su=sus, farm=farm, currencies=["TFT"])
    wallet = j.clients.stellar.get("wallet")
    zos.billing.payout_farmers(wallet, payment_detail)
    pool = get_pool(payment_detail.reservation_id)
    if wait:
        wait_pools([pool])
    return pool


def get_pool(pid):
    return zos.pools.get(pid)


def create_zdb_pools(nodes):
    pools = []
    for node in nodes:
        if node.farm_id == FREEFARM_ID:
            pools.append(create_pool(10, UP_FOR * 0.0416, "freefarm", wait=False))
        else:
            pools.append(create_pool(10, UP_FOR * 0.0416, "ThreeFold_Mazraa", wait=False))
    wait_pools(pools)
    return pools


def create_network(network_name, pool, farm_id):
    ip_range = "172.19.0.0/16"

    network = zos.network.create(ip_range, network_name)
    nodes = zos.nodes_finder.nodes_search(farm_id)
    access_node = list(filter(zos.nodes_finder.filter_public_ip4, nodes))[0]
    zos.network.add_node(network, access_node.node_id, "172.19.1.0/24", pool.pool_id)
    wg_quick = zos.network.add_access(network, access_node.node_id, "172.19.2.0/24", ipv4=True)

    for workload in network.network_resources:
        wid = zos.workloads.deploy(workload)
        workload = zos.workloads.get(wid)
        while not workload.info.result.workload_id:
            sleep(1)
            workload = zos.workloads.get(wid)
    return network, wg_quick


def add_node_to_network(network, node_id, pool, iprange):
    zos.network.add_node(network, node_id, iprange, pool.pool_id)
    for workload in network.network_resources:
        wid = zos.workloads.deploy(workload)
        workload = zos.workloads.get(wid)
        while not workload.info.result.workload_id:
            sleep(1)
            workload = zos.workloads.get(wid)


def deploy_zdb(node, pool):
    w_zdb = zos.zdb.create(
        node_id=node.node_id,
        size=10,
        mode=0,  # seq
        password=PASSWORD,
        pool_id=pool.pool_id,
        disk_type=1,  # SSD=1, HDD=0
        public=False,
    )
    id = zos.workloads.deploy(w_zdb)
    result_workload = zos.workloads.get(id)
    return result_workload


def deploy_zdbs(nodes, pools):
    results = []
    for i, node in enumerate(nodes):
        results.append(deploy_zdb(node, pools[i]))
    return results


def deploy_volume(node_id, pool):
    w_volume = zos.volume.create(node_id, pool.pool_id, size=5, type="SSD")
    return zos.workloads.deploy(w_volume)


def get_namespace_config(wids):
    namespace_config = []
    for result in wids:
        workload = zos.workloads.get(result.id)
        data = j.data.serializers.json.loads(workload.info.result.data_json)
        if data.get("IP"):
            ip = data["IP"]
        elif data.get("IPs"):
            ip = data["IPs"][0]
        else:
            raise j.exceptions.RuntimeError("missing IP field in the 0-DB result")
        cfg = f"{data['Namespace']}:{PASSWORD}@[{ip}]:{data['Port']}"
        namespace_config.append(cfg)
    return namespace_config


def deploy_master_minio(node_id, pool, network_name, namespace_config, tlog_node_namespace, ip_addr):
    secret_env = {
        "SHARDS": zos.container.encrypt_secret(node_id, ",".join(namespace_config)),
        "SECRET_KEY": zos.container.encrypt_secret(node_id, SECRET_KEY),
        "TLOG": zos.container.encrypt_secret(node_id, tlog_node_namespace),
    }

    # Make sure to adjust the node_id and network name to the appropriate in copy / paste mode :-)
    minio_container = zos.container.create(
        node_id=node_id,
        network_name=network_name,
        ip_address=ip_addr,
        flist="https://hub.grid.tf/tf-official-apps/minio:latest.flist",
        capacity_pool_id=pool.pool_id,
        interactive=False,
        entrypoint="",
        cpu=2,
        memory=2048,
        env={
            "DATA": str(DATA_NODES),
            "PARITY": str(PARITY_NODES),
            "ACCESS_KEY": ACCESS_KEY,
            "SSH_KEY": j.sals.fs.read_file(os.path.expanduser("~/.ssh/id_rsa.pub")),  # OPTIONAL to provide ssh access
            "MINIO_PROMETHEUS_AUTH_TYPE": "public",
        },
        secret_env=secret_env,
    )

    zos.workloads.deploy(minio_container)
    return minio_container


def deploy_backup_minio(node_id, pool, network_name, namespace_config, tlog_node_namespace, ip_addr):
    secret_env = {
        "SHARDS": zos.container.encrypt_secret(node_id, ",".join(namespace_config)),
        "SECRET_KEY": zos.container.encrypt_secret(node_id, SECRET_KEY),
        "MASTER": zos.container.encrypt_secret(node_id, tlog_node_namespace),
    }

    # Make sure to adjust the node_id and network name to the appropriate in copy / paste mode :-)
    minio_container = zos.container.create(
        node_id=node_id,
        network_name=network_name,
        ip_address=ip_addr,
        flist="https://hub.grid.tf/tf-official-apps/minio:latest.flist",
        capacity_pool_id=pool.pool_id,
        interactive=False,
        entrypoint="",
        cpu=2,
        memory=2048,
        env={
            "DATA": str(DATA_NODES),
            "PARITY": str(PARITY_NODES),
            "ACCESS_KEY": ACCESS_KEY,
            "SSH_KEY": j.sals.fs.read_file(os.path.expanduser("~/.ssh/id_rsa.pub")),  # OPTIONAL to provide ssh access
            "MINIO_PROMETHEUS_AUTH_TYPE": "public",
        },
        secret_env=secret_env,
    )

    zos.workloads.deploy(minio_container)
    return minio_container


def attach_volume(minio_container, vol_wid):
    zos.volume.attach_existing(container=minio_container, volume_id=f"{vol_wid}-1", mount_point="/data")


freefarm_nodes = list(filter(j.sals.zos.nodes_finder.filter_is_up, j.sals.zos.nodes_finder.nodes_search(FREEFARM_ID)))
mazr3a_nodes = list(filter(j.sals.zos.nodes_finder.filter_is_up, j.sals.zos.nodes_finder.nodes_search(MAZR3A_ID)))

nodes = freefarm_nodes + mazr3a_nodes
random.shuffle(nodes)
nodes = remove_bad_nodes(nodes)
minio_master_node = nodes[-1]
minio_backup_node = nodes[-2]
tlog_node = nodes[(DATA_NODES + PARITY_NODES)]

if len(nodes) < 10:
    print("Not enough nodes to deploy the zdbs")

nodes = nodes[: (DATA_NODES + PARITY_NODES)]
master_pool = (
    create_pool(UP_FOR * 0.25, UP_FOR * 0.043, "freefarm")
    if minio_master_node.farm_id == FREEFARM_ID
    else create_pool(UP_FOR * 0.25, UP_FOR * 0.043, "ThreeFold_Mazraa")
)
backup_pool = (
    create_pool(UP_FOR * 0.25, UP_FOR * 0.043, "freefarm")
    if minio_backup_node.farm_id == FREEFARM_ID
    else create_pool(UP_FOR * 0.25, UP_FOR * 0.043, "ThreeFold_Mazraa")
)
tlog_pool = (
    create_pool(10, UP_FOR * 0.0416, "freefarm")
    if tlog_node.farm_id == FREEFARM_ID
    else create_pool(10, UP_FOR * 0.0416, "ThreeFold_Mazraa")
)
pools = create_zdb_pools(nodes)
network, wg_quick = create_network(network_name, master_pool, minio_master_node.farm_id)
print(wg_quick)


add_node_to_network(network, minio_master_node.node_id, master_pool, "172.19.3.0/24")
add_node_to_network(network, minio_backup_node.node_id, backup_pool, "172.19.4.0/24")
zdb_workloads = deploy_zdbs(nodes, pools)
tlog_workload = deploy_zdb(tlog_node, tlog_pool)
master_vol_id = deploy_volume(minio_master_node.node_id, master_pool)
backup_vol_id = deploy_volume(minio_backup_node.node_id, backup_pool)
zdb_wids = [x.id for x in zdb_workloads]
wait_workloads(zdb_wids)
wait_workload(tlog_workload.id)
wait_workload(master_vol_id)
wait_workload(backup_vol_id)
namespace_config = get_namespace_config(zdb_workloads)
tlog_namespace = get_namespace_config([tlog_workload])[0]
master_ip_address = "172.19.3.3"
backup_ip_address = "172.19.4.4"
minio_master_container = deploy_master_minio(
    minio_master_node.node_id, master_pool, network_name, namespace_config, tlog_namespace, master_ip_address
)
minio_backup_container = deploy_backup_minio(
    minio_backup_node.node_id, backup_pool, network_name, namespace_config, tlog_namespace, backup_ip_address
)
attach_volume(minio_master_container, master_vol_id)
attach_volume(minio_backup_container, backup_vol_id)


print(
    f"""
Finished successfully. After adding the network using
the wireguard config printed above, minio can be accessed on
http://{master_ip_address}:9000
Backed up on:
http://{backup_ip_address}:9000
"""
)
