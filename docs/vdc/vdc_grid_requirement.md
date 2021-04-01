# Grid Requirement

## VDC Capacity Provider

### Farm Resources

To have a VDC deployer, it needs a farm with the following resources:

- Public IPv4 addresses

    These addresses will be assigned to each VDC to be accessed through public network.

- IPv4 access node

    At least one node for private network creation.

- IPv6 access node

    At least one node for private network creation.

- Nodes with CPU, Memory, and SSD disks

    These nodes will be used to deploy Kubernetes clusters.

- Nodes with IPv6 interface and HDD disks

    These nodes will be used to deploy ZDBs that used as storage nodes.

**Important Notes:**

- The nodes needed can have all resources together so they can be used for deploying kubernetes clusters or storage nodes.

### How to use this farm

Changes needed to be done in the code to use this farm in [size.py](https://github.com/threefoldtech/js-sdk/blob/development/jumpscale/sals/vdc/size.py):

- NETWORK_FARM
- ZDB_FARMS
- S3_AUTO_TOPUP_FARMS
- PREFERED_FARM
- PROXY_FARM

**Example**
Change network farm to `myfarm` on all explorers.

```python
class NETWORK_FARM(FarmConfigBase):
    KEY = "NETWORK_FARM"
    devnet = "myfarm"
    testnet = "myfarm"
    mainnet = "myfarm"
```

## Storage Provider

To be a storage provider, it needs a farm with the following resources:

- Nodes with IPv6 interface and HDD disks

    These nodes will be used to deploy ZDBs that used as storage nodes.

**Notes:**

- No need to configure something else, it will appear in the VDC deployer in `Manually Select Farms`.
- If this farm needed to be used for all ZDBs deployment, it will need 10 nodes at least.
- If this farm will be used beside another farms, it will need at least number of nodes equals to the division 10 ZDBs by the number of farms used.
