import ipaddress
from datetime import datetime
from enum import Enum

from jumpscale.core.base import Base, fields


"""
Explorer directory types
"""


class Currency(Enum):
    Eur = 0
    Usd = 1
    Tft = 2
    Aed = 3
    Gbp = 4


class WalletAddress(Base):
    asset = fields.String(default="")
    address = fields.String(default="")


class ResourceUnitPrice(Base):
    currency = fields.Enum(Currency)
    cru = fields.Float()
    mru = fields.Float()
    hru = fields.Float()
    sru = fields.Float()
    nru = fields.Float()


class Location(Base):
    city = fields.String(default="")
    country = fields.String(default="")
    continent = fields.String(default="")
    latitude = fields.Float()
    longitude = fields.Float()

    def __str__(self):
        return ",".join([x for x in [self.continent, self.country, self.city] if x])

class Farm(Base):
    id = fields.Integer()
    threebot_id = fields.Integer()
    iyo_organization = fields.String(default="")
    name = fields.String(default="")
    wallet_addresses = fields.List(fields.Object(WalletAddress))
    location = fields.Object(Location)
    email = fields.Email()
    resource_prices = fields.List(fields.Object(ResourceUnitPrice))
    prefix_zero = fields.IPRange()

    def __str__(self):
        return " - ".join([x for x in [self.name, str(self.location)] if x])
        


class WorkloadsAmount(Base):
    network = fields.Integer()
    volume = fields.Integer()
    zdb_namespace = fields.Integer()
    container = fields.Integer()
    k8s_vm = fields.Integer()
    proxy = fields.Integer()
    reverse_proxy = fields.Integer()
    subdomain = fields.Integer()
    delegate_domain = fields.Integer()


class Gateway(Base):
    node_id = fields.String(default="")
    os_version = fields.String(default="")
    farm_id = fields.Integer()
    created = fields.DateTime()
    updated = fields.DateTime()
    uptime = fields.Integer()
    address = fields.String(default="")
    location = fields.Object(Location)
    public_key_hex = fields.String(default="")
    workloads = fields.Object(WorkloadsAmount)
    managed_domains = fields.List(fields.String())
    tcp_router_port = fields.Integer()
    dns_nameserver = fields.List(fields.String())
    free_to_use = fields.Boolean()


class NodeIface(Base):
    name = fields.String(default="")
    addrs = fields.List(fields.IPRange())
    gateway = fields.List(fields.IPRange())


class ResourceUnitAmount(Base):
    cru = fields.Integer()
    mru = fields.Integer()
    hru = fields.Integer()
    sru = fields.Integer()


class NicType(Enum):
    Macvlan = 0
    Vlan = 1


class NodePublicIface(Base):
    master = fields.String(default="")
    type = fields.Enum(NicType)
    ipv4 = fields.IPRange()
    ipv6 = fields.IPRange()
    gw4 = fields.IPRange()
    gw6 = fields.IPRange()
    version = fields.Integer()


class HardwareProof(Base):
    created = fields.DateTime()
    hardware_hash = fields.String(default="")
    disk_hash = fields.String(default="")
    hardware = fields.Typed(dict)
    disks = fields.Typed(dict)
    hypervisor = fields.List(fields.String())


class Node(Base):
    node_id = fields.String(default="")
    node_id_v1 = fields.String(default="")
    farm_id = fields.Integer()
    os_version = fields.String(default="")
    created = fields.DateTime()
    updated = fields.DateTime()
    uptime = fields.Integer()
    address = fields.String(default="")
    location = fields.Object(Location)
    total_resources = fields.Object(ResourceUnitAmount)
    used_resources = fields.Object(ResourceUnitAmount)
    reserved_resources = fields.Object(ResourceUnitAmount)
    workloads = fields.Object(WorkloadsAmount)
    proofs = fields.List(fields.Object(HardwareProof))
    ifaces = fields.List(fields.Object(NodeIface))
    public_config = fields.Object(NodePublicIface)
    exit_node = fields.Boolean()
    approved = fields.Boolean(default=False)
    public_key_hex = fields.String(default="")
    wg_ports = fields.List(fields.Integer())
    free_to_use = fields.Boolean()


"""
Explorer phonebook types
"""


class User(Base):
    id = fields.Integer()
    name = fields.String(default="")
    email = fields.String(default="")
    pubkey = fields.String(default="")
    host = fields.String(default="")
    description = fields.String(default="")
    signature = fields.String(default="")


"""
Explorer worklaods types
"""


class NextAction(Enum):
    CREATE = 0
    SIGN = 1
    PAY = 2
    DEPLOY = 3
    DELETE = 4
    INVALID = 5
    DELETED = 6
    MIGRATED = 7


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


class WorkloadType(Enum):
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
    Network_resource = 10


class ZDBMode(Enum):
    Seq = 0
    User = 1


class DiskType(Enum):
    HDD = 0
    SSD = 1


class DeployedReservation(Base):
    reservation_id = fields.Integer()
    customer_tid = fields.Integer()


class SigningRequest(Base):
    signers = fields.List(fields.Integer())
    quorum_min = fields.Integer()


class Signature(Base):
    tid = fields.Integer()
    signature = fields.String(default="")
    epoch = fields.DateTime()


class ContainerMount(Base):
    volume_id = fields.String(default="")
    mountpoint = fields.String(default="")


class ContainerNetworkConnection(Base):
    network_id = fields.String(default="")
    ipaddress = fields.IPAddress()
    public_ip6 = fields.Boolean()


class ContainerLogsRedis(Base):
    stdout = fields.String(default="")
    stderr = fields.String(default="")


class ContainerLogs(Base):
    type = fields.String(default="")
    data = fields.Object(ContainerLogsRedis)


class ContainerCapacity(Base):
    cpu = fields.Integer()
    memory = fields.Integer()
    disk_size = fields.Integer()
    disk_type = fields.Enum(DiskType)


class ReservationResult(Base):
    category = fields.Enum(Category)
    workload_id = fields.String(default="")
    data_json = fields.Json()
    signature = fields.Bytes()
    state = fields.Enum(State)
    message = fields.String(default="")
    epoch = fields.DateTime()


class ReservationInfo(Base):
    workload_id = fields.Integer()
    node_id = fields.String()
    pool_id = fields.Integer()
    description = fields.String(default="")
    reference = fields.String(default="")
    customer_tid = fields.Integer()
    customer_signature = fields.String()
    next_action = fields.Enum(NextAction)
    signatures_provision = fields.List(fields.Object(Signature))
    signing_request_provision = fields.Object(SigningRequest)
    signing_request_delete = fields.Object(SigningRequest)
    signatures_farmer = fields.List(fields.Object(Signature))
    signatures_delete = fields.List(fields.Object(Signature))
    epoch = fields.DateTime(default=datetime.utcnow)
    metadata = fields.String(default="")
    result = fields.Object(ReservationResult)
    workload_type = fields.Enum(WorkloadType)


class GatewayProxy(Base):
    id = fields.Integer()
    domain = fields.String(default="")
    addr = fields.String(default="")
    port = fields.Integer()
    port_tls = fields.Integer()
    info = fields.Object(ReservationInfo)


class GatewayReverseProxy(Base):
    id = fields.Integer()
    domain = fields.String(default="")
    secret = fields.String(default="")
    info = fields.Object(ReservationInfo)


class GatewaySubdomain(Base):
    id = fields.Integer()
    domain = fields.String(default="")
    ips = fields.List(fields.String())
    info = fields.Object(ReservationInfo)


class GatewayDelegate(Base):
    id = fields.Integer()
    domain = fields.String(default="")
    info = fields.Object(ReservationInfo)


class Gateway4to6(Base):
    id = fields.Integer()
    public_key = fields.String(default="")
    info = fields.Object(ReservationInfo)


class Statsaggregator(Base):
    addr = fields.String(default="")
    port = fields.Integer()
    secret = fields.String(default="")


class K8s(Base):
    id = fields.Integer()
    size = fields.Integer()
    network_id = fields.String(default="")
    ipaddress = fields.IPAddress()
    cluster_secret = fields.String(default="")
    master_ips = fields.List(fields.IPAddress())
    ssh_keys = fields.List(fields.String())
    stats_aggregator = fields.List(fields.Object(Statsaggregator))
    info = fields.Object(ReservationInfo)


class WireguardPeer(Base):
    public_key = fields.String(default="")
    allowed_iprange = fields.List(fields.IPRange())
    endpoint = fields.String(default="")
    iprange = fields.IPRange(default="10.10.11.0/24")


# class Workload(Base):
#     workload_id = fields.String(default="")
#     user = fields.String(default="")
#     type = fields.Enum(WorkloadType)
#     content = fields.Typed(dict)
#     created = fields.DateTime()
#     duration = fields.Integer()
#     signature = fields.String(default="")
#     to_delete = fields.Boolean()


class EscrowDetail(Base):
    farmer_id = fields.Integer()
    total_amount = fields.Float()


class Escrow(Base):
    address = fields.String(default="")
    asset = fields.String(default="")
    details = fields.List(fields.Object(EscrowDetail))


class PaymentDetail(Base):
    reservation_id = fields.Integer()
    escrow_information = fields.Object(EscrowDetail)


class Container(Base):
    id = fields.Integer()
    flist = fields.String(default="")
    hub_url = fields.String(default="")
    storage_url = fields.String(default="")
    environment = fields.Typed(dict)
    secret_environment = fields.Typed(dict)
    entrypoint = fields.String(default="")
    interactive = fields.Boolean(default=True)
    volumes = fields.List(fields.Object(ContainerMount))
    network_connection = fields.List(fields.Object(ContainerNetworkConnection))
    stats_aggregator = fields.List(fields.Object(Statsaggregator))
    farmer_tid = fields.Integer()
    logs = fields.List(fields.Object(ContainerLogs))
    capacity = fields.Object(ContainerCapacity)
    info = fields.Object(ReservationInfo)


class NetworkResource(Base):
    id = fields.Integer()
    name = fields.String(default="")
    network_iprange = fields.IPRange(default="10.10.0.0/16")
    wireguard_private_key_encrypted = fields.String(default="")
    wireguard_public_key = fields.String(default="")
    wireguard_listen_port = fields.Integer()
    iprange = fields.IPRange(default="10.10.10.0/24")
    peers = fields.List(fields.Object(WireguardPeer))
    info = fields.Object(ReservationInfo)


class Network(Base):
    name = fields.String(default="")
    workload_id = fields.Integer()
    iprange = fields.IPRange(default="10.10.0.0/16")
    stats_aggregator = fields.List(fields.Object(Statsaggregator))
    network_resources = fields.List(fields.Object(NetworkResource))
    farmer_tid = fields.Integer()


class Volume(Base):
    id = fields.Integer()
    size = fields.Integer()
    type = fields.Enum(DiskType)
    stats_aggregator = fields.List(fields.Object(Statsaggregator))
    info = fields.Object(ReservationInfo)


class ZdbNamespace(Base):
    id = fields.Integer()
    node_id = fields.String(default="")
    size = fields.Integer()
    mode = fields.Enum(ZDBMode)
    password = fields.String(default="")
    disk_type = fields.Enum(DiskType)
    public = fields.Boolean(default=False)
    stats_aggregator = fields.List(fields.Object(Statsaggregator))
    info = fields.Object(ReservationInfo)


class ReservationData(Base):
    description = fields.String(default="")
    signing_request_provision = fields.Object(SigningRequest)
    signing_request_delete = fields.Object(SigningRequest)
    containers = fields.List(fields.Object(Container))
    volumes = fields.List(fields.Object(Volume))
    zdbs = fields.List(fields.Object(ZdbNamespace))
    networks = fields.List(fields.Object(Network))
    kubernetes = fields.List(fields.Object(K8s))
    proxies = fields.List(fields.Object(GatewayProxy))
    reverse_proxies = fields.List(fields.Object(GatewayReverseProxy))
    subdomains = fields.List(fields.Object(GatewaySubdomain))
    domain_delegates = fields.List(fields.Object(GatewayDelegate))
    gateway4to6 = fields.List(fields.Object(Gateway4to6))
    expiration_provisioning = fields.DateTime()
    expiration_reservation = fields.DateTime()
    currencies = fields.List(fields.String())


class Reservation(Base):
    id = fields.Integer()
    json = fields.String(default="")
    data_reservation = fields.Object(ReservationData)
    customer_tid = fields.Integer()
    customer_signature = fields.String(default="")
    next_action = fields.Enum(NextAction)
    signatures_provision = fields.List(fields.Object(Signature))
    signatures_farmer = fields.List(fields.Object(Signature))
    signatures_delete = fields.List(fields.Object(Signature))
    epoch = fields.DateTime(default=datetime.utcnow)
    metadata = fields.String(default="")
    results = fields.List(fields.Object(ReservationResult))


class PoolCreateData(Base):
    pool_id = fields.Integer()
    cus = fields.Integer()
    sus = fields.Integer()
    node_ids = fields.List(fields.String())
    currencies = fields.List(fields.String())


class PoolCreate(Base):
    json = fields.String()
    data_reservation = fields.Object(PoolCreateData)
    customer_tid = fields.Integer()
    customer_signature = fields.String()


class Pool(Base):
    pool_id = fields.Integer()
    cus = fields.Float()
    sus = fields.Float()
    node_ids = fields.List(fields.String())
    last_updated = fields.DateTime()
    active_cu = fields.Float()
    active_su = fields.Float()
    empty_at = fields.Integer()  # can't be set to date because of max int64 value
    customer_tid = fields.Integer()
    active_workload_ids = fields.List(fields.Integer())


class PoolEscrow(Base):
    address = fields.String()
    asset = fields.String()
    amount = fields.Integer()


class PoolCreated(Base):
    reservation_id = fields.Integer()
    escrow_information = fields.Object(PoolEscrow)
