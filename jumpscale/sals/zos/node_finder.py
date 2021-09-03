import netaddr
import requests

from jumpscale.clients.explorer.models import Node, Farm
from jumpscale.core.exceptions import Input, NotFound
from jumpscale.data.time import now

from .network import is_private


class NodeFinder:
    """ """

    def __init__(self, identity=None, explorer=None):
        self._identity = identity
        explorer = explorer or identity.explorer  # to make the usage of node finder without identity
        self._nodes = explorer.nodes
        self._farms = explorer.farms
        self._pools = explorer.pools

    def filter_is_up(self, node: Node):
        """filter function that filters out nodes that have not received update for more then 10 minutes"""
        ago = now().timestamp - (60 * 10)
        return node.updated.timestamp() > ago

    def filter_is_free_to_use(self, node: Node):
        """filter function that filters out nodes that are marked as free to use"""
        return node.free_to_use

    def filter_is_not_free_to_use(self, node):
        """filter function that filters out nodes that are not marked as free to use"""
        return not node.free_to_use

    def filter_public_ip4(self, node):
        """filter function that filters out nodes that have a public IPv4 address"""
        return filter_public_ip(node, 4)

    def filter_public_ip6(self, node):
        """filter function that filters out nodes that have a public IPv6 address"""
        return filter_public_ip(node, 6)

    def filter_accessnode_ip4(self, node):
        """filter function that filters out nodes that have a public config with IPv4 address"""
        return is_access_node(node, 4)

    def filter_accessnode_ip6(self, node):
        """filter function that filters out nodes that have a public config with IPv6 address"""
        return is_access_node(node, 6)

    def filter_farm_currency(self, farm: Farm, currency: str):
        """filter function that filters farms by the type of currency supported for capacity reservation

        Args:
          farm: Farm:
          currency: str:

        Returns:

        """
        if currency and currency != "FreeTFT":
            # check if farm support this currency
            for wallet in farm.wallet_addresses:
                if wallet.asset == currency:
                    return True
            return False
        return True

    def nodes_by_capacity(
        self,
        farm_id: int = None,
        farm_name: str = None,
        country: str = None,
        city: str = None,
        cru: int = None,
        sru: int = None,
        mru: int = None,
        hru: int = None,
        currency: str = None,
        pool_id: int = None,
    ):
        """search node with the ability to filter on different criteria

        Args:
          farm_id: int:  (Default value = None)
          farm_name: str:  (Default value = None)
          country: str:  (Default value = None)
          city: str:  (Default value = None)
          cru: int:  (Default value = None)
          sru: int:  (Default value = None)
          mru: int:  (Default value = None)
          hru: int:  (Default value = None)
          currency: str:  (Default value = None)

        Returns:

        """
        not_supported_farms = []
        if pool_id:
            pool = self._pools.get(pool_id)
        else:
            pool = None
        nodes = self.nodes_search(farm_id=farm_id, farm_name=farm_name, country=country, city=city)
        for node in nodes:
            total = node.total_resources
            reserved = node.reserved_resources
            if cru and total.cru - max(0, reserved.cru) < cru:
                continue

            if mru and total.mru - max(0, reserved.mru) < mru:
                continue

            if sru and total.sru - max(0, reserved.sru) < sru:
                continue

            if hru and total.hru - max(0, reserved.hru) < hru:
                continue

            if pool and node.node_id not in pool.node_ids:
                continue

            if currency:
                if currency == "FreeTFT" and not node.free_to_use:
                    continue
                if node.farm_id in not_supported_farms:
                    continue
                try:
                    farm = self._farms.get(node.farm_id)
                except requests.exceptions.HTTPError:
                    not_supported_farms.append(node.farm_id)
                    continue

                if not self.filter_farm_currency(farm, currency):
                    not_supported_farms.append(node.farm_id)
                    continue

            yield node

    def nodes_search(
        self, farm_id=None, country=None, city=None, cru=None, sru=None, mru=None, hru=None, farm_name=None
    ):
        """

        Args:
          farm_id:  (Default value = None)
          country:  (Default value = None)
          city:  (Default value = None)
          cru:  (Default value = None)
          sru:  (Default value = None)
          mru:  (Default value = None)
          hru:  (Default value = None)
          farm_name:  (Default value = None)

        Returns:

        """
        if farm_name:
            farms = self._farms.list(name=farm_name)
            if len(farms) != 1:
                raise NotFound(f"Could not find farm with name {farm_name}")
            farm_id = farms[0].id

        return self._nodes.list(farm_id=farm_id, country=country, city=city, cru=cru, sru=sru, mru=mru, hru=hru)

    def filter_public_ip_bridge(self, node):
        if not any([self.filter_public_ip4(node), self.filter_public_ip6(node)]):
            return False

        for iface in node.ifaces:
            if iface.name == "br-pub":
                return True

        return False


def is_public_ip(ip, version):
    """

    Args:
      ip:
      version:

    Returns:

    """
    try:
        network = netaddr.IPNetwork(ip)
    except netaddr.AddrFormatError:
        return False
    if network.version != version:
        return False
    return not is_private(ip)


def filter_public_ip(node, version):
    """

    Args:
      node:
      version:

    Returns:

    """
    if version not in [4, 6]:
        raise Input("ip version can only be 4 or 6")

    if node.public_config and node.public_config.master:
        if version == 4:
            return is_public_ip(node.public_config.ipv4, 4)
        elif node.public_config.ipv6:
            return is_public_ip(node.public_config.ipv6, 6)
    else:
        for iface in node.ifaces:
            for addr in iface.addrs:
                if is_public_ip(addr, version):
                    return True
    return False


def is_access_node(node, version):
    """

    Args:
      node:
      version:

    Returns:

    """
    if version not in [4, 6]:
        raise Input("ip version can only be 4 or 6")

    if node.public_config and node.public_config.master:
        if version == 4:
            return is_public_ip(node.public_config.ipv4, 4)
        elif node.public_config.ipv6:
            return is_public_ip(node.public_config.ipv6, 6)
    return False
