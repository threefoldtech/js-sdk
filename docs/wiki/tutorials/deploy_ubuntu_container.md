# Deploy Ubuntu in the grid

## configuring identity

To configure your identity:

```python
me = j.core.identity.new(name="default", tname="3BOT_NAME", email="3BOT_EMAIL", words="3BOT_WORDS")

me.tid
# or
j.core.identity.me.tid
```
To register your identity in TFGrid
```python
me.save()
me.register()
```

## Create your network
```python
import time
zos = j.sals.zos

# create a reservation
r = zos.reservation_create()
# create a network with name <network_name> and add it to the reservation
# ip_range = "xxx.xxx.0.0/16", range in private address space, ex. 172.24.0.0/16
network = zos.network.create(r, ip_range="10.80.0.0/16", network_name="<network_name>")

# find all node from farm with id <farm_id>
nodes = list(j.sals.zos.get().nodes_finder.nodes_by_capacity(cru=1, sru=10, mru=2, hru=5, currency="TFT"))

# add each node into the network
for i, node in enumerate(nodes):
    iprange = f"10.80.{i+2}.0/24"
    zos.network.add_node(network, node.node_id, iprange)

# find a node that is public and has ipv4 public IP
node = next(filter(zos.nodes_finder.filter_public_ip6, nodes))
# add an external peer to the network for user laptop access using the public node as entrypoint
# we store the result of this command cause this is the configuration the user has to use to connect to
# the network from his laptop
wg_config = zos.network.add_access(network, node.node_id, "10.80.100.0/24", ipv4=False)

expiration = j.data.time.get().timestamp +3900
# register the reservation
registered_reservation = zos.reservation_register(r, expiration)
# inspect the result of the reservation provisioning might take between 1 to 2 mins before the result is reported, otherwise will return empty list
result = zos.reservation_result(registered_reservation.reservation_id)

print("wireguard configuration")
print(wg_config)
print("provisioning result")
print(result)
print("network")
for n2 in network.network_resources:
    print(n2.node_id, n2.iprange)
```

## Set-up network in Wireguard
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


## deploy ubuntu container access using ssh

```python
import time
zos = j.sals.zos

# create a reservation
r = zos.reservation_create()
# add container reservation into the reservation
zos.container.create(reservation=r,
                    node_id='2fi9ZZiBGW4G9pnrN656bMfW6x55RSoHDeMrd9pgSA8T', # one of the node_id that is part of the network
                    network_name='<network_name>', # this assume this network is already provisioned on the node
                    ip_address='10.80.1.10', # part of ip_range you reserved for your network xxx.xxx.1.10
                    flist='https://hub.grid.tf/tf-bootable/3bot-ubuntu-20.04.flist', # flist of the container you want to install
                    # interactive=True,         # True only if corex_connect required, default false
                    env={"pub_key":"YOUR_PUBLIC_KEY"},                   # field for parameters like config
                    entrypoint='/bin/bash /start.sh')

expiration = j.data.time.get().timestamp +3900
# register the reservation
registered_reservation = zos.reservation_register(r, expiration, currencies=["TFT"])
```
## deploy ubuntu container access using Web only COREX

```python
import time
zos = j.sals.zos

# create a reservation
r = zos.reservation_create()
# add container reservation into the reservation
zos.container.create(reservation=r,
                    node_id='2fi9ZZiBGW4G9pnrN656bMfW6x55RSoHDeMrd9pgSA8T', # one of the node_id that is part of the network
                    network_name='<network_name>', # this assume this network is already provisioned on the node
                    ip_address='10.80.1.10', # part of ip_range you reserved for your network xxx.xxx.1.10
                    flist='https://hub.grid.tf/tf-bootable/3bot-ubuntu-20.04.flist', # flist of the container you want to install
                    interactive=True,         # True only if corex_connect required, default false
                    #env={"pub_key":"YOUR_PUBLIC_KEY"},                   # field for parameters like config
                    entrypoint='/bin/bash /start.sh')

expiration = j.data.time.get().timestamp +3900
# register the reservation
registered_reservation = zos.reservation_register(r, expiration)
time.sleep(5)
# inspect the result of the reservation provisioning
```

## Create Wallet:
```python
from jumpscale.clients.stellar.stellar import _NETWORK_KNOWN_TRUSTS
def create_wallet(name):
        explorer = j.core.identity.me.explorer
        wallettype = "STD"

        # Why while not if?
        while j.clients.stellar.find(name):
            raise j.exceptions.Value("Name already exists")
        wallet = j.clients.stellar.new(name=name, network=wallettype)

        try:
            wallet.activate_through_threefold_service()
        except Exception:
            j.clients.stellar.delete(name=name)
            raise j.exceptions.JSException("Error on wallet activation")

        trustlines = _NETWORK_KNOWN_TRUSTS[str(wallet.network.name)].copy()
        for asset_code in trustlines.keys():
            wallet.add_known_trustline(asset_code)

        wallet.save()
        return wallet

wallet = create_wallet("wallet_name")
```
## Get TFT

TODO: add wiki link here.
See [here](https://github.com/threefoldtech/js-sdk/blob/development/docs/wiki/tutorials/add_funds_to_wallet.md)

## Get balance of your wallet
```python
wallet.get_balance()
```
## Pay for your ubuntu container
```python
j.sals.zos.get().billing.payout_farmers(wallet,reservation_response= registered_reservation)

result = zos.reservation_result(registered_reservation.reservation_id)

print("provisioning result")
print(result)
```

## access your ubuntu container using ssh

```bash
ssh roo@10.80.1.10
```

## access your ubuntu container using web

```bash
10.80.1.10:7681
```
- run bash  to goto into container
```bash
10.80.1.10:7681/api/process/start?arg[]=/bin/bash
```
Then refresh page and press on job id
