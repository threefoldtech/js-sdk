# GENERATED CLASS DONT EDIT
from jumpscale.core.base import Base, fields
from enum import Enum
import ipaddress
from datetime import datetime


class Currency(Enum):
    Eur = 0
    Usd = 1
    Tft = 2
    Aed = 3
    Gbp = 4


class Type(Enum):
    Macvlan = 0
    Vlan = 1


class NextAction(Enum):
    CREATE = 0
    SIGN = 1
    PAY = 2
    DEPLOY = 3
    DELETE = 4
    INVALID = 5
    DELETED = 6


class Category(Enum):
    Zdb = 0
    Container = 1
    Volume = 2
    Network = 3
    Kubernetes = 4
    Proxy = 5
    Reverse_proxy = 6
    Subdomain = 7
    Domain_delegate = 8
    Gateway4to6 = 9


class State(Enum):
    Error = 0
    Ok = 1
    Deleted = 2


class Type(Enum):
    Zdb = 0
    Container = 1
    Volume = 2
    Network = 3
    Kubernetes = 4
    Proxie = 5
    Reverse_proxie = 6
    Subdomain = 7
    Domain_delegate = 8


class Mode(Enum):
    Seq = 0
    User = 1


class DiskType(Enum):
    HDD = 0
    SSD = 1


class TfgridDeployed_reservation1(Base):
    reservation_id = fields.Integer()
    customer_tid = fields.Integer()


class TfgridDirectoryWallet_address1(Base):
    asset = fields.String(default="")
    address = fields.String(default="")


class TfgridDirectoryNodeResourcePrice1(Base):
    currency = fields.Enum(Currency)
    cru = fields.Float()
    mru = fields.Float()
    hru = fields.Float()
    sru = fields.Float()
    nru = fields.Float()


class TfgridDirectoryLocation1(Base):
    city = fields.String(default="")
    country = fields.String(default="")
    continent = fields.String(default="")
    latitude = fields.Float()
    longitude = fields.Float()


class TfgridDirectoryNodeIface1(Base):
    name = fields.String(default="")
    addrs = fields.List(fields.IPRange())
    gateway = fields.List(fields.IPRange())


class TfgridDirectoryNodePublic_iface1(Base):
    master = fields.String(default="")
    type = fields.Enum(Type)
    ipv4 = fields.IPRange()
    ipv6 = fields.IPRange()
    gw4 = fields.IPRange()
    gw6 = fields.IPRange()
    version = fields.Integer()


class TfgridDirectoryNodeResourceAmount1(Base):
    cru = fields.Integer()
    mru = fields.Integer()
    hru = fields.Integer()
    sru = fields.Integer()


class TfgridDirectoryNodeResourceWorkloads1(Base):
    network = fields.Integer()
    volume = fields.Integer()
    zdb_namespace = fields.Integer()
    container = fields.Integer()
    k8s_vm = fields.Integer()
    proxy = fields.Integer()
    reverse_proxy = fields.Integer()
    subdomain = fields.Integer()
    delegate_domain = fields.Integer()


class TfgridDirectoryNodeProof1(Base):
    created = fields.DateTime()
    hardware_hash = fields.String(default="")
    disk_hash = fields.String(default="")
    hardware = fields.Typed(dict)
    disks = fields.Typed(dict)
    hypervisor = fields.List(fields.String())


class TfgridPhonebookUser1(Base):
    id = fields.Integer()
    name = fields.String(default="")
    email = fields.String(default="")
    pubkey = fields.String(default="")
    host = fields.String(default="")
    description = fields.String(default="")
    signature = fields.String(default="")


class TfgridWorkloadActionable1(Base):
    workload_id = fields.String(default="")
    node_id = fields.String(default="")


class TfgridWorkloadsReservationSigningRequest1(Base):
    signers = fields.List(fields.Integer())
    quorum_min = fields.Integer()


class TfgridWorkloadsReservationSigningSignature1(Base):
    tid = fields.Integer()
    signature = fields.String(default="")
    epoch = fields.DateTime()


class TfgridWorkloadsReservationEscrowDetail1(Base):
    farmer_id = fields.Integer()
    total_amount = fields.Float()


class TfgridWorkloadsReservationContainerMount1(Base):
    volume_id = fields.String(default="")
    mountpoint = fields.String(default="")


class TfgridWorkloadsReservationNetworkConnection1(Base):
    network_id = fields.String(default="")
    ipaddress = fields.IPAddress()
    public_ip6 = fields.Boolean()


class TfgridWorkloadsReservationContainerLogsredis1(Base):
    stdout = fields.String(default="")
    stderr = fields.String(default="")


class TfgridWorkloadsReservationContainerLogs1(Base):
    type = fields.String(default="")
    data = fields.Object(TfgridWorkloadsReservationContainerLogsredis1)


class TfgridWorkloadsReservationContainerCapacity1(Base):
    cpu = fields.Integer()
    memory = fields.Integer()
    disk_size = fields.Integer()
    disk_type = fields.Enum(DiskType)


class TfgridWorkloadsReservationGatewayProxy1(Base):
    workload_id = fields.Integer()
    node_id = fields.String(default="")
    domain = fields.String(default="")
    addr = fields.String(default="")
    port = fields.Integer()
    port_tls = fields.Integer()


class TfgridWorkloadsReservationGatewayReverse_proxy1(Base):
    workload_id = fields.Integer()
    node_id = fields.String(default="")
    domain = fields.String(default="")
    secret = fields.String(default="")


class TfgridWorkloadsReservationGatewaySubdomain1(Base):
    workload_id = fields.Integer()
    node_id = fields.String(default="")
    domain = fields.String(default="")
    ips = fields.List(fields.String())


class TfgridWorkloadsReservationGatewayDelegate1(Base):
    workload_id = fields.Integer()
    node_id = fields.String(default="")
    domain = fields.String(default="")


class TfgridWorkloadsReservationGateway4to61(Base):
    workload_id = fields.Integer()
    node_id = fields.String(default="")
    public_key = fields.String(default="")


class TfgridWorkloadsReservationStatsaggregator1(Base):
    addr = fields.String(default="")
    port = fields.Integer()
    secret = fields.String(default="")


class TfgridWorkloadsReservationK8s1(Base):
    workload_id = fields.Integer()
    node_id = fields.String(default="")
    size = fields.Integer()
    network_id = fields.String(default="")
    ipaddress = fields.IPAddress()
    cluster_secret = fields.String(default="")
    master_ips = fields.List(fields.IPAddress())
    ssh_keys = fields.List(fields.String())
    stats_aggregator = fields.List(fields.Object(TfgridWorkloadsReservationStatsaggregator1))
    farmer_tid = fields.Integer()


class TfgridWorkloadsWireguardPeer1(Base):
    public_key = fields.String(default="")
    allowed_iprange = fields.List(fields.IPRange())
    endpoint = fields.String(default="")
    iprange = fields.IPRange(default="10.10.11.0/24")


class TfgridWorkloadsReservationResult1(Base):
    category = fields.Enum(Category)
    workload_id = fields.String(default="")
    data_json = fields.Json()
    signature = fields.Bytes()
    state = fields.Enum(State)
    message = fields.String(default="")
    epoch = fields.DateTime()


class TfgridWorkloadsReservationWorkload1(Base):
    workload_id = fields.String(default="")
    user = fields.String(default="")
    type = fields.Enum(Type)
    content = fields.Typed(dict)
    created = fields.DateTime()
    duration = fields.Integer()
    signature = fields.String(default="")
    to_delete = fields.Boolean()


class TfgridDirectoryFarm1(Base):
    id = fields.Integer()
    threebot_id = fields.Integer()
    iyo_organization = fields.String(default="")
    name = fields.String(default="")
    wallet_addresses = fields.List(fields.Object(TfgridDirectoryWallet_address1))
    location = fields.Object(TfgridDirectoryLocation1)
    email = fields.Email()
    resource_prices = fields.List(fields.Object(TfgridDirectoryNodeResourcePrice1))
    prefix_zero = fields.IPRange()


class TfgridDirectoryGateway1(Base):
    node_id = fields.String(default="")
    os_version = fields.String(default="")
    farm_id = fields.Integer()
    created = fields.DateTime()
    updated = fields.DateTime()
    uptime = fields.Integer()
    address = fields.String(default="")
    location = fields.Object(TfgridDirectoryLocation1)
    public_key_hex = fields.String(default="")
    workloads = fields.Object(TfgridDirectoryNodeResourceWorkloads1)
    managed_domains = fields.List(fields.String())
    tcp_router_port = fields.Integer()
    dns_nameserver = fields.List(fields.String())
    free_to_use = fields.Boolean()


class TfgridDirectoryNode2(Base):
    node_id = fields.String(default="")
    node_id_v1 = fields.String(default="")
    farm_id = fields.Integer()
    os_version = fields.String(default="")
    created = fields.DateTime()
    updated = fields.DateTime()
    uptime = fields.Integer()
    address = fields.String(default="")
    location = fields.Object(TfgridDirectoryLocation1)
    total_resources = fields.Object(TfgridDirectoryNodeResourceAmount1)
    used_resources = fields.Object(TfgridDirectoryNodeResourceAmount1)
    reserved_resources = fields.Object(TfgridDirectoryNodeResourceAmount1)
    workloads = fields.Object(TfgridDirectoryNodeResourceWorkloads1)
    proofs = fields.List(fields.Object(TfgridDirectoryNodeProof1))
    ifaces = fields.List(fields.Object(TfgridDirectoryNodeIface1))
    public_config = fields.Object(TfgridDirectoryNodePublic_iface1)
    exit_node = fields.Boolean()
    approved = fields.Boolean(default=False)
    public_key_hex = fields.String(default="")
    wg_ports = fields.List(fields.Integer())
    free_to_use = fields.Boolean()


class TfgridDomainsDelegate1(Base):
    gateway = fields.Object(TfgridDirectoryGateway1)
    domain = fields.String(default="")


class TfgridDomainsSub1(Base):
    gateway_id = fields.Object(TfgridDirectoryGateway1)
    subdomain = fields.String(default="")
    domain = fields.String(default="")


class TfgridWorkloadsReservationEscrow1(Base):
    address = fields.String(default="")
    asset = fields.String(default="")
    details = fields.List(fields.Object(TfgridWorkloadsReservationEscrowDetail1))


class TfgridWorkloadsReservationCreate1(Base):
    reservation_id = fields.Integer()
    escrow_information = fields.Object(TfgridWorkloadsReservationEscrow1)


class TfgridWorkloadsReservationContainer1(Base):
    workload_id = fields.Integer()
    node_id = fields.String(default="")
    flist = fields.String(default="")
    storage_url = fields.String(default="")
    environment = fields.Typed(dict)
    secret_environment = fields.Typed(dict)
    entrypoint = fields.String(default="")
    interactive = fields.Boolean(default=True)
    volumes = fields.List(fields.Object(TfgridWorkloadsReservationContainerMount1))
    network_connection = fields.List(fields.Object(TfgridWorkloadsReservationNetworkConnection1))
    stats_aggregator = fields.List(fields.Object(TfgridWorkloadsReservationStatsaggregator1))
    farmer_tid = fields.Integer()
    logs = fields.List(fields.Object(TfgridWorkloadsReservationContainerLogs1))
    capacity = fields.Object(TfgridWorkloadsReservationContainerCapacity1)


class TfgridWorkloadsNetworkNet_resource1(Base):
    node_id = fields.String(default="")
    wireguard_private_key_encrypted = fields.String(default="")
    wireguard_public_key = fields.String(default="")
    wireguard_listen_port = fields.Integer()
    iprange = fields.IPRange(default="10.10.10.0/24")
    peers = fields.List(fields.Object(TfgridWorkloadsWireguardPeer1))


class TfgridWorkloadsReservationNetwork1(Base):
    name = fields.String(default="")
    workload_id = fields.Integer()
    iprange = fields.IPRange(default="10.10.0.0/16")
    stats_aggregator = fields.List(fields.Object(TfgridWorkloadsReservationStatsaggregator1))
    network_resources = fields.List(fields.Object(TfgridWorkloadsNetworkNet_resource1))
    farmer_tid = fields.Integer()


class TfgridWorkloadsReservationVolume1(Base):
    workload_id = fields.Integer()
    node_id = fields.String(default="")
    size = fields.Integer()
    type = fields.Enum(DiskType)
    stats_aggregator = fields.List(fields.Object(TfgridWorkloadsReservationStatsaggregator1))
    farmer_tid = fields.Integer()


class TfgridWorkloadsReservationZdb1(Base):
    workload_id = fields.Integer()
    node_id = fields.String(default="")
    size = fields.Integer()
    mode = fields.Enum(Mode)
    password = fields.String(default="")
    disk_type = fields.Enum(DiskType)
    public = fields.Boolean(default=False)
    stats_aggregator = fields.List(fields.Object(TfgridWorkloadsReservationStatsaggregator1))
    farmer_tid = fields.Integer()


class TfgridWorkloadsReservationData1(Base):
    description = fields.String(default="")
    signing_request_provision = fields.Object(TfgridWorkloadsReservationSigningRequest1)
    signing_request_delete = fields.Object(TfgridWorkloadsReservationSigningRequest1)
    containers = fields.List(fields.Object(TfgridWorkloadsReservationContainer1))
    volumes = fields.List(fields.Object(TfgridWorkloadsReservationVolume1))
    zdbs = fields.List(fields.Object(TfgridWorkloadsReservationZdb1))
    networks = fields.List(fields.Object(TfgridWorkloadsReservationNetwork1))
    kubernetes = fields.List(fields.Object(TfgridWorkloadsReservationK8s1))
    proxies = fields.List(fields.Object(TfgridWorkloadsReservationGatewayProxy1))
    reverse_proxies = fields.List(fields.Object(TfgridWorkloadsReservationGatewayReverse_proxy1))
    subdomains = fields.List(fields.Object(TfgridWorkloadsReservationGatewaySubdomain1))
    domain_delegates = fields.List(fields.Object(TfgridWorkloadsReservationGatewayDelegate1))
    gateway4to6 = fields.List(fields.Object(TfgridWorkloadsReservationGateway4to61))
    expiration_provisioning = fields.DateTime()
    expiration_reservation = fields.DateTime()
    currencies = fields.List(fields.String())


class TfgridWorkloadsReservation1(Base):
    id = fields.Integer()
    json = fields.String(default="")
    data_reservation = fields.Object(TfgridWorkloadsReservationData1)
    customer_tid = fields.Integer()
    customer_signature = fields.String(default="")
    next_action = fields.Enum(NextAction)
    signatures_provision = fields.List(fields.Object(TfgridWorkloadsReservationSigningSignature1))
    signatures_farmer = fields.List(fields.Object(TfgridWorkloadsReservationSigningSignature1))
    signatures_delete = fields.List(fields.Object(TfgridWorkloadsReservationSigningSignature1))
    epoch = fields.DateTime(default=datetime.utcnow)
    metadata = fields.String(default="")
    results = fields.List(fields.Object(TfgridWorkloadsReservationResult1))
