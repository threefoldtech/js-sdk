from jumpscale.loader import j
from time import sleep
import uuid

zos = j.sals.zos

payment_detail = zos.pools.create(cu=100, su=100, farm="freefarm", currencies=["TFT"])
print(payment_detail)

wallet = j.clients.stellar.get("wallet")
txs = zos.billing.payout_farmers(wallet, payment_detail)
pool = zos.pools.get(payment_detail.reservation_id)
while pool.cus == 0:
    pool = zos.pools.get(payment_detail.reservation_id)
    sleep(1)

print("compute units available:", pool.cus)
print("storage units available:", pool.sus)

network_name = "demo_network3"
ip_range = "172.19.0.0/16"

network = zos.network.create(ip_range, network_name)
nodes = zos.nodes_finder.nodes_by_capacity(pool_id=pool.pool_id)
access_node = list(filter(zos.nodes_finder.filter_public_ip4, nodes))[0]
zos.network.add_node(network, access_node.node_id, "172.19.2.0/24", pool.pool_id)
wg_quick = zos.network.add_access(network, access_node.node_id, "172.19.3.0/24", ipv4=True)

for workload in network.network_resources:
    wid = zos.workloads.deploy(workload)
    workload = zos.workloads.get(wid)
    while not workload.info.result.workload_id:
        sleep(1)
        workload = zos.workloads.get(wid)
print(wg_quick)

cpu = 1
mem = 1024
disk = 256

available_nodes = list(zos.nodes_finder.nodes_by_capacity(cru=0, sru=0, mru=0, pool_id=pool.pool_id))

deployment_node = available_nodes[0]
zos.network.add_node(network, deployment_node.node_id, "172.19.4.0/24", pool.pool_id)

for workload in network.network_resources:
    wid = zos.workloads.deploy(workload)
    workload = zos.workloads.get(wid)
    while not workload.info.result.workload_id:
        sleep(1)
        workload = zos.workloads.get(wid)

container = zos.container.create(
    node_id=deployment_node.node_id,
    network_name=network_name,
    ip_address="172.19.4.3",
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
SUBDOMAIN = f"solution-expose-ubuntu-demo.{DOMAIN}"

gateway_ips = []
for ns in gateway.dns_nameserver:
    gateway_ips.append(j.sals.nettools.get_host_by_name(ns))
subdomain = zos.gateway.sub_domain(gateway.node_id, SUBDOMAIN, gateway_ips, pool.pool_id)
wid = zos.workloads.deploy(subdomain)

SECRET = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

reverse_proxy = zos.gateway.tcp_proxy_reverse(gateway.node_id, SUBDOMAIN, SECRET, pool.pool_id)
wid = zos.workloads.deploy(reverse_proxy)

SOLUTION_IP_ADDRESS = "172.19.4.3"
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
CONTAINER_IP_ADDRESS = "172.19.4.4"
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

print(SUBDOMAIN)
