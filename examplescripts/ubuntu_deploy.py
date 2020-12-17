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
from jumpscale.clients.explorer.models import NextAction, State, WorkloadType


zos = j.sals.zos.get()
WALLET_NAME = "test"
network_name = "management"
ip_range = "10.100.0.0/16"
wg_quick = None


bad_nodes = []


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


def get_free_iprange(ip_range, network_used_ranges):
    network_range = netaddr.IPNetwork(ip_range)
    for _, subnet in enumerate(network_range.subnet(24)):
        node_iprange = str(subnet)
        if node_iprange not in network_used_ranges:
            return node_iprange
    else:
        raise j.exceptions.Runtime(f"can't find free subnets in network {network_name}")


def get_deploymnet_node(pool):
    available_nodes = list(zos.nodes_finder.nodes_by_capacity(cru=0, sru=1, mru=0, pool_id=pool.pool_id))
    available_nodes = [node for node in available_nodes if node.node_id not in bad_nodes]
    return available_nodes[0]


payment_detail = zos.pools.create(cu=100, su=100, ipv4us=0, farm="freefarm", currencies=["TFT"])
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

if not network_node_ids:
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

    j.core.executors.run_local("wg-quick up ./ubuntu_deploy.conf")

else:
    input("Please make sure you have access to the management network on this machine. Press enter to continue")

# get free nodes for deploying containers

nodes = []
deployment_nodes = [get_deploymnet_node(pool)]
bad_nodes.append(deployment_nodes[0].node_id)
deployment_nodes.append(get_deploymnet_node(pool))

for _, node in enumerate(deployment_nodes):
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

network = zos.network.load_network(network_name)

ip_container_1 = get_free_ip(network, deployment_nodes[0].node_id)

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
success = j.sals.reservation_chatflow.deployer.wait_workload(result)
workload = zos.workloads.get(result)
if not success:
    raise j.exceptions.Runtime(
        f"failed to deploy container workload {result} due to error: {workload.info.result.message}"
    )
print("First container deployed successfully")

# Deploy container 2
ip_container_2 = get_free_ip(network, deployment_nodes[1].node_id)
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
success = j.sals.reservation_chatflow.deployer.wait_workload(result)
workload = zos.workloads.get(result)
if not success:
    raise j.exceptions.Runtime(
        f"failed to deploy container workload {result} due to error: {workload.info.result.message}"
    )
print("Second container deployed successfully")


sleep(10)
if j.clients.sshclient.find("ubuntu_script"):
    j.clients.sshclient.delete("ubuntu_script")

if j.clients.sshclient.find("ubuntu_script2"):
    j.clients.sshclient.delete("ubuntu_script2")

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
