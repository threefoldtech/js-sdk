from typing import Iterator, List

from jumpscale.clients.explorer.models import Pool, PoolCreated, PoolPayment
from jumpscale.loader import j


class Pools:
    """ """

    def __init__(self, identity):
        explorer = identity.explorer
        self._identity = identity
        self._model_create = PoolCreated
        self._pools = explorer.pools
        self._farms = explorer.farms
        self._nodes = explorer.nodes
        self._gateways = explorer.gateway

    def _reserve(self, pool, sponsor_identity=None):
        me = self._identity
        pool.customer_tid = me.tid
        pool.json = j.data.serializers.json.dumps(pool.data_reservation.to_dict())
        pool.customer_signature = me.nacl.sign_hex(pool.json.encode()).decode()
        if sponsor_identity:
            pool.sponsor_tid = sponsor_identity.tid
            pool.sponsor_signature = sponsor_identity.nacl.sign_hex(pool.json.encode()).decode()
        return self._pools.create(pool)

    def create(
        self, cu: int, su: int, ipv4us: int, farm: str, currencies: List[str] = None, sponsor_identity=None
    ) -> PoolCreated:
        """create a new capacity pool

        Args:
          cu(int): amount of compute unit to reserve
          su(int): amount of storage unit to reserve
          ipv4us(int): amount of ipv4 unit to reserve
          farm(str): name of the farm where to reserve capacity
          currencies(List[str], optional): list of currency you are willing to pay with, defaults to None

        Returns:
          PoolCreated: the payment detail required to pay fo the reserved capacity

        """
        cu = int(cu)
        su = int(su)
        ipv4us = int(ipv4us)
        if not currencies:
            currencies = ["TFT"]

        farm_id = farm
        if isinstance(farm, str):
            farm = self._farms.get(farm_name=farm)
            farm_id = farm.id

        node_ids = []
        for node in self._nodes.iter(farm_id=farm_id):
            if currencies == ["FreeTFT"] and not node.free_to_use:
                continue
            node_ids.append(node.node_id)
        for gw in self._gateways.iter(farm_id=farm_id):
            if currencies == ["FreeTFT"] and not gw.free_to_use:
                continue
            node_ids.append(gw.node_id)

        pool = self._pools.new()
        pool.data_reservation.pool_id = 0
        pool.data_reservation.cus = cu
        pool.data_reservation.sus = su
        pool.data_reservation.ipv4us = ipv4us
        pool.data_reservation.node_ids = node_ids
        pool.data_reservation.currencies = currencies
        return self._reserve(pool, sponsor_identity)

    def extend(
        self, pool_id: int, cu: int, su: int, ipv4us: int, currencies: List[str] = None, node_ids: List[str] = None
    ) -> PoolCreated:
        """extend an existing capacity pool

        Args:
          pool_id(int): the ID of the pool to extend
          cu(int): amount of compute units to reserve
          su(int): amount of storage units to reserve
          currencies(List[str], optional): list of currency you are willing to pay with, defaults to None

        Returns:
          PoolCreated: the payment detail required to pay fo the reserved capacity

        """
        cu = int(cu)
        su = int(su)
        ipv4us = int(ipv4us)
        p = self.get(pool_id)
        if not currencies:
            currencies = ["TFT"]

        pool = self._pools.new()
        pool.data_reservation.pool_id = p.pool_id
        pool.data_reservation.cus = cu
        pool.data_reservation.sus = su
        pool.data_reservation.ipv4us = ipv4us
        pool.data_reservation.node_ids = list(set(node_ids).union(set(p.node_ids))) if node_ids else p.node_ids
        pool.data_reservation.currencies = currencies
        return self._reserve(pool)

    def get(self, pool_id: int) -> Pool:
        """get the detail about an specific pool

        Args:
          pool_id(int): ID of the pool to retrieve
          pool_id: int:

        Returns:
          Pool: Pool

        """
        return self._pools.get(pool_id)

    def iter(self) -> Iterator[Pool]:
        """Iterate over all the pools

        :yield: Pool

        Args:

        Returns:

        """
        return self._pools.iter()

    def list(self, page=None) -> List[Pool]:
        """List all the pool

        Args:
          page:  (Default value = None)

        Returns:
          pool: list of pools

        """
        return self._pools.list(customer_tid=self._identity.tid)

    def get_payment_info(self, reservation_id) -> PoolPayment:
        """get pool payment info

        Args:
            reservation_id (int)

        Returns:
            PoolPayment: pool payment info
        """
        return self._pools.get_payment_info(reservation_id)
