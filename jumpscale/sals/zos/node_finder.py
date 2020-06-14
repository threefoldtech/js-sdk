import netaddr
import requests
from jumpscale.data.time import now
from jumpscale.core.exceptions import Input, NotFound
from .network import is_private


class NodeFinder:
    def __init__(self, explorer):
        self._nodes = explorer.nodes
        self._farms = explorer.farms

    def filter_is_up(self, node):
        """
        filter out nodes that have not received update for more then 10 minutes
        """
        ago = now().timestamp - (60 * 10)
        return node.updated.timestamp() > ago

    def filter_is_free_to_use(self, node):
        return node.free_to_use

    def filter_is_not_free_to_use(self, node):
        return not node.free_to_use

    def filter_public_ip4(self, node):
        return filter_public_ip(node, 4)

    def filter_public_ip6(self, node):
        return filter_public_ip(node, 6)

    def filter_farm_currency(self, farm, currency):
        if currency and currency != "FreeTFT":
            # check if farm support this currency
            for wallet in farm.wallet_addresses:
                if wallet.asset == currency:
                    return True
            return False
        return True

    def nodes_by_capacity(
        self,
        farm_id=None,
        farm_name=None,
        country=None,
        city=None,
        cru=None,
        sru=None,
        mru=None,
        hru=None,
        currency=None,
    ):

        not_supported_farms = []
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

            if currency:
                if currency == "FreeTFT":
                    if node.free_to_use:
                        yield node
                    continue
                elif currency != "FreeTFT" and node.free_to_use:
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
        if farm_name:
            farms = self._farms.list(name=farm_name)
            if len(farms) != 1:
                raise NotFound(f"Could not find farm with name {farm_name}")
            farm_id = farms[0].id

        return self._nodes.list(farm_id=farm_id, country=country, city=city, cru=cru, sru=sru, mru=mru, hru=hru)


def is_public_ip(ip, version):
    try:
        network = netaddr.IPNetwork(ip)
    except netaddr.AddrFormatError:
        return False
    if network.version != version:
        return False
    return not is_private(ip)


def filter_public_ip(node, version):
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
