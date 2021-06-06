import random

from jumpscale.loader import j
from jumpscale.sals.reservation_chatflow import deployer
from jumpscale.sals.zos import get as get_zos


class Scheduler:
    def __init__(self, farm_name=None, pool_id=None):
        self.zos = get_zos()
        self._pool_node_ids = None
        if not farm_name and not pool_id:
            raise j.exceptions.Validation("must pass farm_name or pool_id")
        if not farm_name and pool_id:
            pool = self.zos.pools.get(pool_id)
            self._pool_node_ids = pool.node_ids
            farm_id = deployer.get_pool_farm_id(pool_id, pool)
            farm_name = self.zos._explorer.farms.get(farm_id).name
        self.farm_name = farm_name
        self._nodes = []
        self._excluded_node_ids = set()

    def exclude_nodes(self, *node_ids):
        for node_id in node_ids:
            self._excluded_node_ids.add(node_id)

    @property
    def nodes(self):
        if not self._nodes:
            filters = [self.zos.nodes_finder.filter_is_up]
            if self._pool_node_ids:
                filters.append(lambda node: node.node_id in self._pool_node_ids)
            self._nodes = [
                node
                for node in self.zos.nodes_finder.nodes_search(farm_name=self.farm_name)
                if all([f(node) for f in filters])
            ]
        self._order_nodes()
        return self._nodes

    @staticmethod
    def _weight_sorter(node, cru_weight, mru_weight, sru_weight, hru_weight):
        cru = max(0, node.total_resources.cru - max(0, node.reserved_resources.cru))
        mru = max(0, node.total_resources.mru - max(0, node.reserved_resources.mru))
        sru = max(0, node.total_resources.sru - max(0, node.reserved_resources.sru))
        hru = max(0, node.total_resources.hru - max(0, node.reserved_resources.hru))
        return cru * cru_weight + mru * mru_weight + (sru / 1024) * sru_weight + (hru / 1024) * hru_weight

    def _order_nodes(self, randomize=False):
        if randomize:
            random.shuffle(self._nodes)
        else:
            cru_weight = j.core.config.get("SCHEDULER_CRU_WEIGHT", 0)
            mru_weight = j.core.config.get("SCHEDULER_MRU_WEIGHT", 0)
            sru_weight = j.core.config.get("SCHEDULER_SRU_WEIGHT", 5)
            hru_weight = j.core.config.get("SCHEDULER_HRU_WEIGHT", 0.75)
            self._nodes = sorted(
                self._nodes, key=lambda node: self._weight_sorter(node, cru_weight, mru_weight, sru_weight, hru_weight)
            )

    def _update_node(self, selected_node, cru=None, mru=None, sru=None, hru=None):
        for node in self._nodes:
            if node.node_id != selected_node.node_id:
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
        self, cru=None, sru=None, mru=None, hru=None, ip_version=None, public_ip=None, accessnodes=False
    ):
        """search node with the ability to filter on different criteria

        Args:
          cru: int:  (Default value = None)
          sru: int:  (Default value = None)
          mru: int:  (Default value = None)
          hru: int:  (Default value = None)
          ip_version: str:  (Default value = None)
          accessnodes: bool: (Default value = False)

        yields:
            node
        """
        filters = []
        if ip_version == "IPv4":
            filters.append(self.zos.nodes_finder.filter_public_ip4)
        elif ip_version == "IPv6":
            filters.append(self.zos.nodes_finder.filter_public_ip6)

        for node in self.nodes:
            if node.node_id in self._excluded_node_ids:
                continue

            if not self.check_node_capacity(node.node_id, node, cru, mru, hru, sru):
                continue

            if filters and not all([f(node) for f in filters]):
                continue

            if public_ip and not self.check_node_public_ip_bridge(node):
                continue

            # Exclude accessnodes
            # if accessnodes=True,the node needs to be an access node. If accessnode=False, the access nodes need to be excluded
            if accessnodes:
                if not self.check_accessnode(node):
                    continue
            else:
                if self.check_accessnode(node):
                    continue

            self._update_node(node, cru, mru, sru, hru)
            yield node

    def check_node_public_ip_bridge(self, node):
        if not any([self.zos.nodes_finder.filter_public_ip4(node), self.zos.nodes_finder.filter_public_ip6(node)]):
            return False

        for iface in node.ifaces:
            if iface.name == "br-pub":
                return True

        return False

    def check_accessnode(self, node):
        if any([self.zos.nodes_finder.filter_accessnode_ip4(node), self.zos.nodes_finder.filter_accessnode_ip6(node)]):
            return True

        return False

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
        if not j.core.config.get("OVER_PROVISIONING"):
            if cru and total.cru - max(0, reserved.cru) < 0:
                return False

            if cru and total.cru - max(0, reserved.cru) < cru:
                return False

        if mru and total.mru - max(0, reserved.mru) < 0:
            return False

        if mru and total.mru - max(0, reserved.mru) < mru:
            return False

        if sru and total.sru - max(0, reserved.sru) < 0:
            return False

        if sru and total.sru - max(0, reserved.sru) < sru:
            return False

        if hru and total.hru - max(0, reserved.hru) < 0:
            return False

        if hru and total.hru - max(0, reserved.hru) < hru:
            return False
        return True

    def refresh_nodes(self, clean_excluded=False):
        self._nodes = []
        if clean_excluded:
            self._excluded_node_ids = set()


class GlobalScheduler:
    def __init__(self) -> None:
        self.farm_schedulers = {}

    def get_scheduler(self, farm_name=None, pool_id=None):
        if not farm_name:
            scheduler = Scheduler(farm_name, pool_id)
            farm_name = scheduler.farm_name
            if farm_name not in self.farm_schedulers:
                self.farm_schedulers[farm_name] = scheduler
                return scheduler
        if farm_name in self.farm_schedulers:
            return self.farm_schedulers[farm_name]
        self.farm_schedulers[farm_name] = Scheduler(farm_name, pool_id)
        return self.farm_schedulers[farm_name]

    def add_all_farms(self):
        zos = get_zos()
        for farm in zos._explorer.farms.list():
            self.get_scheduler(farm.name)

    def nodes_by_capacity(
        self,
        farm_name=None,
        pool_id=None,
        cru=None,
        sru=None,
        mru=None,
        hru=None,
        ip_version=None,
        public_ip=None,
        all_farms=False,
    ):
        my_schedulers = []
        if farm_name or pool_id:
            scheduler = self.get_scheduler(farm_name, pool_id)
            my_schedulers.append(scheduler)
        else:
            if all_farms:
                self.add_all_farms()

            my_schedulers = list(self.farm_schedulers.values())
            random.shuffle(my_schedulers)

        for scheduler in my_schedulers:
            node_generator = scheduler.nodes_by_capacity(cru, sru, mru, hru, ip_version, public_ip)
            try:
                while True:
                    yield next(node_generator)
            except StopIteration:
                continue


class CapacityChecker:
    def __init__(self, farm_name):
        self.farm_name = farm_name
        self.scheduler = Scheduler(farm_name)
        self.result = True

    def exclude_nodes(self, *node_ids):
        self.scheduler.exclude_nodes(*node_ids)

    def add_query(
        self,
        cru=None,
        mru=None,
        hru=None,
        sru=None,
        ip_version=None,
        public_ip=None,
        no_nodes=1,
        backup_no=0,
        accessnodes=False,
    ):
        nodes = []
        for node in self.scheduler.nodes_by_capacity(cru, sru, mru, hru, ip_version, public_ip, accessnodes):
            nodes.append(node)
            if len(nodes) == no_nodes + backup_no:
                return self.result
        self.result = False
        return self.result

    def refresh(self, clear_excluded=False):
        self.result = True
        self.scheduler.refresh_nodes(clear_excluded)


class GlobalCapacityChecker:
    def __init__(self):
        self._checkers = {}
        self._result = True
        self._excluded_node_ids = []

    @property
    def result(self):
        for cc in self._checkers.values():
            self._result = self._result and cc.result
        return self._result

    def get_checker(self, farm_name):
        if farm_name not in self._checkers:
            cc = CapacityChecker(farm_name)
            cc.exclude_nodes(*self._excluded_node_ids)
            self._checkers[farm_name] = cc
        return self._checkers[farm_name]

    def exclude_nodes(self, *node_ids):
        self._excluded_node_ids += node_ids
        for cc in self._checkers.values():
            cc.exclude_nodes(*node_ids)

    def add_query(
        self,
        farm_name,
        cru=None,
        mru=None,
        hru=None,
        sru=None,
        ip_version=None,
        public_ip=None,
        no_nodes=1,
        backup_no=0,
        accessnodes=False,
    ):
        cc = self.get_checker(farm_name)
        result = cc.add_query(cru, mru, hru, sru, ip_version, public_ip, no_nodes, backup_no, accessnodes)
        self._result = self._result and result
        return self._result

    def refresh(self, clear_excluded=False):
        self._result = True
        for cc in self._checkers.values():
            cc.refresh(clear_excluded)

    def get_available_farms(
        self,
        cru=None,
        mru=None,
        hru=None,
        sru=None,
        ip_version=None,
        public_ip=None,
        no_nodes=1,
        backup_no=0,
        accessnodes=False,
    ):
        explorer = j.core.identity.me.explorer
        all_farms = explorer.farms.list()
        for farm in all_farms:
            cc = self.get_checker(farm.name)
            result = cc.add_query(cru, mru, hru, sru, ip_version, public_ip, no_nodes, backup_no, accessnodes)
            if result:
                yield farm.name
