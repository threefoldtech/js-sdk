import random
import netaddr
from nacl import public
from nacl.encoding import Base64Encoder
from jumpscale.data.idgenerator import chars
from jumpscale.core.exceptions import Input
from jumpscale.tools.wireguard import generate_zos_keys
from .id import _next_workload_id
from jumpscale.clients.explorer.models import (
    TfgridWorkloadsReservationNetwork1,
    TfgridWorkloadsNetworkNet_resource1,
    TfgridWorkloadsWireguardPeer1,
)


class Network:
    def __init__(self, explorer):
        self._nodes = explorer.nodes
        self._farms = explorer.farms

    def _load_network(self, network):
        for nr in network.network_resources:
            nr.public_endpoints = get_endpoints(self._nodes.get(nr.node_id))

        network.access_points = extract_access_points(network)

    def _cleanup_network(self, network):
        for nr in network.network_resources:
            if hasattr(nr, "public_endpoints"):
                delattr(nr, "public_endpoints")

        if hasattr(network, "access_points"):
            delattr(network, "access_points")

    def create(self, reservation, ip_range, network_name=None):
        """add a network into the reservation

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1]): root reservation object, the network will be added to it
            ip_range (str): subnet of the network, it must have a network mask of /16
            network_name (str, optional): identifier of the network, if not specified a randon name will be generated. Defaults to None.

        Raises:
            jumpscale.core.exceptions.Input: If iprange not a private range (RFC 1918)
            jumpscale.core.exceptions.Input: if mask of ip_range is not /16

        Returns:
            [type]: new network object
        """
        network = netaddr.IPNetwork(ip_range)
        if not is_private(network):
            raise Input("ip_range must be a private network range (RFC 1918)")
        if network.prefixlen != 16:
            raise Input("network mask of ip range must be a /16")

        network = TfgridWorkloadsReservationNetwork1()
        network.workload_id = _next_workload_id(reservation)
        network.name = network_name if network_name else chars(16)
        network.iprange = ip_range
        reservation.data_reservation.networks.append(network)
        return network

    def add_node(self, network, node_id, ip_range, wg_port=None):
        """add a 0-OS node into the network

        Args:
            network ([type]): network object where to add the network resource
            node_id (str): node_id of the node we want to add to the network
            ip_range (str): subnet to attach to the network resource. network mask should be a /24 and be part of the network subnet
            wg_port (int, optional): listening port of the wireguard interface, if None port will be selected automatically. Defaults to None.

        Raises:
            jumpscale.core.exceptions.Input: if mask of ip_range is not /24
        """
        node = self._nodes.get(node_id)

        if netaddr.IPNetwork(ip_range).prefixlen != 24:
            raise Input("ip_range should have a netmask of /24, not /%d", ip_range.prefixlen)

        if wg_port is None:
            wg_port = _find_free_wg_port(node)

        _, wg_private_encrypted, wg_public = generate_zos_keys(node.public_key_hex)

        nr = TfgridWorkloadsNetworkNet_resource1()

        nr.iprange = ip_range
        nr.node_id = node_id
        nr.wireguard_listen_port = wg_port
        nr.wireguard_public_key = wg_public
        nr.wireguard_private_key_encrypted = wg_private_encrypted
        network.network_resources.append(nr)
        try:
            self._load_network(network)
            generate_peers(network)
        finally:
            self._cleanup_network(network)

    def add_access(self, network, node_id, ip_range, wg_public_key=None, ipv4=False):
        """add an external access to the network. use this function if you want to allow
           a member to your network that is not a 0-OS node like User laptop, external server,...

        Args:
            network ([type]): network object where to add the network resource
            node_id (str): node_id of the node to use a access point into the network
            ip_range (str): subnet to allocate to the member,  network mask should be a /24 and be part of the network subnet
            wg_public_key (str, optional): public key of the new member. If none a new key pair will be generated automatically. Defaults to None.
            ipv4 (bool, optional): if True, the endpoint of the access node will use IPv4. Use this if the member is not IPv6 enabled. Defaults to False.

        Raises:
            jumpscale.core.exceptions.Input: if mask of ip_range is not /24
            jumpscale.core.exceptions.Input: If specified access node not part of the network
            jumpscale.core.exceptions.Input: If access node point doesn't have a public endpoint
            jumpscale.core.exceptions.Input: If access node point doesn't have pubic endpoint of requested type

        Returns:
            [type]: [description]
        """
        if netaddr.IPNetwork(ip_range).prefixlen != 24:
            raise Input("ip_range should have a netmask of /24, not /%d", ip_range.prefixlen)

        try:
            self._load_network(network)

            access_point_nr = None
            for nr in network.network_resources:
                if node_id == nr.node_id:
                    access_point_nr = nr

            if access_point_nr is None:
                raise Input("can not add access through a node which is not in the network")

            if len(access_point_nr.public_endpoints) == 0:
                raise Input("access node must have at least 1 public endpoint")

            endpoint = ""
            wg_port = access_point_nr.wireguard_listen_port
            for ep in access_point_nr.public_endpoints:
                if ipv4 and ep.version == 4:
                    endpoint = f"{str(ep.ip)}:{wg_port}"
                    break
                if not ipv4 and ep.version == 6:
                    ip = str(access_point_nr.public_endpoints[0].ip)
                    endpoint = f"[{ip}]:{wg_port}"
                    break

            if not endpoint:
                raise Input("access node has no public endpoint of the requested type")

            wg_private_key = None
            if wg_public_key is None:
                wg_private = public.PrivateKey.generate()
                wg_public = wg_private.public_key
                wg_private_key = wg_private.encode(Base64Encoder)
                wg_public_key = wg_public.encode(Base64Encoder)

            network.access_points.append(
                AccessPoint(node_id=node_id, subnet=ip_range, wg_public_key=wg_public_key, ip4=ipv4)
            )

            generate_peers(network)

        finally:
            self._cleanup_network(network)

        return generate_wg_quick(
            wg_private_key.decode(), ip_range, access_point_nr.wireguard_public_key, network.iprange, endpoint
        )


def generate_peers(network):
    """Generate  peers in the network

    Args:
        network ([type]): network object
    """

    public_nr = None
    if has_hidden_nodes(network):
        public_nr = find_public_node(network.network_resources)

    # We also need to inform nodes how to route the external access subnets.
    # Working with the knowledge that these external subnets come in through
    # the network through a single access point, which is part of the network
    # and thus already routed, we can map the external subnets to the subnet
    # of the access point, and add these external subnets to all peers who also
    # have the associated internal subnet.

    # Map the network subnets to their respective node ids first for easy access later
    internal_subnets = {}
    for nr in network.network_resources:
        internal_subnets[nr.node_id] = nr.iprange

    external_subnet = {}
    for ap in network.access_points:
        internal_sub = internal_subnets[ap.node_id]
        if internal_sub not in external_subnet:
            external_subnet[internal_sub] = []
        external_subnet[internal_sub].append(ap.subnet)

    # Maintain a mapping of access point nodes to the subnet and wg key they give access
    # to, as these need to be added as peers as well for these nodes
    access_points = {}
    for ap in network.access_points:
        if ap.node_id not in access_points:
            access_points[ap.node_id] = []
        access_points[ap.node_id].append(ap)

    # Find all hidden nodes, and collect their subnets. Also collect the subnets
    # of public IPv6 only nodes, since hidden nodes need IPv4 to connect.
    hidden_subnets = {}
    # also maintain subnets from nodes who have only IPv6 since this will also
    # need to be routed for hidden nodes
    ipv6_only_subnets = {}
    for nr in network.network_resources:
        if len(nr.public_endpoints) == 0:
            hidden_subnets[nr.node_id] = nr.iprange
            continue

        if not has_ipv4(nr):
            ipv6_only_subnets[nr.node_id] = nr.iprange

    for nr in network.network_resources:

        nr.peers = []
        for onr in network.network_resources:
            # skip ourself
            if nr.node_id == onr.node_id:
                continue

            endpoint = ""

            allowed_ips = [onr.iprange, wg_routing_ip(onr.iprange)]

            if len(nr.public_endpoints) == 0:
                # If node is hidden, set only public peers (with IPv4), and set first public peer to
                # contain all hidden subnets, except for the one owned by the node
                if not has_ipv4(onr):
                    continue

                # Also add all other subnets if this is the pub node
                if public_nr and onr.node_id == public_nr.node_id:
                    for owner, subnet in hidden_subnets.items():
                        # Do not add our own subnet
                        if owner == nr.node_id:
                            continue

                        allowed_ips.append(subnet)
                        allowed_ips.append(wg_routing_ip(subnet))

                    for subnet in ipv6_only_subnets.values():
                        allowed_ips.append(subnet)
                        allowed_ips.append(wg_routing_ip(subnet))

                    for pep in onr.public_endpoints:
                        if pep.version == 4:
                            endpoint = f"{str(pep.ip)}.{onr.wireguard_listen_port}"
                            break

                # Endpoint must be IPv4
                for pep in onr.public_endpoints:
                    if pep.version == 4:
                        endpoint = f"{str(pep.ip)}:{onr.wireguard_listen_port}"
                        break

            elif len(onr.public_endpoints) == 0 and has_ipv4(nr):
                # if the peer is hidden but we have IPv4,  we can connect to it, but we don't know an endpoint.
                endpoint = ""
            else:
                # if we are not hidden, we add all other nodes, unless we don't
                # have IPv4, because then we also can't connect to hidden nodes.
                # Ignore hidden nodes if we don't have IPv4
                if not has_ipv4(nr) and len(onr.public_endpoints) == 0:
                    continue

                # both nodes are public therefore we can connect over IPv6

                # if this is the selected public_nr - also need to add allowedIPs for the hidden nodes
                if public_nr and onr.node_id == public_nr.node_id:
                    for subnet in hidden_subnets.values():
                        allowed_ips.append(subnet)
                        allowed_ips.append(wg_routing_ip(subnet))

                # Since the node is not hidden, we know that it MUST have at least 1 IPv6 address
                for pep in onr.public_endpoints:
                    if pep.version == 6:
                        endpoint = f"[{str(pep.ip)}]:{onr.wireguard_listen_port}"
                        break

                # as a fallback assign IPv4
                if endpoint == "":
                    for pep in onr.public_endpoint:
                        if pep.version == 4:
                            endpoint = f"{pep.ip}:{onr.wireguard_listen_port}"
                            break

            # Add subnets for external access
            for aip in allowed_ips:
                for subnet in external_subnet.get(aip, []):
                    allowed_ips.append(subnet)
                    allowed_ips.append(wg_routing_ip(subnet))

            peer = TfgridWorkloadsWireguardPeer1()
            peer.iprange = str(onr.iprange)
            peer.endpoint = endpoint
            peer.allowed_iprange = [str(x) for x in allowed_ips]
            peer.public_key = onr.wireguard_public_key
            nr.peers.append(peer)

        #  Add configured external access peers
        for ea in access_points.get(nr.node_id, []):
            allowed_ips = [str(ea.subnet), wg_routing_ip(ea.subnet)]

            peer = TfgridWorkloadsWireguardPeer1()
            peer.iprange = ea.subnet
            peer.endpoint = ""
            peer.allowed_iprange = [str(x) for x in allowed_ips]
            peer.public_key = ea.wg_public_key if isinstance(ea.wg_public_key, str) else ea.wg_public_key.decode()
            nr.peers.append(peer)


def has_hidden_nodes(network):
    for nr in network.network_resources:
        if len(nr.public_endpoints) <= 0:
            return True
    return False


def find_public_node(network_resources):
    for nr in network_resources:
        if has_ipv4(nr):
            return nr
    return None


def has_ipv4(network_resource):
    for pep in network_resource.public_endpoints:
        if pep.version == 4:
            return True
    return False


def wg_routing_ip(ip_range):
    if not isinstance(ip_range, netaddr.IPNetwork):
        ip_range = netaddr.IPNetwork(ip_range)
    words = ip_range.ip.words
    return f"100.64.{words[1]}.{words[2]}/32"


def _find_free_wg_port(node):
    ports = set(list(range(1000, 9000)))
    used = set(node.wg_ports)
    free = ports - used
    return random.choice(tuple(free))


# a node has either a public namespace with []ipv4 or/and []ipv6 -or-
# some interface has received a SLAAC addr
# which has been registered in BCDB
def get_endpoints(node):
    ips = []
    if node.public_config and node.public_config.master:
        ips.append(netaddr.IPNetwork(node.public_config.ipv4))
        ips.append(netaddr.IPNetwork(node.public_config.ipv6))
    else:
        for iface in node.ifaces:
            for ip in iface.addrs:
                ips.append(netaddr.IPNetwork(ip))

    endpoints = []
    for ip in ips:
        if ip.is_unicast() and not is_private(ip):
            endpoints.append(ip)
    return endpoints


_private_networks = [
    netaddr.IPNetwork("127.0.0.0/8"),  # IPv4 loopback
    netaddr.IPNetwork("10.0.0.0/8"),  # RFC1918
    netaddr.IPNetwork("172.16.0.0/12"),  # RFC1918
    netaddr.IPNetwork("192.168.0.0/16"),  # RFC1918
    netaddr.IPNetwork("169.254.0.0/16"),  # RFC3927 link-local
    netaddr.IPNetwork("::1/128"),  # IPv6 loopback
    netaddr.IPNetwork("fe80::/10"),  # IPv6 link-local
    netaddr.IPNetwork("fc00::/7"),  # IPv6 unique local addr
]


def is_private(ip):
    if not isinstance(ip, netaddr.IPNetwork):
        ip = netaddr.IPNetwork(ip)
    for network in _private_networks:
        if ip in network:
            return True
    return False


def extract_access_points(network):
    # gather all actual nodes, using their wg pubkey as key in the map (NodeID
    # can't be seen in the actual peer struct)
    actual_nodes = {}
    for nr in network.network_resources:
        actual_nodes[nr.wireguard_public_key] = None

    aps = []
    for nr in network.network_resources:
        for peer in nr.peers:
            if peer.public_key not in actual_nodes:
                # peer is not a node so it must be external
                ap = AccessPoint(
                    node_id=nr.node_id,
                    subnet=peer.iprange,
                    wg_public_key=peer.public_key,
                    # we can't infer if we use IPv6 or IPv4
                )
                aps.append(ap)
    return aps


class AccessPoint:
    def __init__(self, node_id, subnet, wg_public_key, ip4=None):
        self.node_id = node_id
        self.subnet = subnet
        self.wg_public_key = wg_public_key
        self.ip4 = ip4


def generate_wg_quick(wg_private_key, subnet, peer_wg_pub_key, allowed_ip, endpoint):
    address = wg_routing_ip(subnet)
    allowed_ips = [allowed_ip, wg_routing_ip(allowed_ip)]
    aip = ", ".join(allowed_ips)

    result = f"""
[Interface]
Address = {address}
PrivateKey = {wg_private_key}
[Peer]
PublicKey = {peer_wg_pub_key}
AllowedIPs = {aip}
PersistentKeepalive = 25
"""
    if endpoint:
        result += f"Endpoint = {endpoint}"

    return result
