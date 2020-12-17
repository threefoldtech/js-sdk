"""
This is an example script to create an ubuntu container with corex enabled and expose it over a managed domain.

Requirements:
1- stellar wallet named "wallet" funded with enough TFTs

Expected Result:
1- a network named "management" created or extended with the nodes required for container deployment
2- ubuntu container with corex enabled and exposed over a managed domain.

Running the script:
```
python ubuntu.py
```
"""


from jumpscale.loader import j
import netaddr
from time import sleep
import uuid
from jumpscale.clients.explorer.models import State, WorkloadType, NextAction

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
    while not workload.info.result.state.value and not workload.info.result.message:
        if j.data.time.now().timestamp > timeout:
            raise j.exceptions.Runtime(f"workload {wid} failed to deploy in time")
        sleep(1)
        workload = zos.workloads.get(wid)
    if workload.info.result.state != State.Ok:
        raise j.exceptions.Runtime(f"workload {wid} failed due to {workload.info.result.message}")


payment_detail = zos.pools.create(cu=100, su=100, ipv4us=0, farm="freefarm", currencies=["TFT"])
print(payment_detail)

wallet = j.clients.stellar.get("wallet")
txs = zos.billing.payout_farmers(wallet, payment_detail)
pool = zos.pools.get(payment_detail.reservation_id)
while pool.cus == 0:
    pool = zos.pools.get(payment_detail.reservation_id)
    sleep(1)

print("compute units available:", pool.cus)
print("storage units available:", pool.sus)

network_name = "management"
ip_range = "10.100.0.0/16"
network = zos.network.load_network(network_name)
if not network:
    network = zos.network.create(ip_range=ip_range, network_name=network_name)
    nodes = zos.nodes_finder.nodes_by_capacity(pool_id=pool.pool_id)
    access_node = list(filter(zos.nodes_finder.filter_public_ip4, nodes))[0]
    zos.network.add_node(network, access_node.node_id, "100.10.0.0/24", pool.pool_id)
    wg_quick = zos.network.add_access(network, access_node.node_id, "100.10.1.0/24", ipv4=True)
    wids = []
    for workload in network.network_resources:
        wid = zos.workloads.deploy(workload)
        wids.append(wid)
    for wid in wids:
        wait_workload(wid)
    print(wg_quick)
    with open("ubuntu.conf", "w") as f:
        f.write(wg_quick)

cpu = 1
mem = 1024
disk = 256

available_nodes = list(zos.nodes_finder.nodes_by_capacity(cru=0, sru=0, mru=0, pool_id=pool.pool_id))

deployment_node = available_nodes[0]


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
        if subnet in network_used_ranges:
            continue
        break
    else:
        raise j.exceptions.Runtime("couldn't find free range in management network")

    zos.network.add_node(network, deployment_node.node_id, subnet, pool.pool_id)
    wids = []
    for resource in network.network_resources:
        wid = zos.workloads.deploy(resource)
        wids.append(wid)
    for wid in wids:
        wait_workload(wid)

network = zos.network.load_network(network_name)


SOLUTION_IP_ADDRESS = get_free_ip(network, deployment_node.node_id)
container = zos.container.create(
    node_id=deployment_node.node_id,
    network_name=network_name,
    ip_address=SOLUTION_IP_ADDRESS,
    flist="https://hub.grid.tf/tf-bootable/3bot-ubuntu-20.04.flist",
    capacity_pool_id=pool.pool_id,
    cpu=cpu,
    memory=mem,
    disk_size=disk,
    interactive=True,
)

result = zos.workloads.deploy(container)

gateway_ids = {g.node_id: g for g in zos.gateways_finder.gateways_search() if zos.nodes_finder.filter_is_up(g)}

gateway = None
for gid, g in gateway_ids.items():
    if gid in pool.node_ids:
        if not g.dns_nameserver:
            continue
        gateway = g
        break

if not gateway:
    raise j.exceptions.Input(f"Can't find any gateway")

DOMAIN = gateway.managed_domains[0]
SUBDOMAIN = f"solution-expose-ubuntu-{uuid.uuid4().hex}.{DOMAIN}"

gateway_ips = []
for ns in gateway.dns_nameserver:
    gateway_ips.append(j.sals.nettools.get_host_by_name(ns))
subdomain = zos.gateway.sub_domain(gateway.node_id, SUBDOMAIN, gateway_ips, pool.pool_id)
wid = zos.workloads.deploy(subdomain)
wait_workload(wid)

SECRET = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

reverse_proxy = zos.gateway.tcp_proxy_reverse(gateway.node_id, SUBDOMAIN, SECRET, pool.pool_id)
wid = zos.workloads.deploy(reverse_proxy)
wait_workload(wid)

SOLUTION_PORT = 7681
SOLUTION_TLS_PORT = 7681  # not serving https actually, but it must be provided
GATEWAY_IP = gateway_ips[0]


entrypoint = (
    f"/bin/trc -local {SOLUTION_IP_ADDRESS}:{SOLUTION_PORT} -local-tls {SOLUTION_IP_ADDRESS}:{SOLUTION_TLS_PORT}"
    f" -remote {GATEWAY_IP}:{gateway.tcp_router_port}"
)

# trc container deployment
NODE_ID = deployment_node.node_id
FLIST_URL = "https://hub.grid.tf/tf-official-apps/tcprouter:latest.flist"
CONTAINER_IP_ADDRESS = get_free_ip(network, NODE_ID)
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
wait_workload(wid)

print(SUBDOMAIN)
