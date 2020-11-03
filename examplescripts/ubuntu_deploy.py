"""
This script is for deploying two ubuntu containers and testing sshing between them
Steps:
- creating new pool
- loading network with name `management` to create containers on it or creating new network with same name if it doesn't exist
- deploy network with access node
- deploy two containers on the network
- use ssh forwarding to ssh between the containers
"""

from jumpscale.loader import j
from time import sleep
import netaddr
import random


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


def get_node_free_ip(ip_range):
    """
    get a node free ip, skips the first ip as it is assigned to the network
    """
    hosts = netaddr.IPNetwork(ip_range).iter_hosts()
    next(hosts)
    return str(next(hosts))  # skip ip used by node


def get_free_iprange(ip_range, network_used_ranges):
    network_range = netaddr.IPNetwork(ip_range)
    for _, subnet in enumerate(network_range.subnet(24)):
        node_iprange = str(subnet)
        if node_iprange not in network_used_ranges:
            return node_iprange
    else:
        raise j.exceptions.Runtime(f"can't find free subnets in network {network_name}")


zos = j.sals.zos.get()
WALLET_NAME = "test"
network_name = "management"
ip_range = "10.100.0.0/16"
wg_quick = None


payment_detail = zos.pools.create(cu=100, su=100, farm="freefarm", currencies=["TFT"])
print(payment_detail)

if not j.clients.stellar.find(WALLET_NAME):
    j.clients.stellar.create_testnet_funded_wallet(WALLET_NAME)

wallet = j.clients.stellar.get(WALLET_NAME)

txs = zos.billing.payout_farmers(wallet, payment_detail)
print(txs)
pool = zos.pools.get(payment_detail.reservation_id)
# wait until pool is activated
while pool.cus == 0:
    pool = zos.pools.get(payment_detail.reservation_id)
    sleep(1)

print("compute units available:", pool.cus)
print("storage units available:", pool.sus)

# create ssh key
if not j.sals.fs.exists("/tmp/.ssh"):
    j.core.executors.run_local('mkdir /tmp/.ssh && ssh-keygen -t rsa -f /tmp/.ssh/id_rsa -q -N "" ')
j.core.executors.run_local("ssh-add /tmp/.ssh/id_rsa")

ssh_cl = j.clients.sshkey.get("ubuntu_script")
ssh_cl.private_key_path = "/tmp/.ssh/id_rsa"
ssh_cl.load_from_file_system()
ssh_cl.save()

network = zos.network.load_network(network_name)
if not network:
    network = zos.network.create(ip_range, network_name)

network_node_ids = set()
network_used_ranges = set()
node_ranges = {}

# get used range in the network
for resource in network.network_resources:
    node_ranges[resource.info.node_id] = resource.iprange
    network_node_ids.add(resource.info.node_id)
    network_used_ranges.add(resource.iprange)
    for peer in resource.peers:
        network_used_ranges.add(peer.iprange)

# search for access node with public IPv4
pool_nodes = list(zos.nodes_finder.nodes_by_capacity(pool_id=pool.pool_id))
for node in filter(zos.nodes_finder.filter_public_ip4, pool_nodes):
    if zos.nodes_finder.filter_is_up(node):
        access_node = node
        break
else:
    raise Exception("can not find a node with ipv4 that can be used as access node for the cluster")

freerange1 = get_free_iprange(ip_range, network_used_ranges)
zos.network.add_node(network, access_node.node_id, freerange1, pool.pool_id)
network_used_ranges.add(freerange1)

freerange2 = get_free_iprange(ip_range, network_used_ranges)
wg_quick = zos.network.add_access(network, access_node.node_id, freerange2, ipv4=True)
network_used_ranges.add(freerange2)
print(wg_quick)
with open("ubuntu_deploy.conf", "w") as f:
    f.writelines(wg_quick)

for workload in network.network_resources:
    wid = zos.workloads.deploy(workload)
    if not wait_workload(wid):
        raise Exception(f"Failed to deploy, Workload ID: {wid}")

# get free nodes for deploying containers
nodes = []
random.shuffle(pool_nodes)
for _, node in enumerate(pool_nodes):
    if node.node_id in network_node_ids:
        nodes.append({"id": node.node_id, "ip_range": node_ranges[node.node_id]})
        continue
    if not zos.nodes_finder.filter_is_up(node) or node.node_id == access_node.node_id:
        continue

    freerange = get_free_iprange(ip_range, network_used_ranges)

    zos.network.add_node(network, node.node_id, freerange, pool.pool_id)
    nodes.append({"id": node.node_id, "ip_range": freerange})
    network_used_ranges.add(freerange)

    # two free nodes for two containers
    if len(nodes) == 2:
        break

# Deploy the network
node_workloads = {}
for workload in network.network_resources:
    node_workloads[workload.info.node_id] = workload

for workload in node_workloads.values():
    wid = zos.workloads.deploy(workload)
    if not wait_workload(wid):
        raise Exception(f"Failed to deploy network for ubuntu, Workload ID: {wid}")

ip_container_1 = get_node_free_ip(nodes[0]["ip_range"])
ip_container_2 = get_node_free_ip(nodes[1]["ip_range"])

# Deploy container 1
container = zos.container.create(
    node_id=nodes[0]["id"],
    network_name=network_name,
    ip_address=ip_container_1,
    flist="https://hub.grid.tf/tf-bootable/3bot-ubuntu-20.04.flist",
    capacity_pool_id=pool.pool_id,
    interactive=False,
    env={"pub_key": ssh_cl.public_key.rstrip()},
    entrypoint="/bin/bash /start.sh",
    public_ipv6=True,
)
result = zos.workloads.deploy(container)
j.sals.reservation_chatflow.deployer.wait_workload(result)
workload = zos.workloads.get(result)
print("First container deployed successfully")

# Deploy container 2
container2 = zos.container.create(
    node_id=nodes[1]["id"],
    network_name=network_name,
    ip_address=ip_container_2,
    flist="https://hub.grid.tf/tf-bootable/3bot-ubuntu-20.04.flist",
    capacity_pool_id=pool.pool_id,
    interactive=False,
    env={"pub_key": ssh_cl.public_key.rstrip()},
    entrypoint="/bin/bash /start.sh",
    public_ipv6=True,
)
result = zos.workloads.deploy(container2)
j.sals.reservation_chatflow.deployer.wait_workload(result)
workload = zos.workloads.get(result)
print("Second container deployed successfully")

_, config, _ = j.core.executors.run_local("sudo wg")
if "wg_script" in config:
    j.core.executors.run_local("wg-quick down /tmp/wg_script.conf")

j.core.executors.run_local(f'echo "{wg_quick}" > /tmp/wg_script.conf')
j.core.executors.run_local("wg-quick up /tmp/wg_script.conf")

sleep(5)

localclient = j.clients.sshclient.get("ubuntu_script")
localclient.sshkey = "ubuntu_script"
localclient.host = ip_container_1
localclient.save()

localclient2 = j.clients.sshclient.get("ubuntu_script2")
localclient2.sshkey = "ubuntu_script"
localclient2.host = ip_container_2
localclient2.save()

print(localclient.sshclient.run(f'ssh -o "StrictHostKeyChecking=no" root@{ip_container_2} -A ls /'))
print(localclient2.sshclient.run(f'ssh -o "StrictHostKeyChecking=no" root@{ip_container_1} -A ls /'))
print("Congratulations, SUCCESS")
