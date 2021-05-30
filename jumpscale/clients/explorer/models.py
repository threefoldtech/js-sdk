import ipaddress
from datetime import datetime
from enum import Enum
from collections import OrderedDict

from jumpscale.core.base import Base, fields
from jumpscale.loader import j

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


class FarmerIP(Base):
    address = fields.IPRange()
    gateway = fields.IPAddress()
    reservation_id = fields.Integer()


class CloudUnitMonthPrice(Base):
    cu = fields.Float(default=10)
    su = fields.Float(default=8)
    ipv4u = fields.Float(default=6)


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
    ipaddresses = fields.List(fields.Object(FarmerIP))
    enable_custom_pricing = fields.Boolean(default=False)
    farm_cloudunits_price = fields.Object(CloudUnitMonthPrice)
    is_grid3_compliant = fields.Boolean(default=False)

    def __str__(self):
        return " - ".join([x for x in [self.name, str(self.location)] if x])


class FarmThreebotPrice(Base):
    threebot_id = fields.Integer()
    farm_id = fields.Integer()
    custom_cloudunits_price = fields.Object(CloudUnitMonthPrice)


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


class CloudUnits(Base):
    # compute units
    cu = fields.Float()
    # storage units
    su = fields.Float()
    # ipv4 units
    ipv4u = fields.Float()

    def cost(self, cu_price, su_price, ipv4u_price, duration):
        """
        compute the total cost

        Args:
            cu_price (float): price of compute unit per second
            su_price (float): price of storage unit per second
            duration (int): duration in second

        Returns:
            [float]: price
        """
        price_per_second = self.cu * cu_price + self.su * su_price + self.ipv4u * ipv4u_price
        return price_per_second * duration


class ResourceUnitAmount(Base):
    cru = fields.Integer()
    mru = fields.Float()
    hru = fields.Float()
    sru = fields.Float()
    ipv4u = fields.Float()

    def cloud_units(self) -> CloudUnits:
        # converts resource units to cloud units. Cloud units are rounded to 3
        # decimal places
        cloud_units = CloudUnits()
        cloud_units.cu = round(min(self.mru / 4, self.cru / 2) * 1000) / 1000
        cloud_units.su = round((self.hru / 1200 + self.sru / 300) * 1000) / 1000
        cloud_units.ipv4u = self.ipv4u
        return cloud_units


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
    hostname = fields.String(default="")
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
    Public_IP = 10


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
    Public_IP = 11
    Virtual_Machine = 12


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
    # deprecated, please use secret_stdout instead
    stdout = fields.String(default="")
    # deprecated, please use secret_stderr instead
    stderr = fields.String(default="")

    secret_stdout = fields.String(default="")
    secret_stderr = fields.String(default="")


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

    def resource_units(self):
        return ResourceUnitAmount()


class GatewayReverseProxy(Base):
    id = fields.Integer()
    domain = fields.String(default="")
    secret = fields.String(default="")
    info = fields.Object(ReservationInfo)

    def resource_units(self):
        return ResourceUnitAmount()


class GatewaySubdomain(Base):
    id = fields.Integer()
    domain = fields.String(default="")
    ips = fields.List(fields.String())
    info = fields.Object(ReservationInfo)

    def resource_units(self):
        return ResourceUnitAmount()


class GatewayDelegate(Base):
    id = fields.Integer()
    domain = fields.String(default="")
    info = fields.Object(ReservationInfo)

    def resource_units(self):
        return ResourceUnitAmount()


class Gateway4to6(Base):
    id = fields.Integer()
    public_key = fields.String(default="")
    info = fields.Object(ReservationInfo)

    def resource_units(self):
        return ResourceUnitAmount()


class Statsaggregator(Base):
    addr = fields.String(default="")
    port = fields.Integer()
    secret = fields.String(default="")


class ContainerStatsRedis(Base):
    endpoint = fields.String(default="")


class ContainerStats(Base):
    type = fields.String(default="")
    data = fields.Object(ContainerStatsRedis)


VMSIZES = OrderedDict(
    {
        1: {"cru": 1, "mru": 2, "sru": 50},
        2: {"cru": 2, "mru": 4, "sru": 100},
        3: {"cru": 2, "mru": 8, "sru": 25},
        4: {"cru": 2, "mru": 5, "sru": 50},
        5: {"cru": 2, "mru": 8, "sru": 200},
        6: {"cru": 4, "mru": 16, "sru": 50},
        7: {"cru": 4, "mru": 16, "sru": 100},
        8: {"cru": 4, "mru": 16, "sru": 400},
        9: {"cru": 8, "mru": 32, "sru": 100},
        10: {"cru": 8, "mru": 32, "sru": 200},
        11: {"cru": 8, "mru": 32, "sru": 800},
        12: {"cru": 16, "mru": 64, "sru": 200},
        13: {"cru": 16, "mru": 64, "sru": 400},
        14: {"cru": 16, "mru": 64, "sru": 800},
        15: {"cru": 1, "mru": 2, "sru": 25},
        16: {"cru": 2, "mru": 4, "sru": 50},
        17: {"cru": 4, "mru": 8, "sru": 50},
        18: {"cru": 1, "mru": 1, "sru": 25},
    }
)


class K8s(Base):
    id = fields.Integer()
    size = fields.Integer()
    network_id = fields.String(default="")
    ipaddress = fields.IPAddress()
    cluster_secret = fields.String(default="")
    master_ips = fields.List(fields.IPAddress())
    ssh_keys = fields.List(fields.String())
    public_ip = fields.Integer()
    stats_aggregator = fields.List(fields.Object(Statsaggregator))
    info = fields.Object(ReservationInfo)
    datastore_endpoint = fields.String(default="")
    disable_default_ingress = fields.Boolean(default=True)

    SIZES = VMSIZES

    def resource_units(self):

        resource_units = ResourceUnitAmount()
        size = VMSIZES.get(self.size)
        if not size:
            raise j.exceptions.Input(f"kubernetes size {self.size} not supported")

        resource_units.cru += size["cru"]
        resource_units.mru += size["mru"]
        resource_units.sru += size["sru"]
        return resource_units


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
    stats = fields.List(fields.Object(ContainerStats))
    farmer_tid = fields.Integer()
    logs = fields.List(fields.Object(ContainerLogs))
    capacity = fields.Object(ContainerCapacity)
    info = fields.Object(ReservationInfo)

    def resource_units(self):
        cap = self.capacity
        resource_units = ResourceUnitAmount()
        resource_units.cru = cap.cpu
        resource_units.mru = round(cap.memory / 1024 * 10000) / 10000
        storage_size = round(cap.disk_size / 1024 * 10000) / 10000
        storage_size = max(0, storage_size - 50)  # we offer the 50 first GB of storage for container root filesystem
        if cap.disk_type == DiskType.HDD:
            resource_units.hru += storage_size
        elif cap.disk_type == DiskType.SSD:
            resource_units.sru += storage_size
        return resource_units


class VirtualMachine(Base):
    id = fields.Integer()
    name = fields.String(default="")
    hub_url = fields.String(default="")
    network_connection = fields.List(fields.Object(ContainerNetworkConnection))
    network_id = fields.String()
    farmer_tid = fields.Integer()
    size = fields.Integer()
    info = fields.Object(ReservationInfo)
    ssh_keys = fields.List(fields.String())
    public_ip = fields.Integer()
    ipaddress = fields.IPAddress()

    SIZES = VMSIZES

    def resource_units(self):

        resource_units = ResourceUnitAmount()
        size = VMSIZES.get(self.size)
        if not size:
            raise j.exceptions.Input(f"VM size {self.size} not supported")

        resource_units.cru += size["cru"]
        resource_units.mru += size["mru"]
        resource_units.sru += size["sru"]
        return resource_units


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

    def resource_units(self):
        return ResourceUnitAmount()


class Network(Base):
    name = fields.String(default="")
    workload_id = fields.Integer()
    iprange = fields.IPRange(default="10.10.0.0/16")
    stats_aggregator = fields.List(fields.Object(Statsaggregator))
    network_resources = fields.List(fields.Object(NetworkResource))
    farmer_tid = fields.Integer()

    def resource_units(self):
        return ResourceUnitAmount()


class Volume(Base):
    id = fields.Integer()
    size = fields.Integer()
    type = fields.Enum(DiskType)
    stats_aggregator = fields.List(fields.Object(Statsaggregator))
    info = fields.Object(ReservationInfo)

    def resource_units(self):
        resource_units = ResourceUnitAmount()
        if self.type == DiskType.HDD:
            resource_units.hru += self.size
        elif self.type == DiskType.SSD:
            resource_units.sru += self.size
        return resource_units


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

    def resource_units(self):
        resource_units = ResourceUnitAmount()
        if self.disk_type == DiskType.HDD:
            resource_units.hru += self.size
        elif self.disk_type == DiskType.SSD:
            resource_units.sru += self.size
        return resource_units


class PublicIP(Base):
    id = fields.Integer()
    ipaddress = fields.IPRange()
    info = fields.Object(ReservationInfo)

    def resource_units(self):
        resource_units = ResourceUnitAmount()
        resource_units.ipv4u = 1
        return resource_units


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
    ipv4us = fields.Integer()
    node_ids = fields.List(fields.String())
    currencies = fields.List(fields.String())


class PoolCreate(Base):
    json = fields.String()
    data_reservation = fields.Object(PoolCreateData)
    customer_tid = fields.Integer()
    customer_signature = fields.String()
    sponsor_tid = fields.Integer()
    sponsor_signature = fields.String()


class Pool(Base):
    pool_id = fields.Integer()
    cus = fields.Float()
    sus = fields.Float()
    ipv4us = fields.Float()
    node_ids = fields.List(fields.String())
    last_updated = fields.DateTime()
    active_cu = fields.Float()
    active_su = fields.Float()
    active_ipv4 = fields.Float()
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


class PoolPayment(Base):
    id = fields.Integer()
    farmer_id = fields.Integer()
    address = fields.String()
    expiration = fields.DateTime()
    asset = fields.String()
    amount = fields.Integer()
    paid = fields.Boolean()
    released = fields.Boolean()
    canceled = fields.Boolean()
    cause = fields.String()
