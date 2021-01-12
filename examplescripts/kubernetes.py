"""
This is an example script to create a kubernetes cluster and optionally expose it using ZOS sal.

Requirements:
1- stellar wallet named "wallet" funded with enough TFTs

Expected Result:
1- a network named "management" created or extended with the nodes required for kubernetes deployment
2- kubernetes cluster of size 1 with 3 nodes
3- Optional, cluster exposed on the specified domain prefix.

Running the script:
Basic usage is just
```
python kubernetes.py
```

the script is a click cli application. you can view all options using python kubernetes.py --help.
"""

from jumpscale.loader import j
from time import sleep
import netaddr
import uuid
import click
import random
from jumpscale.clients.explorer.models import NextAction, WorkloadType

zos = j.sals.zos.get()
network_name = "management"
size = 1
cluster_secret = "supersecret"


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


def get_ssh_key():
    if not j.sals.fs.exists("/tmp/.ssh"):
        j.core.executors.run_local("mkdir /tmp/.ssh && ssh-keygen -t rsa -f /tmp/.ssh/id_rsa")
    ssh_cl = j.clients.sshkey.get("ubuntu_script")
    ssh_cl.private_key_path = "/tmp/.ssh/id_rsa"
    ssh_cl.load_from_file_system()
    ssh_cl.save()
    return ssh_cl.public_key.rstrip()


def reserve_pool():
    """
    reserve a pool for kubernetes cluster
    """
    payment_detail = zos.pools.create(cu=20000, su=20000, ipv4us=0, farm="freefarm", currencies=["TFT"])
    print(payment_detail)
    if not j.clients.stellar.find("wallet"):
        j.clients.stellar.create_testnet_funded_wallet("wallet")

    wallet = j.clients.stellar.get("wallet")
    txs = zos.billing.payout_farmers(wallet, payment_detail)
    pool = zos.pools.get(payment_detail.reservation_id)
    while True:
        pool = j.sals.zos.get().pools.get(pool.pool_id)
        if pool.cus > 0:
            break
        sleep(5)
    return pool


def deploy_overlay_network(pool):
    """
    deploying kubernetes network and adding nodes to it
    """
    ip_range = "10.100.0.0/16"
    network = zos.network.load_network(network_name)
    if not network:
        network = zos.network.create(ip_range=ip_range, network_name=network_name)
    network_node_ids = set()
    network_used_ranges = set()
    node_ranges = {}
    for resource in network.network_resources:
        node_ranges[resource.info.node_id] = resource.iprange
        network_node_ids.add(resource.info.node_id)
        network_used_ranges.add(resource.iprange)
        for peer in resource.peers:
            network_used_ranges.add(peer.iprange)
    pool_nodes = list(zos.nodes_finder.nodes_by_capacity(pool_id=pool.pool_id))
    for node in filter(zos.nodes_finder.filter_public_ip4, pool_nodes):
        if zos.nodes_finder.filter_is_up(node):
            access_node = node
            break
    else:
        raise Exception("can not find a node with ipv4 that can be used as access node for the cluster")

    if not network_node_ids:
        iprange = "10.100.0.0/24"
        zos.network.add_node(network, access_node.node_id, iprange, pool.pool_id)

        # adding wiregaurd access through a node that has ipv4
        wg_quick = zos.network.add_access(network, access_node.node_id, "10.100.1.0/24", ipv4=True)
        network_used_ranges.add("10.100.0.0/24")
        network_used_ranges.add("10.100.1.0/24")
        print(wg_quick)
        with open("kube.conf", "w") as f:
            f.writelines(wg_quick)

        for workload in network.network_resources:
            wid = zos.workloads.deploy(workload)
            workload = zos.workloads.get(wid)
            while not workload.info.result.workload_id:
                sleep(1)
                workload = zos.workloads.get(wid)

    nodes = []
    random.shuffle(pool_nodes)
    for _, node in enumerate(pool_nodes):
        if node.node_id == "3dAnxcykEDgKVQdTRKmktggL2MZbm3CPSdS9Tdoy4HAF":
            continue
        if not zos.nodes_finder.filter_is_up(node) or node.node_id == access_node.node_id:
            continue

        if node.node_id in network_node_ids:
            nodes.append({"id": node.node_id, "ip_range": node_ranges[node.node_id]})
            continue

        network_range = netaddr.IPNetwork("10.100.0.0/16")
        for _, subnet in enumerate(network_range.subnet(24)):
            iprange = str(subnet)
            if iprange in network_used_ranges:
                continue

            zos.network.add_node(network, node.node_id, iprange, pool.pool_id)
            nodes.append({"id": node.node_id, "ip_range": iprange})
            network_used_ranges.add(iprange)
            break
        else:
            raise j.exceptions.Runtime(f"can't find free subnets in network {network_name}")
        if len(nodes) == 3:
            break

    # Deploy the network
    node_workloads = {}
    for workload in network.network_resources:
        node_workloads[workload.info.node_id] = workload

    wids = []
    for workload in node_workloads.values():
        wid = zos.workloads.deploy(workload)
        wids.append(wid)

    for wid in wids:
        if not wait_workload(wid):
            raise Exception(f"Failed to deploy network for kubernetes, Workload ID: {wid}")

    return nodes


def get_node_free_ip(ip_range):
    """
    get a node free ip, skips the first ip as it is assigned to the network
    """
    hosts = netaddr.IPNetwork(ip_range).iter_hosts()
    next(hosts)
    return str(next(hosts))  # skip ip used by node


def deploy_k8s_master(
    cluster, node, pool_id,
):
    """
    deploying kubernets master node
    """
    print(f"deploying kubernetes master on node: {node['id']}, iprange: {node['ip_range']}")
    network = zos.network.load_network(network_name)
    master = zos.kubernetes.add_master(
        node_id=node["id"],  # node_id to make the capacity reservation on and deploy the Flist
        network_name=network_name,  # network_name deployed on the node (node could have multiple private networks)
        cluster_secret=cluster_secret,  # cluster pasword
        ip_address=get_free_ip(network, node["id"]),  # IP address of the node
        size=size,  # 1 (1 logical core, 2GB of memory) or 2 (2 logical cores and 4GB of memory)
        ssh_keys=[get_ssh_key()],  # ssh public key providing ssh access to master of worker vm's
        pool_id=pool_id,
    )
    cluster.append(master)
    return master


def deploy_k8s_workers(cluster, master, nodes, pool_id):
    """
    deploying kubernets worker nodes
    """
    network = zos.network.load_network(network_name)
    workloads = zos.workloads.list(j.core.identity.me.tid)
    for node in nodes:
        print(f"deploying kubernetes worker on node: {node['id']}, iprange: {node['ip_range']}")
        worker = zos.kubernetes.add_worker(
            node_id=node["id"],
            network_name=network_name,
            cluster_secret=cluster_secret,
            ip_address=get_free_ip(network, node["id"], workloads),
            size=size,
            master_ip=master.ipaddress,
            ssh_keys=[get_ssh_key()],
            pool_id=pool_id,
        )
        cluster.append(worker)


def wait_workload(workload_id, expiry=10):
    expiry = expiry or 10
    expiration_provisioning = j.data.time.now().timestamp + expiry * 60
    # wait for workload
    while True:
        workload = zos.workloads.get(workload_id)
        if workload.info.result.workload_id:
            success = workload.info.result.state.value == 1
            if not success:
                error_message = workload.info.result.message
                msg = f"Workload {workload.id} failed to deploy due to error {error_message}. For more details: {j.core.identity.me.explorer_url}/reservations/workloads/{workload.id}"
                print(msg)
            return success
        if expiration_provisioning < j.data.time.get().timestamp:
            j.sals.reservation_chatflow.solutions.cancel_solution([workload_id])
        sleep(2)
    return False


def deploy_k8s_cluster(nodes, pool_id):
    """
    deploying kubernets cluster(master and workers nodes)
    """
    cluster = []
    master = deploy_k8s_master(cluster, nodes[0], pool_id)
    deploy_k8s_workers(cluster, master, nodes[1:3], pool_id)

    for w in cluster:
        wid = zos.workloads.deploy(w)

        if not wait_workload(wid):
            raise Exception(f"Faild to deploy workload: {wid}")
    print(f"you can now ssh to master node using 'ssh rancher@{master.ipaddress}'")
    return master


@click.command()
@click.option(
    "--domain-prefix", default="kubernetes-demo", help="domain prefix you want to use, will be ignored if not exposed"
)
@click.option("--expose", is_flag=True, help="do you want to expose kubernetes on a domain or not")
def deploy(expose, domain_prefix):
    """
    deploy all stuff needed for a kubernetes cluster
    """
    pool = reserve_pool()
    nodes = deploy_overlay_network(pool)
    master = deploy_k8s_cluster(nodes, pool.pool_id)
    if expose:
        expose_cluster(pool, domain_prefix, nodes[0], master.ipaddress)
    print("DONE")


def get_gateway(pool):
    gateway_ids = {g.node_id: g for g in zos.gateways_finder.gateways_search() if zos.nodes_finder.filter_is_up(g)}
    for gid, g in gateway_ids.items():
        if gid in pool.node_ids:
            if not g.dns_nameserver:
                continue
            return g
    else:
        raise j.exceptions.NotFound("can not find any available gateways")


def add_subdomain(subdomain, gateway, pool):
    domain = gateway.managed_domains[0]
    subdomain = f"{subdomain}.{domain}"
    gateway_ips = []
    for ns in gateway.dns_nameserver:
        gateway_ips.append(j.sals.nettools.get_host_by_name(ns))
    subdomain_wl = zos.gateway.sub_domain(gateway.node_id, subdomain, gateway_ips, pool.pool_id)
    wid = zos.workloads.deploy(subdomain_wl)
    wait_workload(wid)
    return gateway_ips, subdomain


def deploy_tcp_router(gateway, pool, subdomain, gateway_ips, network_name, node, ip):
    SECRET = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"
    reverse_proxy = zos.gateway.tcp_proxy_reverse(gateway.node_id, subdomain, SECRET, pool.pool_id)
    wid = zos.workloads.deploy(reverse_proxy)
    wait_workload(wid)
    SOLUTION_IP_ADDRESS = ip
    SOLUTION_PORT = 30080
    SOLUTION_TLS_PORT = 30443
    GATEWAY_IP = gateway_ips[0]

    entrypoint = (
        f"/bin/trc -local {SOLUTION_IP_ADDRESS}:{SOLUTION_PORT} -local-tls {SOLUTION_IP_ADDRESS}:{SOLUTION_TLS_PORT}"
        f" -remote {GATEWAY_IP}:{gateway.tcp_router_port}"
    )

    # trc container deployment
    NODE_ID = node["id"]
    FLIST_URL = "https://hub.grid.tf/tf-official-apps/tcprouter:latest.flist"
    CONTAINER_IP_ADDRESS = get_free_ip(zos.network.load_network(network_name), NODE_ID)
    secret_env = {"TRC_SECRET": zos.container.encrypt_secret(NODE_ID, SECRET)}
    container = zos.container.create(
        node_id=NODE_ID,
        network_name=network_name,
        ip_address=CONTAINER_IP_ADDRESS,
        flist=FLIST_URL,
        capacity_pool_id=pool.pool_id,
        entrypoint=entrypoint,
        secret_env=secret_env,
    )
    wid = zos.workloads.deploy(container)


def expose_cluster(pool, subdomain_prefix, node, ip):
    gateway = get_gateway(pool)
    gateway_ips, subdomain = add_subdomain(subdomain_prefix, gateway, pool)
    deploy_tcp_router(gateway, pool, subdomain, gateway_ips, network_name, node, ip)
    print(subdomain)


if __name__ == "__main__":
    deploy()
