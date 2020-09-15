from jumpscale.loader import j
from time import sleep
import uuid
import random

zos = j.sals.zos

payment_detail = zos.pools.create(cu=100, su=100, farm="freefarm", currencies=["TFT"])
print(payment_detail)

if not j.clients.stellar.find("ubuntu_wallet"):
    j.clients.stellar.create_testnet_funded_wallet("ubuntu_wallet")

wallet = j.clients.stellar.get("ubuntu_wallet")

txs = zos.billing.payout_farmers(wallet, payment_detail)
pool = zos.pools.get(payment_detail.reservation_id)
while pool.cus == 0:
    pool = zos.pools.get(payment_detail.reservation_id)
    sleep(1)

if not j.sals.fs.exists("/tmp/.ssh"):
    j.core.executors.run_local(
        'mkdir /tmp/.ssh && ssh-keygen -t rsa -f /tmp/.ssh/id_rsa -q -N "" '
    )

ssh_cl = j.clients.sshkey.get("ubuntu_script")
ssh_cl.private_key_path = "/tmp/.ssh/id_rsa"
ssh_cl.load_from_file_system()
ssh_cl.save()

print("compute units available:", pool.cus)
print("storage units available:", pool.sus)

network_name = "demo_network_script"
ip_range = "10.110.0.0/16"
ip_container_1 = "10.110.4.12"

ip_container_2 = "10.110.4.15"

network = zos.network.create(ip_range, network_name)
nodes = zos.nodes_finder.nodes_by_capacity(pool_id=pool.pool_id)
access_node = list(filter(zos.nodes_finder.filter_public_ip4, nodes))[0]
zos.network.add_node(network, access_node.node_id, "10.110.2.0/24", pool.pool_id)
wg_quick = zos.network.add_access(
    network, access_node.node_id, "10.110.3.0/24", ipv4=True
)

node_workloads = {}
for workload in network.network_resources:
    node_workloads[workload.info.node_id] = workload

for workload in node_workloads.values():
    wid = zos.workloads.deploy(workload)
    if not j.sals.reservation_chatflow.deployer.wait_workload(wid):
        raise Exception(f"Failed to deploy network for kubernetes, Workload ID: {wid}")

print(wg_quick)

cpu = 1
mem = 1024
disk = 256

available_nodes = list(
    zos.nodes_finder.nodes_by_capacity(cru=0, sru=2, mru=2, pool_id=pool.pool_id)
)
available_nodes = list(filter(j.sals.zos.nodes_finder.filter_is_up, available_nodes))
deployment_node = random.choice(available_nodes)
zos.network.add_node(network, deployment_node.node_id, "10.110.4.0/24", pool.pool_id)

node_workloads = {}
for workload in network.network_resources:
    node_workloads[workload.info.node_id] = workload

for workload in node_workloads.values():
    wid = zos.workloads.deploy(workload)
    if not j.sals.reservation_chatflow.deployer.wait_workload(wid):
        raise Exception(f"Failed to deploy network for kubernetes, Workload ID: {wid}")

# Deploy container 1
container = zos.container.create(
    node_id=deployment_node.node_id,
    network_name=network_name,
    ip_address=ip_container_1,
    flist="https://hub.grid.tf/tf-bootable/3bot-ubuntu-20.04.flist",
    capacity_pool_id=pool.pool_id,
    cpu=cpu,
    memory=mem,
    disk_size=disk,
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
    node_id=deployment_node.node_id,
    network_name=network_name,
    ip_address=ip_container_2,
    flist="https://hub.grid.tf/tf-bootable/3bot-ubuntu-20.04.flist",
    capacity_pool_id=pool.pool_id,
    cpu=cpu,
    memory=mem,
    disk_size=disk,
    interactive=False,
    env={"pub_key": ssh_cl.public_key.rstrip()},
    entrypoint="/bin/bash /start.sh",
    public_ipv6=True,
)

result = zos.workloads.deploy(container2)

j.sals.reservation_chatflow.deployer.wait_workload(result)
workload = zos.workloads.get(result)

print("Second container deployed successfully")

_, config, _ = j.core.executors.run_local("wg")
if "wg_script" in config:
    j.core.executors.run_local("wg-quick down /tmp/wg_script.conf")

j.core.executors.run_local(f'echo "{wg_quick}" > /tmp/wg_script.conf')
j.core.executors.run_local("wg-quick up /tmp/wg_script.conf")

sleep(5)
j.core.executors.run_local("eval `ssh-agent` && ssh-add /tmp/.ssh/id_rsa")
j.core.executors.run_local(f'ssh root@{ip_container_1} ssh -o "StrictHostKeyChecking=no" root@{ip_container_2} ls /')
j.core.executors.run_local(f'ssh root@{ip_container_2} ssh -o "StrictHostKeyChecking=no" root@{ip_container_1} ls /')

# will use sshclient when fix this issue (https://github.com/threefoldtech/js-sdk/issues/1135)
#localclient = j.clients.sshclient.get("ubuntu_script")
#localclient.sshkey = "ubuntu_script"
#localclient.host = ip_container_1
#localclient.save()
#
#localclient2 = j.clients.sshclient.get("ubuntu_script2")
#localclient2.sshkey = "ubuntu_script"
#localclient2.host = ip_container_2
#localclient2.save()
#
#print(
#    localclient.sshclient.run(
#        f'ssh -o "StrictHostKeyChecking=no" root@{ip_container_2} -A ls /'
#    )
#)
#
#
#print(
#    localclient2.sshclient.run(
#        f'ssh -o "StrictHostKeyChecking=no"  root@{ip_container_1} -A ls /'
#    )
#)

print("Congratulations, SUCCESS")
