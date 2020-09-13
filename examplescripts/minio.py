from jumpscale.loader import j
from time import sleep
import random
import uuid


zos = j.sals.zos

FREEFARM_ID = 71
MAZR3A_ID = 13619
DATA_NODES = 2
PARITY_NODES = 1
ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
PASSWORD = "super secure passowrd"
network_name = str(uuid.uuid4())


def wait_workload(wid):
    workload = zos.workloads.get(wid)
    while not workload.info.result.workload_id:
        sleep(1)
        workload = zos.workloads.get(wid)


def wait_workloads(wids):
    for wid in wids:
        wait_workload(wid)


def create_pool(cus=100, sus=100, farm="freefarm"):
    payment_detail = zos.pools.create(cu=cus, su=sus, farm=farm, currencies=["TFT"])
    print(payment_detail)
    wallet = j.clients.stellar.get("wallet")
    zos.billing.payout_farmers(wallet, payment_detail)
    pool = zos.pools.get(payment_detail.reservation_id)
    while pool.cus == 0:
        pool = zos.pools.get(payment_detail.reservation_id)
        sleep(1)
    return pool


def create_network(network_name, pool):
    ip_range = "172.19.0.0/16"

    network = zos.network.create(ip_range, network_name)
    nodes = zos.nodes_finder.nodes_by_capacity()
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


def deploy_zdbs(nodes, freefarm_pool, mazr3a_pool):
    results = []
    for node in nodes:
        pool = freefarm_pool if node.farm_id == FREEFARM_ID else mazr3a_pool
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
        results.append(result_workload)
    return results


def deploy_volume(node_id, pool):
    w_volume = zos.volume.create(node_id, pool.pool_id, size=10, type="SSD")
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


def deploy_minio(node_id, pool, network_name, namespace_config, ip_addr):
    secret_env = {
        "SHARDS": zos.container.encrypt_secret(node_id, ",".join(namespace_config)),
        "SECRET_KEY": zos.container.encrypt_secret(node_id, SECRET_KEY),
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
            "SSH_KEY": j.sals.fs.read_file("/home/omar/id_rsa.pub"),  # OPTIONAL to provide ssh access
            "MINIO_PROMETHEUS_AUTH_TYPE": "public",
        },
        secret_env=secret_env,
    )

    zos.workloads.deploy(minio_container)
    return minio_container


def attach_volume(minio_container, vol_wid):
    zos.volume.attach_existing(container=minio_container, volume_id=f"{vol_wid}-1", mount_point="/data")


freefarm_pool = create_pool(1000, 1000)
mazr3a_pool = create_pool(1000, 1000, "ThreeFold_Mazraa")
network, wg_quick = create_network(network_name, freefarm_pool)
print(wg_quick)


freefarm_nodes = list(filter(j.sals.zos.nodes_finder.filter_is_up, j.sals.zos.nodes_finder.nodes_search(FREEFARM_ID)))
mazr3a_nodes = list(filter(j.sals.zos.nodes_finder.filter_is_up, j.sals.zos.nodes_finder.nodes_search(MAZR3A_ID)))

nodes = freefarm_nodes + mazr3a_nodes
random.shuffle(nodes)
minio_node = nodes[-1]
nodes = nodes[: (DATA_NODES + PARITY_NODES)]
pool_to_pay = freefarm_pool if minio_node.farm_id == FREEFARM_ID else mazr3a_pool
add_node_to_network(network, minio_node.node_id, pool_to_pay, "172.19.3.0/24")
zdb_workloads = deploy_zdbs(nodes, freefarm_pool, mazr3a_pool)
vol_wid = deploy_volume(minio_node.node_id, pool_to_pay)
zdb_wids = [x.id for x in zdb_workloads]
wait_workloads(zdb_wids)
wait_workload(vol_wid)
namespace_config = get_namespace_config(zdb_workloads)

minio_container = deploy_minio(minio_node.node_id, pool_to_pay, network_name, namespace_config, "172.19.3.3")
attach_volume(minio_container, vol_wid)
