from jumpscale.loader import j
from jumpscale.clients.explorer.models import PoolCreated, Pool

from typing import List, Iterator


class Pools:
    def __init__(self, explorer):
        self._model_create = PoolCreated
        self._pools = explorer.pools
        self._farms = explorer.farms
        self._nodes = explorer.nodes
        self._gateways = explorer.gateway

    def _reserve(self, pool):
        me = j.core.identity.me
        pool.customer_tid = me.tid
        pool.json = j.data.serializers.json.dumps(pool.data_reservation.to_dict())
        pool.customer_signature = me.nacl.sign_hex(pool.json.encode()).decode()
        return self._pools.create(pool)

    def create(self, cu: int, su: int, farm: str, currencies: List[str] = None) -> PoolCreated:
        """
        create a new capacity pool

        :param cu: amount of compute unit to reserve
        :type cu: int
        :param su: amount of storage unit to reserve
        :type su: int
        :param farm: name of the farm where to reserve capacity
        :type farm: str
        :param currencies: list of currency you are willing to pay with, defaults to None
        :type currencies: List[str], optional
        :return: the payment detail required to pay fo the reserved capacity
        :rtype: PoolCreated
        """
        if not currencies:
            currencies = ["TFT"]

        farm_id = farm
        if isinstance(farm, str):
            farm = self._farms.get(farm_name=farm)
            farm_id = farm.id

        node_ids = []
        for node in self._nodes.iter(farm_id=farm_id):
            node_ids.append(node.node_id)
        for gw in self._gateways.iter(farm_id=farm_id):
            node_ids.append(gw.node_id)

        pool = self._pools.new()
        pool.data_reservation.pool_id = 0
        pool.data_reservation.cus = cu
        pool.data_reservation.sus = su
        pool.data_reservation.node_ids = node_ids
        pool.data_reservation.currencies = currencies
        return self._reserve(pool)

    def extend(self, pool_id: int, cu: int, su: int, currencies: List[str] = None) -> PoolCreated:
        """
        extend an existing capacity pool

        :param pool_id: the ID of the pool to extend
        :type pool_id: int
        :param cu: amount of compute units to reserve
        :type cu: int
        :param su: amount of storage units to reserve
        :type su: int
        :param currencies: list of currency you are willing to pay with, defaults to None
        :type currencies: List[str], optional
        :return: the payment detail required to pay fo the reserved capacity
        :rtype: PoolCreated
        """
        p = self.get(pool_id)
        if not currencies:
            currencies = ["TFT"]

        pool = self._pools.new()
        pool.data_reservation.pool_id = p.pool_id
        pool.data_reservation.cus = int(p.cus + cu)
        pool.data_reservation.sus = int(p.sus + su)
        pool.data_reservation.node_ids = p.node_ids
        pool.data_reservation.currencies = currencies
        return self._reserve(pool)

    def get(self, pool_id: int) -> Pool:
        """
        get the detail about an specific pool

        :param pool_id: ID of the pool to retrieve
        :type pool_id: int
        :return: Pool
        :rtype: Pool
        """
        return self._pools.get(pool_id)

    def iter(self) -> Iterator[Pool]:
        """
        Iterate over all the pools

        :yield: Pool
        :rtype: Iterator[Pool]
        """
        return self._pools.iter()

    def list(self, page=None) -> List[Pool]:
        """
        List all the pool

        :return: list of pools
        :rtype: pool
        """
        return self._pools.list()
