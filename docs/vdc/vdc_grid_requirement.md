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

    These nodes will be used to deploy ZDBs that used as storage containers.

**Important Notes:**

- The nodes needed can have all resources together so they can be used for deploying kubernetes clusters or storage containers.

### How to use this farm

If there are 3 farms called `mydevfarm`, `mytestfarm`, and `myfarm`, then they are needed to be used for devnet, testnet, and mainnet explorers, respectively. The following steps should be done:

- A json file should be written as the following

  ```json
    {
        "NETWORK_FARMS": {
            "devnet": [
                "mydevfarm"
            ],
            "testnet": [
                "mytestfarm"
            ],
            "mainnet": [
                "myfarm"
            ]
        },
        "COMPUTE_FARMS": {
            "devnet": [
                "mydevfarm"
            ],
            "testnet": [
                "mytestfarm"
            ],
            "mainnet": [
                "myfarm"
            ]
        },
        "ZDB_FARMS": {
            "devnet": [
                "mydevfarm"
            ],
            "testnet": [
                "mytestfarm"
            ],
            "mainnet": [
                "myfarm"
            ]
        },
        "S3_AUTO_TOPUP_FARMS": {
            "devnet": [
                "mydevfarm"
            ],
            "testnet": [
                "mytestfarm"
            ],
            "mainnet": [
                "myfarm"
            ]
        },
        "PROXY_FARMS": {
            "devnet": [
                "mytestfarm"
            ],
            "testnet": [
                "mytestfarm"
            ],
            "mainnet": [
                "myfarm"
            ]
        }
    }
  ```

- Set the path of the farm's configuration to the json file has been written

  ```python
  j.config.set("VDC_FARMS_CONFIG", "</path/to/the/json/file>")
  ```

## Storage Provider

To be a storage provider, it needs a farm with the following resources:

- Nodes with IPv6 interface and HDD disks

    These nodes will be used to deploy ZDBs that used as storage containers.

**Notes:**

- No need to configure something else, it will appear in the VDC deployer in `Manually Select Farms`.
- If this farm needed to be used for all ZDBs deployment, it will need 10 nodes at least.
- If this farm will be used beside another farms, it will need at least number of nodes equals to the division 10 ZDBs by the number of farms used.
