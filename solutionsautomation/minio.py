from gedispatch import GedisChatBotPatch
from jumpscale.packages.tfgrid_solutions.chats.minio import MinioDeploy


class MinioAutomated(GedisChatBotPatch, MinioDeploy):
    NAME_MESSAGE = "Please enter a name for your workload (Can be used to prepare domain for you and needed to track your solution on the grid)"
    SETUP_MESSAGE = "Please choose the type of setup you need. Single setup is the basic setup while master/slave setup includes TLOG use to be able to reconstruct the metadata"
    ZDB_DISK_TYPE_MESSAGE = "Please choose a the type of disk for zdb"
    CPU_MESSAGE = "Please specify how many CPUs"
    MEM_MESSAGE = "Please specify how much memory (in MB)"
    DATA_SHARDS_MESSAGE = "Please add the number of locations you need. Take care of the ratio between the locations and locations allowed to fail that you will specify next"
    PARITY_SHARDS_MESSAGE = "Please add the number of locations allowed to fail"
    ZDB_POOLS_MESSAGE = "Please select the pools you wish to distribute you ZDB workloads on"
    USERNAME_MESSAGE = "Please add the key to be used for minio when logging in. Make sure not to lose it"
    PASSWORD_MESSAGE = (
        "Please add the secret to be used for minio when logging in to match the previous key. Make sure not to lose it"
    )
    NETWORK_MESSAGE = "Please select a network"
    LOG_MESSAGE = "Do you want to push the container logs (stdout and stderr) onto an external redis channel"
    SSH_MESSAGE = (
        "Please add your public ssh key, this will allow you to access the deployed minio container using ssh."
    )
    IP_MESSAGE = r"^Please choose IP Address for (.*) container$"
    IPV6_MESSAGE = r"^Do you want to assign a global IPv6 address to (.*)\?$"
    NODE_ID_MESSAGE = r"^Do you want to automatically select a node for deployment for (.*)\?$"
    POOL_MESSAGE = r"^Please select a pool( for (.*))?$"
    NODE_SELECTION_MESSAGE = r"^Please choose the node you want to deploy (.*) on$"

    QS = {
        # strs
        NAME_MESSAGE: "get_name",
        SSH_MESSAGE: "ssh",
        USERNAME_MESSAGE: "username",
        PASSWORD_MESSAGE: "password",
        # ints
        CPU_MESSAGE: "cpu",
        MEM_MESSAGE: "memory",
        DATA_SHARDS_MESSAGE: "data_shards",
        PARITY_SHARDS_MESSAGE: "parity_shards",
        # single choice
        SETUP_MESSAGE: "setup",
        ZDB_DISK_TYPE_MESSAGE: "zdb_disk_type",
        NETWORK_MESSAGE: "choose_random",
        LOG_MESSAGE: "log",
        IP_MESSAGE: "choose_random",
        IPV6_MESSAGE: "ipv6",
        POOL_MESSAGE: "choose_random",
        NODE_ID_MESSAGE: "node_automatic",
        NODE_SELECTION_MESSAGE: "choose_random",
        # multi choice
        ZDB_POOLS_MESSAGE: "multi_choice",
    }


test = MinioAutomated(
    solution_name="minio",
    currency="TFT",
    setup="single",
    zdb_disk_type="SSD",
    cpu=1,
    memory=1024,
    data_shards=2,
    parity_shards=1,
    username="test",
    password="test12345",
    log="NO",
    ssh="~/.ssh/id_rsa.pub",
    ipv6="NO",
    node_automatic="NO",
    debug=True,
)
