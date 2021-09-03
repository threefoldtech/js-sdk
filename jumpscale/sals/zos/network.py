import random

import netaddr
from nacl import public
from nacl.encoding import Base64Encoder

from jumpscale.clients.explorer.models import NetworkResource, NextAction, WireguardPeer, WorkloadType
from jumpscale.core.exceptions import Input
from jumpscale.loader import j
from jumpscale.tools.wireguard import generate_zos_keys
import netaddr


class Network:
    class Info:
        def __init__(self):
            self.workload_type = WorkloadType.Network_resource

    def __init__(self, name, iprange):
        self.info = self.Info()
        self.name = name
        self.iprange = iprange
        self.network_resources = []
        self.used_ips = []

    def get_free_range(self, *excluded_ranges):
        used_ip_ranges = set(excluded_ranges)
        for workload in self.network_resources:
            used_ip_ranges.add(workload.iprange)
            for peer in workload.peers:
                used_ip_ranges.add(peer.iprange)
        else:
            network_range = netaddr.IPNetwork(self.iprange)
            for _, subnet in enumerate(network_range.subnet(24)):
                if str(subnet) not in used_ip_ranges:
                    break
            else:
                return None
        return str(subnet)

    def get_node_range(self, node_id):
        for workload in self.network_resources:
            if workload.info.node_id == node_id:
                return workload.iprange
        return None

    def get_free_ip(self, node_id):
        free_ips = []
        ip_range = self.get_node_range(node_id)
        if not ip_range:
            raise j.exceptions.Input(f"node: {node_id} is not part of network: {self.name}")
        hosts = netaddr.IPNetwork(ip_range).iter_hosts()
        next(hosts)  # skip ip used by node
        for host in hosts:
            ip = str(host)
            if ip not in self.used_ips:
                free_ips.append(ip)
        if not free_ips:
            return None
        ip = random.choice(free_ips)
        self.used_ips.append(ip)
        return ip


class NetworkGenerator:
    def __init__(self, identity):
        explorer = identity.explorer
        self._identity = identity
        self._nodes = explorer.nodes
        self._farms = explorer.farms
        self._workloads = explorer.workloads

    def _load_network(self, network):
        for nr in network.network_resources:
            nr.public_endpoints = get_endpoints(self._nodes.get(nr.info.node_id))

        network.access_points = extract_access_points(network)

    def _cleanup_network(self, network):
        for nr in network.network_resources:
            if hasattr(nr, "public_endpoints"):
                delattr(nr, "public_endpoints")

        if hasattr(network, "access_points"):
            delattr(network, "access_points")

    def create(self, ip_range: str, network_name: str = None) -> Network:
        """create a new network

        Args:
          ip_range(str): IP range (cidr) of the full network. The network mask must be /16
          network_name(str, optional): name of the network. If None, a random name will be generated, defaults to None

        Returns:
          Network: Network

        Raises:
          Input: if ip_range not a private range (RFC 1918)
          Input: if network mask of ip_range is not /16

        """
        network = netaddr.IPNetwork(ip_range)
        if not is_private(network):
            raise Input("ip_range must be a private network range (RFC 1918)")
        if network.prefixlen != 16:
            raise Input("network mask of ip range must be a /16")
        network = Network(network_name, ip_range)
        return network

    def add_node(self, network: Network, node_id: str, ip_range: str, pool_id: int, wg_port: int = None):
        """add a node into the network

        Args:
          network(Network): network object
          node_id(str): ID of the node to add to the network
          ip_range(str): IP range (cidr) to assign to the node inside the network. The network mask must be a /24
          pool_id(int): the capacity pool ID
          wg_port(int, optional

        Raises:
          Input: if mask of ip_range is not /24
          Input: If specified access node not part of the network
          Input: If access node point doesn't have a public endpoint
          Input: If access node point doesn't have pubic endpoint of requested type): wireguar port of the wireguard endpoint. If None it will be picked automatically, defaults to None

        Returns:

        """
        node = self._nodes.get(node_id)

        if netaddr.IPNetwork(ip_range).prefixlen != 24:
            raise Input("ip_range should have a netmask of /24, not /%d", ip_range.prefixlen)

        if wg_port is None:
            wg_port = _find_free_wg_port(node)

        _, wg_private_encrypted, wg_public = generate_zos_keys(node.public_key_hex)

        nr = NetworkResource()
        nr.info.pool_id = pool_id
        nr.info.workload_type = WorkloadType.Network_resource
        nr.network_iprange = network.iprange
        nr.iprange = ip_range
        nr.info.node_id = node_id
        nr.wireguard_listen_port = wg_port
        nr.wireguard_public_key = wg_public
        nr.wireguard_private_key_encrypted = wg_private_encrypted
        nr.name = network.name
        network.network_resources.append(nr)
        try:
            self._load_network(network)
            generate_peers(network)
        finally:
            self._cleanup_network(network)

    def delete_node(self, network: Network, node_id: str):
        """deletes a node from the network

        Args:
          network(Network): network object
          node_id(str): ID of the node to add to the network

        Returns:
            wids: list to decomission
        """
        wids = []
        owner_tid = None
        node_range = network.get_node_range(node_id)
        if not node_range:
            return wids
        filtered_workloads = []
        for resource in network.network_resources:
            owner_tid = resource.info.customer_tid
            if resource.info.node_id != node_id:
                new_peers = []
                for peer in resource.peers:
                    if peer.iprange != node_range:
                        new_peers.append(peer)
                resource.peers = new_peers
                filtered_workloads.append(resource)
        network.network_resources = filtered_workloads
        for w in self._workloads.iter(customer_tid=owner_tid, next_action=NextAction.DEPLOY.name):
            if (
                w.info.workload_type == WorkloadType.Network_resource
                and w.name == network.name
                and w.info.node_id == node_id
            ):
                wids.append(w.id)
        return wids

    def add_access(
        self, network: Network, node_id: str, ip_range: str, wg_public_key: str = None, ipv4: bool = False
    ) -> str:
        """add an external access to the network. use this function if you want to allow
        a peer to your network that is not a 0-OS node like User laptop, external server,...

        Args:
          network(Network): network object
          node_id(str): ID of the node to use as entrypoint to the network
          ip_range(str): IP range to allocate for this peer
          wg_public_key(str, optional): wireguard public key of the peer. If not specify a new key will be generated, defaults to None
          ipv4(bool, optional): If True, use an IPv4 address as endpoint to connect to the network otherwise use IPv6, defaults to False

        Returns:
          str: the wireguard configuration to be used by the peer to connect to the network

        """
        if netaddr.IPNetwork(ip_range).prefixlen != 24:
            raise Input("ip_range should have a netmask of /24, not /%d", ip_range.prefixlen)

        try:
            self._load_network(network)

            access_point_nr = None
            for nr in network.network_resources:
                if node_id == nr.info.node_id:
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
                    ip = str(ep.ip)
                    endpoint = f"[{ip}]:{wg_port}"
                    break

            if not endpoint:
                raise Input("access node has no public endpoint of the requested type")

            wg_private_key = ""
            if not wg_public_key:
                wg_private = public.PrivateKey.generate()
                wg_public = wg_private.public_key
                wg_private_key = wg_private.encode(Base64Encoder).decode()
                wg_public_key = wg_public.encode(Base64Encoder).decode()

            network.access_points.append(
                AccessPoint(node_id=node_id, subnet=ip_range, wg_public_key=wg_public_key, ip4=ipv4)
            )

            generate_peers(network)

        finally:
            self._cleanup_network(network)

        return generate_wg_quick(
            wg_private_key, ip_range, access_point_nr.wireguard_public_key, network.iprange, endpoint
        )

    def delete_access(self, network: Network, node_id: str, iprange: str) -> Network:
        """remove a peer that was added using add_access method
        use this is you want to revoke the access to the network from someone

        Args:
          network(Network): network object
          node_id(str): ID of the node to use as entrypoint to the network
          ip_range(str): IP range to allocate for this peer

        Returns:
          Network: Network

        """
        node_workloads = {}
        node_ranges = set()
        for net_workload in network.network_resources:
            node_workloads[net_workload.info.node_id] = net_workload
            node_ranges.add(net_workload.iprange)
        if iprange in node_ranges:
            raise Input("Can't delete zos node peer")

        access_workload = node_workloads.get(node_id)
        if not access_workload:
            raise Input(f"Node {node_id} is not part of network")
        # remove peer from access node
        new_peers = []
        for peer in access_workload.peers:
            if peer.iprange != iprange:
                new_peers.append(peer)
        access_workload.peers = new_peers
        # remove peer from allowed ips on all nodes
        access_node_range = node_workloads[node_id]
        routing_range = wg_routing_ip(iprange)
        for network_resource in node_workloads.values():
            for peer in network_resource.peers:
                if peer.iprange != access_node_range:
                    if iprange in peer.allowed_iprange:
                        peer.allowed_iprange.remove(iprange)
                    if routing_range in peer.allowed_iprange:
                        peer.allowed_iprange.remove(routing_range)
        return network

    def load_network(self, network_name: str, customer_tid=None) -> Network:
        """load network fetch all network resource belonging to the same network
        and re-create the full network object

        if make sure to only take the latest version of each network resource

        use this function if you need to modify and existing network

        Args:
          network_name(str): the name of the network to load
          network_name: str:

        Returns:
          Network: Network object

        """
        if customer_tid is None:
            customer_tid = self._identity.tid
        nrs = {}
        used_ips = []
        # first gather all the latest version of each network resource for this network
        for w in self._workloads.iter(customer_tid=customer_tid, next_action=NextAction.DEPLOY.name):
            if w.info.workload_type == WorkloadType.Network_resource and w.name == network_name:
                nrs[w.info.node_id] = w
            elif w.info.workload_type == WorkloadType.Kubernetes:
                if w.network_id == network_name:
                    used_ips.append(w.ipaddress)
            elif w.info.workload_type == WorkloadType.Container:
                for conn in w.network_connection:
                    if conn.network_id == network_name:
                        used_ips.append(conn.ipaddress)

        network = None
        for nr in nrs.values():
            # ensure all network resource have the same network iprange
            # if this is not the case, then we have an issue
            if network is None:
                network = Network(network_name, nr.network_iprange)
            else:
                if nr.network_iprange != network.iprange:
                    raise j.exceptions.Value(
                        f"found a network resource with IP range ({nr.network_iprange}) different from the network IP range ({network.iprange})"
                    )

            nr.info.reference = ""  # just to handle possible migrated network
            network.network_resources.append(nr)

        if network:
            network.used_ips = used_ips

        return network


def generate_peers(network):
    """Generate  peers in the network
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
        internal_subnets[nr.info.node_id] = nr.iprange

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
            hidden_subnets[nr.info.node_id] = nr.iprange
            continue

        if not has_ipv4(nr):
            ipv6_only_subnets[nr.info.node_id] = nr.iprange

    for nr in network.network_resources:
        nr.peers = []
        for onr in network.network_resources:
            # skip ourself
            if nr.info.node_id == onr.info.node_id:
                continue

            endpoint = ""
            allowed_ips = set()
            allowed_ips.add(onr.iprange)
            allowed_ips.add(wg_routing_ip(onr.iprange))

            if len(nr.public_endpoints) == 0:
                # If node is hidden, set only public peers (with IPv4), and set first public peer to
                # contain all hidden subnets, except for the one owned by the node
                if not has_ipv4(onr):
                    continue

                # Also add all other subnets if this is the pub node
                if public_nr and onr.info.node_id == public_nr.info.node_id:
                    for owner, subnet in hidden_subnets.items():
                        # Do not add our own subnet
                        if owner == nr.info.node_id:
                            continue

                        allowed_ips.add(subnet)
                        allowed_ips.add(wg_routing_ip(subnet))

                    for subnet in ipv6_only_subnets.values():
                        allowed_ips.add(subnet)
                        allowed_ips.add(wg_routing_ip(subnet))

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
                if public_nr and onr.info.node_id == public_nr.info.node_id:
                    for subnet in hidden_subnets.values():
                        allowed_ips.add(subnet)
                        allowed_ips.add(wg_routing_ip(subnet))

                # Since the node is not hidden, we know that it MUST have at least 1 IPv6 address
                for pep in onr.public_endpoints:
                    if pep.version == 6:
                        endpoint = f"[{str(pep.ip)}]:{onr.wireguard_listen_port}"
                        break

                # as a fallback assign IPv4
                if endpoint == "":
                    for pep in onr.public_endpoints:
                        if pep.version == 4:
                            endpoint = f"{pep.ip}:{onr.wireguard_listen_port}"
                            break

            # Add subnets for external access
            new_allowed_ips = set()
            for aip in allowed_ips:
                new_allowed_ips.add(aip)
                for subnet in external_subnet.get(aip, []):
                    new_allowed_ips.add(subnet)
                    new_allowed_ips.add(wg_routing_ip(subnet))
            allowed_ips = new_allowed_ips

            peer = WireguardPeer()
            peer.iprange = str(onr.iprange)
            peer.endpoint = endpoint
            peer.allowed_iprange = [str(x) for x in allowed_ips]
            peer.public_key = onr.wireguard_public_key
            nr.peers.append(peer)
        #  Add configured external access peers
        for ea in access_points.get(nr.info.node_id, []):
            allowed_ips = [str(ea.subnet), wg_routing_ip(ea.subnet)]

            peer = WireguardPeer()
            peer.iprange = ea.subnet
            peer.endpoint = ""
            peer.allowed_iprange = [str(x) for x in allowed_ips]
            peer.public_key = ea.wg_public_key if isinstance(ea.wg_public_key, str) else ea.wg_public_key.decode()
            nr.peers.append(peer)


def has_hidden_nodes(network):
    """

    Args:
      network:

    Returns:

    """
    for nr in network.network_resources:
        if len(nr.public_endpoints) <= 0:
            return True
    return False


def find_public_node(network_resources):
    """

    Args:
      network_resources:

    Returns:

    """
    for nr in network_resources:
        if has_ipv4(nr):
            return nr
    return None


def has_ipv4(network_resource):
    """

    Args:
      network_resource:

    Returns:

    """
    for pep in network_resource.public_endpoints:
        if pep.version == 4:
            return True
    return False


def wg_routing_ip(ip_range):
    """

    Args:
      ip_range:

    Returns:

    """
    if not isinstance(ip_range, netaddr.IPNetwork):
        ip_range = netaddr.IPNetwork(ip_range)
    words = ip_range.ip.words
    return f"100.64.{words[1]}.{words[2]}/32"


def _find_free_wg_port(node):
    """

    Args:
      node:

    Returns:

    """
    ports = set(list(range(1000, 9000)))
    used = set(node.wg_ports)
    free = ports - used
    return random.choice(tuple(free))


# a node has either a public namespace with []ipv4 or/and []ipv6 -or-
# some interface has received a SLAAC addr
# which has been registered in BCDB
def get_endpoints(node):
    """

    Args:
      node:

    Returns:

    """
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
    netaddr.IPNetwork("200::/7"),  # IPv6 yggdrasil range
]


def is_private(ip):
    """

    Args:
      ip:

    Returns:

    """
    if not isinstance(ip, netaddr.IPNetwork):
        ip = netaddr.IPNetwork(ip)
    for network in _private_networks:
        if ip in network:
            return True
    return False


def extract_access_points(network):
    """

    Args:
      network:

    Returns:

    """
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
                    node_id=nr.info.node_id,
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
    """

    Args:
      wg_private_key:
      subnet:
      peer_wg_pub_key:
      allowed_ip:
      endpoint:

    Returns:

    """
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
