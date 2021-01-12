"""
This is an example script to create a minio cluster and test haigh availability by shutting down and replacing both ZDB and minio containers.

Requirements:
1- stellar wallet named "wallet" funded with enough TFTs

Expected Result:
1- a network named "management" created or extended with the nodes required for minio deployment
2- minio cluster (primary/secondary) with 7 data nodes and 3 parity nodes.

Running the script:
```
python minio.py
```

you will get prompted for each test phase to validate what's happening and continue the execution.
"""


from jumpscale.loader import j
from time import sleep
import random
import os
import random
import netaddr
from jumpscale.clients.explorer.models import NextAction, WorkloadType, State
import math

zos = j.sals.zos.get()

FREEFARM_ID = 71
MAZR3A_ID = 13619
DATA_NODES = 7
PARITY_NODES = 3
TO_KILL = 3
ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
PASSWORD = "supersecurepassowrd"
network_name = "management"
print(f"network name: {network_name}")
BAD_NODES = set([])
UP_FOR = 60 * 20  # number of seconds


def get_free_ip(network, node_id, workloads=None):
    workloads = workloads or zos.workloads.list(j.core.identity.me.tid)
    used_ips = set()
    for workload in workloads:
        if workload.info.node_id != node_id:
            continue
        if workload.info.next_action != NextAction.DEPLOY:
            continue
        if workload.info.workload_type == WorkloadType.Kubernetes:
            if workload.network_id == network.name:
                used_ips.add(workload.ipaddress)
        elif workload.info.workload_type == WorkloadType.Container:
            for conn in workload.network_connection:
                if conn.network_id == network.name:
                    used_ips.add(conn.ipaddress)
    node_range = None
    for resource in network.network_resources:
        if resource.info.node_id == node_id:
            node_range = resource.iprange
            break

    hosts = netaddr.IPNetwork(node_range).iter_hosts()
    next(hosts)  # skip ip used by node
    for host in hosts:
        ip = str(host)
        if ip not in used_ips:
            used_ips.add(ip)
            return ip
    return None


def wait_site_up(url):
    up = False
    while not up:
        try:
            code = j.tools.http.get(url, timeout=1).status_code
            up = code == 200
        except Exception:
            pass
        sleep(1)


def wait_site_down(url):
    down = False
    while not down:
        try:
            code = j.tools.http.get(url, timeout=1).status_code
            down = code != 200
        except Exception:
            down = True
        sleep(1)


def remove_bad_nodes(nodes):
    return list(filter(lambda x: x.node_id not in BAD_NODES, nodes))


def wait_workload(wid):
    workload = zos.workloads.get(wid)
    timeout = j.data.time.now().timestamp + 15 * 60 * 60
    while not workload.info.result.state.value:
        if j.data.time.now().timestamp > timeout:
            raise j.exceptions.Runtime(f"workload {wid} failed to deploy in time")
        sleep(1)
        workload = zos.workloads.get(wid)
    if workload.info.result.state != State.Ok:
        raise j.exceptions.Runtime(f"workload {wid} failed due to {workload.info.result.message}")


def wait_zdb_workloads(zdb_wids):
    # Looks like the workload_id can be set before the namespace
    timeout = j.data.time.now().timestamp + 15 * 60 * 60
    for wid in zdb_wids:
        if j.data.time.now().timestamp > timeout:
            raise j.exceptions.Runtime(f"workload {wid} failed to deploy in time")
        workload = zos.workloads.get(wid)
        data = j.data.serializers.json.loads(workload.info.result.data_json)
        if workload.info.result.message:
            x = workload.info.result.message
            raise Exception(f"Failed to initialize ZDB: {x}")
        elif data.get("IP") or data.get("IPs"):
            return
        else:
            sleep(1)
            continue


def wait_pools(pools):
    for pool in pools:
        while pool.cus == 0:
            pool = get_pool(pool.pool_id)
            sleep(1)


def wait_workloads(wids):
    for wid in wids:
        wait_workload(wid)


def create_pool(cus=100, sus=100, farm="freefarm", wait=True):
    cus = math.ceil(cus)
    sus = math.ceil(sus)
    payment_detail = zos.pools.create(cu=cus, su=sus, ipv4us=0, farm=farm, currencies=["TFT"])
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
    network = zos.network.load_network(network_name)
    if network:
        return network, None
    ip_range = "10.100.0.0/16"
    network = zos.network.create(ip_range, network_name)
    nodes = zos.nodes_finder.nodes_search(farm_id)
    access_node = list(filter(zos.nodes_finder.filter_public_ip4, nodes))[0]
    zos.network.add_node(network, access_node.node_id, "10.100.0.0/24", pool.pool_id)
    wg_quick = zos.network.add_access(network, access_node.node_id, "10.100.1.0/24", ipv4=True)

    for workload in network.network_resources:
        timeout = j.data.time.now().timestamp + 15 * 60 * 60
        wid = zos.workloads.deploy(workload)
        workload = zos.workloads.get(wid)
        while not workload.info.result.workload_id:
            if j.data.time.now().timestamp > timeout:
                raise j.exceptions.Runtime(f"workload {wid} failed to deploy in time")
            sleep(1)
            workload = zos.workloads.get(wid)
    with open("minio.conf", "w") as f:
        f.write(wg_quick)
    return network, wg_quick


def add_node_to_network(network, node_id, pool, iprange):
    zos.network.add_node(network, node_id, iprange, pool.pool_id)
    nodes_workloads = {}
    for workload in network.network_resources:
        nodes_workloads[workload.info.node_id] = workload

    wids = []
    for workload in nodes_workloads.values():
        wid = zos.workloads.deploy(workload)
        wids.append(wid)
        print(wid)
    for wid in wids:
        timeout = j.data.time.now().timestamp + 7 * 60 * 60
        workload = zos.workloads.get(wid)
        while not workload.info.result.workload_id:
            if j.data.time.now().timestamp > timeout:
                raise j.exceptions.Runtime(f"workload {wid} timedout")
            sleep(1)
            workload = zos.workloads.get(wid)


def deploy_zdb(node, pool):
    w_zdb = zos.zdb.create(
        node_id=node.node_id,
        size=3,
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
            raise j.exceptions.Runtime(f"missing IP field in the 0-DB result in workload {workload.id}")
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

    wid = zos.workloads.deploy(minio_container)
    return wid, minio_container


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

    wid = zos.workloads.deploy(minio_container)
    return wid, minio_container


def attach_volume(minio_container, vol_wid):
    zos.volume.attach_existing(container=minio_container, volume_id=f"{vol_wid}-1", mount_point="/data")


def pick_minio_nodes(nodes):
    if nodes[-1].farm_id == MAZR3A_ID:
        for node in reversed(nodes):
            if node.node_id == "3dAnxcykEDgKVQdTRKmktggL2MZbm3CPSdS9Tdoy4HAF":
                continue
            if node.farm_id == FREEFARM_ID:
                return node, nodes[-1]
    return nodes[-1], nodes[-2]


freefarm_nodes = list(
    filter(
        j.sals.zos.get().nodes_finder.filter_is_up, j.sals.zos.get().nodes_finder.nodes_by_capacity(FREEFARM_ID, sru=3),
    )
)
mazr3a_nodes = list(
    filter(
        j.sals.zos.get().nodes_finder.filter_is_up, j.sals.zos.get().nodes_finder.nodes_by_capacity(MAZR3A_ID, sru=3),
    )
)

nodes = freefarm_nodes + mazr3a_nodes
random.shuffle(nodes)
nodes = remove_bad_nodes(nodes)
minio_master_node, minio_backup_node = pick_minio_nodes(nodes)


while len(nodes) < (DATA_NODES + PARITY_NODES + TO_KILL + 1):
    nodes.append(random.sample(nodes, 1)[0])

tlog_node = nodes[(DATA_NODES + PARITY_NODES + TO_KILL)]

zdb_later_nodes = nodes[DATA_NODES + PARITY_NODES : DATA_NODES + PARITY_NODES + TO_KILL]
nodes = nodes[: (DATA_NODES + PARITY_NODES)]
master_pool = (
    create_pool(UP_FOR * 0.25, UP_FOR * 0.043, "freefarm")
    if minio_master_node.farm_id == FREEFARM_ID
    else create_pool(UP_FOR * 0.25, UP_FOR * 0.043, "ThreeFold_Mazraa")
)

network, wg_quick = create_network(network_name, master_pool, minio_master_node.farm_id)
print(wg_quick)

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


network_used_ranges = set()
network_node_ids = set()
for resource in network.network_resources:
    network_used_ranges.add(resource.iprange)
    network_node_ids.add(resource.info.node_id)
    for peer in resource.peers:
        network_used_ranges.add(peer.iprange)

network_range = netaddr.IPNetwork("10.100.0.0/16")
node_ids = [minio_master_node.node_id, minio_backup_node.node_id]
minio_pools = [master_pool, backup_pool]

for idx, node_id in enumerate(node_ids):
    if node_id in network_node_ids:
        continue
    for _, subnet in enumerate(network_range.subnet(24)):
        subnet = str(subnet)
        if subnet in network_used_ranges:
            continue
        add_node_to_network(network, node_id, minio_pools[idx], subnet)
        network_node_ids.add(node_id)
        network_used_ranges.add(subnet)
        network = zos.network.load_network(network_name)
        break

zdb_workloads = deploy_zdbs(nodes, pools)
tlog_workload = deploy_zdb(tlog_node, tlog_pool)
master_vol_id = deploy_volume(minio_master_node.node_id, master_pool)
backup_vol_id = deploy_volume(minio_backup_node.node_id, backup_pool)
zdb_wids = [x.id for x in zdb_workloads]
wait_workloads(zdb_wids)
wait_zdb_workloads(zdb_wids)
wait_workloads([tlog_workload.id])
wait_zdb_workloads([tlog_workload.id])
wait_workload(master_vol_id)
wait_workload(backup_vol_id)
namespace_config = get_namespace_config(zdb_workloads)
tlog_namespace = get_namespace_config([tlog_workload])[0]
master_ip_address = get_free_ip(network, minio_master_node.node_id)
master_wid, minio_master_container = deploy_master_minio(
    minio_master_node.node_id, master_pool, network_name, namespace_config, tlog_namespace, master_ip_address
)
backup_ip_address = get_free_ip(network, minio_backup_node.node_id)
backup_wid, minio_backup_container = deploy_backup_minio(
    minio_backup_node.node_id, backup_pool, network_name, namespace_config, tlog_namespace, backup_ip_address
)
attach_volume(minio_master_container, master_vol_id)
attach_volume(minio_backup_container, backup_vol_id)


print(
    f"""
Finished successfully. After adding the network using
the wireguard config printed above, minio can be accessed on
http://{master_ip_address}:9000
Slave up on:
http://{backup_ip_address}:9000
"""
)


input(
    """Make sure that the master and slave are accessible and play around with s3fs and restic to make sure they behave as expected,
maybe add prometheus or grafana to ensure that there's no down time then press enter to continue to the second phase where redunduncy is checked"""
)

to_die = random.sample(range(0, 10), TO_KILL)

zdb_new_pools = create_zdb_pools(zdb_later_nodes)
zdb_new_workloads = deploy_zdbs(zdb_later_nodes, zdb_new_pools)
zdb_new_wids = [x.id for x in zdb_new_workloads]
wait_workloads(zdb_new_wids)
wait_zdb_workloads(zdb_new_wids)
new_namespace_config = get_namespace_config(zdb_new_workloads)

print("Removing three backup storages")
for i, idx in enumerate(to_die):
    zos.workloads.decomission(zdb_workloads[idx].id)
    namespace_config[idx] = new_namespace_config[i]

input("Removed, make sure that the system is still intact (read-only), then press enter")

print("Removing master node")
zos.workloads.decomission(master_wid)
input("Removed the master check that the slave is still accessible and mountable (read only), then press enter")

print(
    "Removing the slave and redeploying a new master/slave nodes with newly created 3 zdb storages instead of the dead ones"
)


zos.workloads.decomission(backup_wid)
sleep(4 * 60)
master_wid, minio_master_container = deploy_master_minio(
    minio_master_node.node_id, master_pool, network_name, namespace_config, tlog_namespace, master_ip_address
)
wait_workload(master_wid)
backup_wid, minio_backup_container = deploy_backup_minio(
    minio_backup_node.node_id, backup_pool, network_name, namespace_config, tlog_namespace, backup_ip_address
)
wait_workload(backup_wid)
attach_volume(minio_master_container, master_vol_id)
attach_volume(minio_backup_container, backup_vol_id)


print("Recheck, the master/slave printed urls. All should be deployed successfullly")
