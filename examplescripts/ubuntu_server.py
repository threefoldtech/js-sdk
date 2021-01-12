"""
This is an example script to create an ubuntu container with a minimal web service runnng on top of it and expose it over different managed domains (gateways if available).

Requirements:
1- stellar wallet funded with enough TFTs
2- environment varibale `WALLET` with the wallet name defined

Expected Result:
1- a network named "management" created or extended with the nodes required for container deployment
2- ubuntu container exposed over two subdomains
3- failover test for these two domains

Running the script:

```
python ubuntu_server.py
```

you will be prompted to verify the availability of the container over the domain names during the execution
"""


from jumpscale.loader import j
from jumpscale.clients.explorer.models import WorkloadType, NextAction, State
from time import sleep
import uuid
import netaddr
import os

bad_nodes = []
DOMAIN = "mydomain.com"
SUBDOMAIN1 = f"testa.{DOMAIN}"
SUBDOMAIN2 = f"testb.{DOMAIN}"
NETWORK_NAME = "management"
SOLUTION_IP_ADDRESS = None
SOLUTION_PORT = 3001
SOLUTION_TLS_PORT = 443  # not serving https actually, but it must be provided
SECRET = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

zos = j.sals.zos.get()


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


def create_pool(currency="TFT", wallet_name=None):
    wallet_name = wallet_name or os.environ.get("WALLET_NAME")
    if wallet_name is None:
        j.logger.error("Pass WALLET_NAME with the name of the wallet in j.clients.stellar to reserve a pool")
        exit(0)
    payment_detail = zos.pools.create(cu=100, su=100, ipv4us=0, farm="freefarm", currencies=[currency])

    wallet = j.clients.stellar.get(wallet_name)
    zos.billing.payout_farmers(wallet, payment_detail)
    pool = zos.pools.get(payment_detail.reservation_id)
    while pool.cus == 0:
        pool = zos.pools.get(payment_detail.reservation_id)
        sleep(1)

    return pool


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
    with open("ubuntu_server.conf", "w") as f:
        f.write(wg_quick)
    return network, wg_quick


def get_deploymnet_node(pool):
    available_nodes = list(zos.nodes_finder.nodes_by_capacity(cru=0, sru=1, mru=0, pool_id=pool.pool_id))
    available_nodes = [node for node in available_nodes if node.node_id not in bad_nodes]
    return available_nodes[0]


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
        wait_workload(wid)


def get_ssh_key():
    with open(os.path.expanduser("~/.ssh/id_rsa.pub"), "r") as f:
        return f.read()


def deploy_ubuntu_server(node, pool, ssh_key):
    global SOLUTION_IP_ADDRESS
    env = {"pub_key": ssh_key, "DOMAIN": SUBDOMAIN1}
    network = zos.network.load_network(NETWORK_NAME)
    SOLUTION_IP_ADDRESS = get_free_ip(network, node.node_id)
    container = zos.container.create(
        node_id=node.node_id,
        network_name=NETWORK_NAME,
        ip_address=SOLUTION_IP_ADDRESS,
        flist="https://hub.grid.tf/omar0.3bot/omarelawady-k_https_server-latest.flist",
        capacity_pool_id=pool.pool_id,
        cpu=1,
        memory=1024,
        disk_size=1024,
        entrypoint="/usr/local/bin/run_server.sh",
        env=env,
        interactive=False,
    )

    return zos.workloads.deploy(container)


def get_gateways(pool):
    gateway_ids = {g.node_id: g for g in zos.gateways_finder.gateways_search() if zos.nodes_finder.filter_is_up(g)}

    gateways = []
    for gid, g in gateway_ids.items():
        if gid in pool.node_ids:
            if not g.dns_nameserver or g.dns_nameserver == "tf-gateway-prod-05":
                continue
            gateways.append(g)

    if not gateways:
        raise j.exceptions.Input(f"Can't find any gateway")

    if len(gateways) < 2:
        # raise j.exceptions.Input(f"Can't find two gateways")
        return gateways[0], gateways[0]
    return gateways[0], gateways[1]


def create_proxy(node, gateway, pool, ip_address, domain):
    reverse_proxy = zos.gateway.tcp_proxy_reverse(gateway.node_id, domain, SECRET, pool.pool_id)
    wid = zos.workloads.deploy(reverse_proxy)
    gateway_ip = j.sals.nettools.get_host_by_name(gateway.dns_nameserver[0])

    # trc container deployment
    FLIST_URL = "https://hub.grid.tf/tf-official-apps/tcprouter:latest.flist"
    secret_env = {"TRC_SECRET": zos.container.encrypt_secret(node.node_id, SECRET)}

    entrypoint = (
        f"/bin/trc -local {SOLUTION_IP_ADDRESS}:{SOLUTION_PORT} -local-tls {SOLUTION_IP_ADDRESS}:{SOLUTION_TLS_PORT}"
        f" -remote {gateway_ip}:{gateway.tcp_router_port}"
    )

    container = zos.container.create(
        node_id=node.node_id,
        network_name=NETWORK_NAME,
        ip_address=ip_address,
        flist=FLIST_URL,
        capacity_pool_id=pool.pool_id,
        entrypoint=entrypoint,
        secret_env=secret_env,
    )
    wid = zos.workloads.deploy(container)

    return wid


pool = create_pool()
gateway1, gateway2 = get_gateways(pool)
gateway1_ip = j.sals.nettools.get_host_by_name(gateway1.dns_nameserver[0])
gateway2_ip = j.sals.nettools.get_host_by_name(gateway2.dns_nameserver[0])
network, wg_quick = create_network(NETWORK_NAME, pool, zos._explorer.farms.get(farm_name="freefarm").id)

deployment_node = get_deploymnet_node(pool)


network_used_ranges = set()
network_node_ids = set()
for resource in network.network_resources:
    network_used_ranges.add(resource.iprange)
    network_node_ids.add(resource.info.node_id)
    for peer in resource.peers:
        network_used_ranges.add(peer.iprange)

if deployment_node.node_id not in network_node_ids:
    network_range = netaddr.IPNetwork("10.100.0.0/16")
    for _, subnet in enumerate(network_range.subnet(24)):
        subnet = str(subnet)
        if subnet not in network_used_ranges:
            break
    else:
        raise j.exceptions.Runtime(f"failed to find a free range to assign to node {deployment_node.node_id}")
    add_node_to_network(network, deployment_node.node_id, pool, subnet)
ssh_key = get_ssh_key()


wid = deploy_ubuntu_server(deployment_node, pool, ssh_key)
wait_workload(wid)
j.logger.info(f"Reserving the proxy on the gateway {gateway1_ip}")
network = zos.network.load_network(NETWORK_NAME)
first_proxy = create_proxy(deployment_node, gateway1, pool, get_free_ip(network, deployment_node.node_id), SUBDOMAIN1)
wait_workload(first_proxy)
j.logger.info(f"Reserving the proxy on the gateway {gateway2_ip}")
second_proxy = create_proxy(deployment_node, gateway2, pool, get_free_ip(network, deployment_node.node_id), SUBDOMAIN1)
wait_workload(second_proxy)
j.logger.info(f"Reserving the proxy on the gateway {gateway1_ip}")
second_domain_proxy = create_proxy(
    deployment_node, gateway1, pool, get_free_ip(network, deployment_node.node_id), SUBDOMAIN2
)
wait_workload(second_domain_proxy)
input(f"Check https://{SUBDOMAIN1} reachable after pointing it to {gateway1_ip} in /etc/hosts")
j.logger.info(f"Decommisioning the proxy workload from the first gateway")
zos.workloads.decomission(first_proxy)
if gateway1_ip != gateway2_ip:
    input(f"Check https://{SUBDOMAIN1} is no longer reachable.")
input(f"Check https://{SUBDOMAIN1} reachable after pointing it to {gateway2_ip} in /etc/hosts")
input(
    f"Check https://{SUBDOMAIN2} is not reachable because the generated certificate for a different domain. but is accessible using http after pointing it to {gateway1_ip}."
)
