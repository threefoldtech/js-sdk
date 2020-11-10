from jumpscale.sals.zos import get as get_zos


class Scheduler:
    def __init__(self, farm_name):
        self.zos = get_zos()
        self.farm_name = farm_name
        self._nodes = []

    @property
    def nodes(self):
        if not self._nodes:
            self._nodes = self.zos.nodes_finder.nodes_search(farm_name=self.farm_name)
        return self._nodes

    def _update_node(self, selected_node, cru=None, mru=None, sru=None, hru=None):
        for node in self.nodes:
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

            if not all([f(node) for f in filters]):
                continue

            self._update_node(node, cru, mru, hru, sru)
            yield node
