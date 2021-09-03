from typing import Iterator, List

from jumpscale.core.exceptions import Input

from .base import BaseResource
from .models import Node, NodePublicIface
from .pagination import get_all, get_page


def _build_query(
    farm_id: int = None,
    city: str = None,
    cru: int = None,
    sru: int = None,
    mru: int = None,
    hru: int = None,
    proofs: bool = False,
) -> dict:
    query = {}
    if proofs:
        query["proofs"] = "true"
    args = {
        "farm": farm_id,
        "city": city,
        "cru": cru,
        "sru": sru,
        "mru": mru,
        "hru": hru,
    }
    for k, v in args.items():
        if v is not None:
            query[k] = v
    return query


class Nodes(BaseResource):
    _resource = "nodes"

    def list(
        self, farm_id=None, country=None, city=None, cru=None, sru=None, mru=None, hru=None, proofs=False, page=None,
    ) -> List[Node]:
        """
        List all the nodes in the grid

        :param farm_id: filter by farm ID
        :type farm_id: int, optional
        :param country: filter by country
        :type country: str, optional
        :param city: filter by city
        :type city: str, optional
        :param cru: filter by total amount of cru
        :type cru: int, optional
        :param sru: filter by total amount of sru
        :type sru: int, optional
        :param mru: filter by total amount of mru
        :type mru: int, optional
        :param hru: filter by total amount of hru
        :type hru: int, optional
        :param proofs: bool, if True, includes the hardware proof in the response. This greatly increase the size of the response.
        :type proofs: bool, optional
        :return: list of nodes
        :rtype: List[Node]
        """
        query = _build_query(farm_id, city, cru, sru, mru, hru, proofs)
        if page:
            nodes, _ = get_page(self._session, page, Node, self._url, query)
        else:
            nodes = list(self.iter(farm_id, country, city, cru, sru, mru, hru, proofs))
        return nodes

    def iter(
        self, farm_id=None, country=None, city=None, cru=None, sru=None, mru=None, hru=None, proofs=False,
    ) -> Iterator[Node]:
        """
        returns an iterator yielding nodes

        :param farm_id: filter by farm ID
        :type farm_id: int, optional
        :param country: filter by country
        :type country: str, optional
        :param city: filter by city
        :type city: str, optional
        :param cru: filter by total amount of cru
        :type cru: int, optional
        :param sru: filter by total amount of sru
        :type sru: int, optional
        :param mru: filter by total amount of mru
        :type mru: int, optional
        :param hru: filter by total amount of hru
        :type hru: int, optional
        :param proofs: bool, if True, includes the hardware proof in the response. This greatly increase the size of the response.
        :type proofs: bool, optional
        :yield: Farm
        :rtype: Iterator[Farm]
        """
        query = _build_query(farm_id, city, cru, sru, mru, hru, proofs)
        yield from get_all(self._session, Node, self._url, query)

    def get(self, node_id: str, proofs=False) -> Node:
        """
        get the detail of a specific node

        :param node_id: node ID of the node to retrieve
        :type node_id: str
        :param proofs: bool, if True, includes the hardware proof in the response. This greatly increase the size of the response.
        :type proofs: bool, optional
        :return: Node
        :rtype: Node
        """
        params = {}
        if proofs:
            params["proofs"] = "true"
        resp = self._session.get(f"{self._url}/{node_id}", params=params)
        return Node.from_dict(resp.json())

    def configure_free_to_use(self, node_id: str, free: bool) -> bool:
        """
        configure if the node capacity can be paid using FreeTFT

        :param node_id: the node ID of the node to configure
        :type node_id: str
        :param free: if True, enable FreeTFT, if false disable it
        :type free: bool
        :return: True when the configuration was done successfully
        :rtype: bool
        """
        if not isinstance(free, bool):
            raise Input("free must be a boolean")

        data = {"free_to_use": free}
        self._session.post(
            f"{self._url}/{node_id}/configure_free", json=data,
        )
        return True

    def configure_public_config(
        self, node_id: str, master_iface: str, ipv4: str, gw4: str, ipv6: str, gw6: str
    ) -> bool:
        """
        configure the public interface on a node

        A node can have a NIC that is dedicated for public traffic only. To enable this on the node,
        this function needs to be call with the proper IP and gateway configuration that match the farm network of the node.

        :param node_id: node ID
        :type node_id: str
        :param master_iface: name of the NIC to use for public traffic
        :type master_iface: str
        :param ipv4: IPv4 address to assign to the public NIC
        :type ipv4: str
        :param gw4: gateway for the IPv4 address
        :type gw4: str
        :param ipv6: IPv6 address to assign to the public NIC
        :type ipv6: str
        :param gw6: gatway for the IPv6 address
        :type gw6: str
        :return: true if the config was properly saved
        :rtype: bool
        """
        node = self.get(node_id)

        public_config = node.public_config or NodePublicIface()
        public_config.master = master_iface
        public_config.ipv4 = ipv4
        public_config.gw4 = gw4
        public_config.ipv6 = ipv6
        public_config.gw6 = gw6
        public_config.type = 0
        public_config.version += 1

        data = public_config.to_dict()
        self._session.post(
            f"{self._url}/{node_id}/configure_public", json=data,
        )
        return True
