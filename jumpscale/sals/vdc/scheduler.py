from jumpscale.sals.zos import get as get_zos
import random
from jumpscale.loader import j


class Scheduler:
    def __init__(self, farm_name):
        self.zos = get_zos()
        self.farm_name = farm_name
        self._nodes = []
        self._excluded_node_ids = set()

    def exclude_nodes(self, *node_ids):
        for node_id in node_ids:
            self._excluded_node_ids.add(node_id)

    @property
    def nodes(self):
        if not self._nodes:
            self._nodes = self.zos.nodes_finder.nodes_search(farm_name=self.farm_name)
        random.shuffle(self._nodes)
        return self._nodes

    def _update_node(self, selected_node, cru=None, mru=None, sru=None, hru=None):
        for node in self._nodes:
            if node.node_id not in selected_node.node_id:
                continue
            if cru:
                node.reserved_resources.cru += cru
            if mru:
                node.reserved_resources.mru += mru
            if sru:
                node.reserved_resources.sru += sru
            if hru:
                node.reserved_resources.hru += hru

    def nodes_by_capacity(
        self, cru=None, sru=None, mru=None, hru=None, ip_version=None,
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
        filters = [self.zos.nodes_finder.filter_is_up]
        if ip_version == "IPv4":
            filters.append(self.zos.nodes_finder.filter_public_ip4)
        elif ip_version == "IPv6":
            filters.append(self.zos.nodes_finder.filter_public_ip6)

        for node in self.nodes:
            if node.node_id in self._excluded_node_ids:
                continue
            if not self.check_node_capacity(node.node_id, node, cru, mru, hru, sru):
                continue

            if not all([f(node) for f in filters]):
                continue

            self._update_node(node, cru, mru, hru, sru)
            yield node

    def check_node_capacity(self, node_id, node=None, cru=None, mru=None, hru=None, sru=None):
        if not node:
            for t_node in self.nodes:
                if t_node.node_id == node_id:
                    node = t_node
                    break

        if not node:
            raise j.exceptions.Validation(f"node {node_id} is not part of farm {self.farm_name}")
        total = node.total_resources
        reserved = node.reserved_resources
        if cru and total.cru - max(0, reserved.cru) < cru:
            return False

        if mru and total.mru - max(0, reserved.mru) < mru:
            return False

        if sru and total.sru - max(0, reserved.sru) < sru:
            return False

        if hru and total.hru - max(0, reserved.hru) < hru:
            return False
        return True

    def refresh_nodes(self, clean_excluded=False):
        self._nodes = []
        if clean_excluded:
            self._excluded_node_ids = set()
