# Making use of zosv2

## Index

- [Reserve some capacity](#create-capacity-pool)
- [Create a network](#create-a-network)
- [Create a container](#create-a-container)
- [Create a Kubernetes cluster](#create-k8s-cluster)
- [Reserve storage](#reserve-storage)

## Create capacity pool

The first step before being able to deploy some workloads on the grid is to reserve some capacity.
You reserve capacity by creating a pool of capacity on a certain farm.

```python
zos = j.sals.zos

# create a capacity pool container 500 cloud units, 500 storage units on the farm called "farm_name"
# and ask to pay using TFT
payment_detail = zos.pools.create(cu=500,su=500,farm="farm_name", currencies=['TFT'])
pool_id = payment_detail.reservation_id
# get your wallet ready
wallet = j.clients.stellar.get('my_wallet')

# pay for the capacity pool
# txs contains the list of transactions made on stellar to pay for the capacity
txs = zos.billing.payout_farmers(wallet,payment_detail)

# get the detail of your capacity pool
pool = zos.pools.get(pool_id)
```

## Create a network

### Create a network on all the nodes of a farm

```python
zos = j.sals.zos

# create a reservation
r = zos.reservation_create()
# create a network with name <network_name> and add it to the reservation
# ip_range = "xxx.xxx.0.0/16", range in private address space, ex. 172.24.0.0/16
network = zos.network.create(r, ip_range="172.24.0.0/16", network_name="<network_name>")

# find all node from farm with id <farm_id>
nodes = zos.nodes_finder.nodes_search(farm_id=<farm_id>)
# add each node into the network
for i, node in enumerate(nodes):
    iprange = f"172.24.{i+2}.0/24"
    zos.network.add_node(network, node.node_id, iprange)

# find a node that is public and has ipv4 public IP
node = next(filter(zos.nodes_finder.filter_public_ip4, nodes))
# add an external peer to the network for user laptop access using the public node as entrypoint
# we store the result of this command cause this is the configuration the user has to use to connect to
# the network from his laptop
wg_config = zos.network.add_access(network, node.node_id, "172.24.100.0/24", ipv4=True)


expiration = j.data.time.epoch + (3600 * 24 * 365)
# register the reservation
rid = zos.reservation_register(r, expiration)
time.sleep(5)
# inspect the result of the reservation provisioning
result = zos.reservation_result(rid)

print("wireguard configuration")
print(wg_config)
print("provisioning result")
print(result)
print("network")
for n2 in network.network_resources:
    print(n2.node_id, n2.iprange)
```

## set-up network in Wireguard
In order to have the network active and accessible from your local machine, a good way is to create the network configuration in Wireguard.
To do this, copy the setup into wireguard:
```bash
# for macOS 10.7 or newer

# in Docker installation:
docker exec --it 3bot bash

# for ubuntu

wg-quick [up|down] $config_file


cat /tmp/wg_config

```
You will see something like :
```bash
[Interface]
Address = 100.64.22.100/32
PrivateKey = <private_key>
[Peer]
PublicKey = <public_key>
AllowedIPs = 172.22.0.0/16, 100.64.22.0/32
PersistentKeepalive = 25
Endpoint = 185.69.166.59:5000
```
Import these lines into a new Wireguard tunnel.

## create a container

```python
zos = j.sals.zos

# create a reservation
r = zos.reservation_create()
# add container reservation into the reservation
zos.container.create(reservation=r,
                    node_id='2fi9ZZiBGW4G9pnrN656bMfW6x55RSoHDeMrd9pgSA8T', # one of the node_id that is part of the network
                    network_name='<network_name>', # this assume this network is already provisioned on the node
                    ip_address='172.24.1.10', # part of ip_range you reserved for your network xxx.xxx.1.10
                    flist='https://hub.grid.tf/zaibon/zaibon-ubuntu-ssh-0.0.2.flist', # flist of the container you want to install
                  # interactive=True,         # True only if corex_connect required, default false
                  # env={},                   # field for parameters like config
                    entrypoint='/sbin/my_init')

# expiration = j.data.time.epoch + (3600 * 24 * 365)
# reserve until now + (x) seconds
expiration = j.data.time.epoch + (10*60)
# register the reservation
rid = zos.reservation_register(r, expiration)
time.sleep(5)
# inspect the result of the reservation provisioning
result = zos.reservation_result(rid)

print("provisioning result")
print(result)
```

## create k8s cluster

Main documentation can be found [here](https://github.com/threefoldtech/zos/tree/master/docs/kubernetes)

### Example of a deployment

```python
zos = j.sals.zos
r = zos.reservation_create()

cluster_secret = 'supersecret'
size = 1
network_name = 'zaibon_testnet_0'
sshkeys = ['ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMtml/KgilrDqSeFDBRLImhoAfIqikR2N9XH3pVbb7ex zaibon@tesla']

master = zos.kubernetes.add_master(
    reservation=r,
    node_id='2fi9ZZiBGW4G9pnrN656bMfW6x55RSoHDeMrd9pgSA8T',
    network_name=network_name,
    cluster_secret=cluster_secret,
    ip_address='172.24.1.20',
    size=size,
    ssh_keys=sshkeys)


worker = zos.kubernetes.add_worker(
    reservation=r,
    node_id='72CP8QPhMSpF7MbSvNR1TYZFbTnbRiuyvq5xwcoRNAib',
    network_name=network_name,
    cluster_secret=cluster_secret,
    ip_address='172.24.2.20',
    size=size,
    master_ip=master.ipaddress,
    ssh_keys=sshkeys)

expiration = j.data.time.epoch + (3600 * 24 * 365)
# register the reservation
rid = zos.reservation_register(r, expiration)
time.sleep(120)
# inspect the result of the reservation provisioning
result = zos.reservation_result(rid)

print("provisioning result")
print(result)
```

## Reserve storage

## Example : reserve 0-DB storage namespaces

```python
zos = j.sals.zos

# find some node that have 10 GiB of SSD disks
nodes = zos.nodes_finder.nodes_search(sru=10)

# create a reservation
r = zos.reservation_create()
# add container reservation into the reservation
zos.zdb.create(
    reservation=r,
    node_id=nodes[0].node_id,
    size=10,
    mode='seq',
    password='supersecret',
    disk_type="SSD",
    public=False)

expiration = j.data.time.epoch + (3600 * 24)
# register the reservation
rid = zos.reservation_register(r, expiration)
time.sleep(5)
# inspect the result of the reservation provisioning
result = zos.reservation_result(rid)

print("provisioning result")
print(result)
```

## Example : deploy minio container

```python
password = "supersecret"

# first find the node where to reserve 0-db namespaces
nodes = zos.nodes_finder.nodes_search(sru=10)
nodes = list(filter(zos.nodes_finder.filter_is_up,nodes))
nodes = nodes[:3]

# find a node where to run the minio container itself
# make sure this node is part of your overlay network
nodes = zos.nodes_finder.nodes_search(sru=10)
nodes = list(filter(zos.nodes_finder.filter_is_up,nodes))
minio_node = nodes[0]

# create a reservation for the 0-DBs
reservation_storage = zos.reservation_create()
# reservation some 0-db namespaces
for node in nodes:
    zos.zdb.create(
        reservation=reservation_storage,
        node_id=node.node_id,
        size=10,
        mode='seq',
        password='supersecret',
        disk_type="SSD",
        public=False)

volume = zos.volume.create(reservation_storage,minio_node.node_id,size=10,type='SSD')

zdb_rid = zos.reservation_register(reservation_storage, j.data.time.epoch+(60*60))
results = zos.reservation_result(zdb_rid)

# read the IP address of the 0-db namespaces after they are deployed
# we will need these IPs when creating the minio container
namespace_config = []
for result in results:
    data = j.data.serializers.json.loads(result.data_json)
    cfg = f"{data['Namespace']}:{password}@[{data['IP']}]:{data['Port']}"
    namespace_config.append(cfg)


# create a reservation for the minio container
reservation_container = zos.reservation_create()

container = zos.container.create(
    reservation=reservation_container,
    node_id="72CP8QPhMSpF7MbSvNR1TYZFbTnbRiuyvq5xwcoRNAib",
    network_name='zaibon_testnet_0', # this assume this network is already provisioned on the node
    ip_address='172.24.2.15',
    flist='https://hub.grid.tf/tf-official-apps/minio-2020-01-25T02-50-51Z.flist',
    entrypoint='/bin/entrypoint',
    cpu=2,
    memory=2048,
    env={
        "SHARDS":','.join(namespace_config),
        "DATA":"2",
        "PARITY":"1",
        "ACCESS_KEY":"minio",
        "SECRET_KEY":"passwordpassword",
    })

zos.volume.attach_existing(
    container=container,
    volume_id=f'{zdb_rid}-{volume.workload_id}',
    mount_point='/data')


rid = zos.reservation_register(reservation_container, j.data.time.epoch+(60*60))
results = zos.reservation_result(rid)
```
