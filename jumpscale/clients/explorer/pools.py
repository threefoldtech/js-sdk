from typing import Iterator, List

from jumpscale.loader import j

from .models import Pool, PoolCreate, PoolCreated, PoolPayment
from .pagination import get_all, get_page


class Pools:
    def __init__(self, client):
        self._session = client._session
        self._client = client
        self._model = Pool

    @property
    def _base_url(self):
        return self._client.url + "/reservations/pools"

    def new(self) -> PoolCreate:
        """
        create a new empty Pool object

        :return: PoolCreate
        :rtype: PoolCreate
        """
        return PoolCreate()

    def create(self, pool: Pool) -> PoolCreated:
        """
        Register a new capacity pool on the explorer

        :param pool: Pool object
        :type pool: Pool
        :return: returns an object which contains the information required to
                execute the transaction in order to pay for the capacity reserved in the pool
        :rtype: PoolCreated
        """
        resp = self._session.post(self._base_url, json=pool.to_dict())
        return PoolCreated.from_dict(resp.json())

    def list(self, customer_tid: int = None, page: int = None) -> List[Pool]:
        """
        List all the capacity pools

        :param customer_tid: filter the pool owned by the user with ID customer_tid, by default this methond only list your own pools
        :type customer_tid: int, optional
        :return: list of Pool object
        :rtype: list
        """
        if page:
            tid = customer_tid if customer_tid else j.core.identity.me.tid
            url = self._base_url + f"/owner/{tid}"
            reservations, _ = get_page(self._session, page, Pool, url)
        else:
            reservations = list(self.iter(customer_tid))
        return reservations

    def iter(self, customer_tid: int = None) -> Iterator[Pool]:
        """
        Iterate over the capacity pools

        :param customer_tid: filter the pool owned by the user with ID customer_tid, by default this methond only list your own pools
        :type customer_tid: int, optional
        :yield: Pool
        :rtype: Iterator[Pool]
        """
        tid = customer_tid if customer_tid else j.core.identity.me.tid
        url = self._base_url + f"/owner/{tid}"
        yield from get_all(self._session, Pool, url)

    def get(self, pool_id: int) -> Pool:
        """
        get the detail of a specific capacity pool

        :param pool_id: the pool ID to retrieve
        :type pool_id: int
        :return: Pool
        :rtype: Pool
        """
        url = self._base_url + f"/{pool_id}"
        resp = self._session.get(url)
        return Pool.from_dict(resp.json())

    def get_payment_info(self, reservation_id: int) -> PoolPayment:
        """get pool payment info

        Args:
            reservation_id (int)

        Returns:
            PoolPayment: pool payment info
        """
        url = self._base_url + f"/payment/{reservation_id}"
        resp = self._session.get(url)
        return PoolPayment.from_dict(resp.json())
