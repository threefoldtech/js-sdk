from jumpscale.loader import j
from time import sleep
import uuid

zos = j.sals.zos

payment_detail = zos.pools.create(cu=100, su=100, farm="freefarm", currencies=["TFT"])
print(payment_detail)

wallet = j.clients.stellar.get(
    "demos_wallet"
)  # change wallet_name depand on your wallet
txs = zos.billing.payout_farmers(wallet, payment_detail)
pool = zos.pools.get(payment_detail.reservation_id)
while pool.cus == 0:
    pool = zos.pools.get(payment_detail.reservation_id)
    sleep(1)

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

for workload in network.network_resources:
    wid = zos.workloads.deploy(workload)
    j.sals.reservation_chatflow.deployer.wait_workload(wid)
    workload = zos.workloads.get(wid)
print(wg_quick)

cpu = 1
mem = 1024
disk = 256

available_nodes = list(
    zos.nodes_finder.nodes_by_capacity(cru=0, sru=0, mru=0, pool_id=pool.pool_id)
)

deployment_node = available_nodes[0]
zos.network.add_node(network, deployment_node.node_id, "10.110.4.0/24", pool.pool_id)

for workload in network.network_resources:
    wid = zos.workloads.deploy(workload)
    j.sals.reservation_chatflow.deployer.wait_workload(wid)
    workload = zos.workloads.get(wid)

#Deploy container 1
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
    env={
        "pub_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDL/IvQhp+pxoZKaQ9kHYLwlWNgZOsIgPnTa9ZsTcJk5EF9zui2+gDlbIDnk1xE9L6yn2I593d3/fTiJgcImTfKqhhd9siZNGxIRKyXw+0olMwccEWCY6DIJG/PgSCRsHyw/zPGntLax4+lV0svAp7i+Wa8fjZsHSDTeBMc8xRf9p7ASV53NwyjUum7KUB7bJzCUlZpykNwN9+CAHZv8X+7qgiQ58yHVwlrccaLX8KVU5fhSl5MME8gjvG8naI/PtFMkRxo0xvD/PkTsiV+1ba6PwPrqTGMXWoPpJTs6ICbv4LbzLPdfmOXsYehYlBHPopxxU0IUyQU0Z1GEmGfP6bj /root/.ssh/id_rsa"
    }, #Change ssh-key depan on your key
    entrypoint="/bin/bash /start.sh",
    public_ipv6=True,
)

result = zos.workloads.deploy(container)

j.sals.reservation_chatflow.deployer.wait_workload(result)
workload = zos.workloads.get(result)

print("First container deployed successfully")

#Deploy container 2
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
    env={
        "pub_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDL/IvQhp+pxoZKaQ9kHYLwlWNgZOsIgPnTa9ZsTcJk5EF9zui2+gDlbIDnk1xE9L6yn2I593d3/fTiJgcImTfKqhhd9siZNGxIRKyXw+0olMwccEWCY6DIJG/PgSCRsHyw/zPGntLax4+lV0svAp7i+Wa8fjZsHSDTeBMc8xRf9p7ASV53NwyjUum7KUB7bJzCUlZpykNwN9+CAHZv8X+7qgiQ58yHVwlrccaLX8KVU5fhSl5MME8gjvG8naI/PtFMkRxo0xvD/PkTsiV+1ba6PwPrqTGMXWoPpJTs6ICbv4LbzLPdfmOXsYehYlBHPopxxU0IUyQU0Z1GEmGfP6bj /root/.ssh/id_rsa"
    }, #Change ssh-key depan on your key
    entrypoint="/bin/bash /start.sh",
    public_ipv6=True,
)

result = zos.workloads.deploy(container2)

j.sals.reservation_chatflow.deployer.wait_workload(result)
workload = zos.workloads.get(result)

print("Second container deployed successfully")

j.core.executors.run_local(f'echo "{wg_quick}" > /etc/wireguard/wg_script.conf')
j.core.executors.run_local("wg-quick up wg_script")

sleep(5)
ssh_cl = j.clients.sshkey.get("ubuntu_script")
ssh_cl.private_key_path = "/root/.ssh/id_rsa"
ssh_cl.load_from_file_system()
ssh_cl.save()

localclient = j.clients.sshclient.get("ubuntu_script")
localclient.sshkey = "ubuntu_script"
localclient.host = ip_container_1

localclient2 = j.clients.sshclient.get("ubuntu_script2")
localclient2.sshkey = "ubuntu_script"
localclient2.host = ip_container_2

print(
    localclient.sshclient.run(
        f'ssh -o "StrictHostKeyChecking=no" root@{ip_container_2} ls /'
    )
)


print(
    localclient2.sshclient.run(
        f'ssh -o "StrictHostKeyChecking=no" root@{ip_container_1} ls /'
    )
)

print("Congratulations, SUCCESS")
