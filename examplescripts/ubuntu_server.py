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

with open("/tmp/wg-demo.conf", "w") as f:
    f.write(wg_quick)

j.sals.process.execute("wg-quick up /tmp/wg-demo.conf")

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

with open("/home/omar/.ssh/id_rsa.pub", "r") as f:
    ssh_key = f.read()

print(ssh_key)

env = {"pub_key": ssh_key}

container = zos.container.create(
    node_id=deployment_node.node_id,
    network_name=network_name,
    ip_address="172.19.4.3",
    flist="https://hub.grid.tf/tf-bootable/3bot-ubuntu-20.04.flist",
    capacity_pool_id=pool.pool_id,
    cpu=cpu,
    memory=mem,
    disk_size=disk,
    entrypoint="/bin/bash /start.sh",
    env=env,
    interactive=False,
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

DOMAIN = "mydomain.com"
SUBDOMAIN1 = f"testa.{DOMAIN}"
SUBDOMAIN2 = f"testb.{DOMAIN}"

gateway_ips = []
for ns in gateway.dns_nameserver:
    gateway_ips.append(j.sals.nettools.get_host_by_name(ns))

SECRET = f"{j.core.identity.me.tid}:{uuid.uuid4().hex}"

reverse_proxy = zos.gateway.tcp_proxy_reverse(gateway.node_id, SUBDOMAIN1, SECRET, pool.pool_id)
wid = zos.workloads.deploy(reverse_proxy)

SOLUTION_IP_ADDRESS = "172.19.4.3"
SOLUTION_PORT = 3001
SOLUTION_TLS_PORT = 443  # not serving https actually, but it must be provided
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

workload = zos.workloads.get(wid)
while not workload.info.result.workload_id:
    sleep(1)
    workload = zos.workloads.get(wid)

key = j.clients.sshkey.get("omar")
key.private_key_path = "/home/omar/.ssh/id_rsa"
key.save()

localclient = j.clients.sshclient.get("ubuntu_client")
localclient.host = "172.19.4.3"
localclient.sshkey = "omar"
localclient.connect_timeout = 5 * 60
cmds = f"""apt update
apt -y install curl python3 psmisc
export DEBIAN_FRONTEND=noninteractive
curl -L https://github.com/caddyserver/caddy/releases/download/v2.1.1/caddy_2.1.1_linux_amd64.deb > ./caddy_2.1.1_linux_amd64.deb
dpkg -i ./caddy_2.1.1_linux_amd64.deb
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/threefoldfoundation/grid_testscripts/master/tools/install.sh)"
cd ~/code/github/threefoldfoundation/grid_testscripts
source start.sh
export DOMAIN={SUBDOMAIN1}
echo "tls internal" >> /root/code/github/threefoldfoundation/grid_testscripts/templates/caddy_proxy
web_run"""
localclient.sshclient.run(cmds)


print(SUBDOMAIN1)
print(SUBDOMAIN2)
