import binascii
from typing import Iterator, List, Union
import gevent

from jumpscale.loader import j

from .models import (
    Container,
    Gateway4to6,
    GatewayDelegate,
    GatewayProxy,
    GatewayReverseProxy,
    GatewaySubdomain,
    K8s,
    NetworkResource,
    NextAction,
    ReservationInfo,
    Volume,
    WorkloadType,
    ZdbNamespace,
    PublicIP,
    VirtualMachine,
)
from .pagination import get_all, get_page


class Decoder:
    @classmethod
    def from_dict(cls, datadict):
        obj = cls(data=datadict)
        return obj.workload()

    def __init__(self, data):
        self.data = data
        self._models = {
            WorkloadType.Volume: Volume,
            WorkloadType.Container: Container,
            WorkloadType.Zdb: ZdbNamespace,
            WorkloadType.Kubernetes: K8s,
            WorkloadType.Proxy: GatewayProxy,
            WorkloadType.Reverse_proxy: GatewayReverseProxy,
            WorkloadType.Subdomain: GatewaySubdomain,
            WorkloadType.Domain_delegate: GatewayDelegate,
            WorkloadType.Gateway4to6: Gateway4to6,
            WorkloadType.Network_resource: NetworkResource,
            WorkloadType.Public_IP: PublicIP,
            WorkloadType.Virtual_Machine: VirtualMachine,
        }

    def workload(self):
        info = ReservationInfo.from_dict(self.data)
        model = self._models.get(info.workload_type)
        if not model:
            raise j.core.exceptions.Input("unsupported workload type %s" % info.workload_type)
        workload = model.from_dict(self.data)
        workload.info = info
        return workload


def _build_query(customer_tid: int = None, next_action: str = None) -> dict:
    query = {}
    if customer_tid:
        query["customer_tid"] = customer_tid
    if next_action:
        query["next_action"] = _next_action(next_action).value
    return query


def _next_action(next_action) -> NextAction:
    if isinstance(next_action, str):
        next_action = NextAction[next_action.upper()]
    return next_action


class Workloads:
    def __init__(self, client):
        self._session = client._session
        self._client = client

    @property
    def _base_url(self):
        return self._client.url + "/reservations/workloads"

    def create(self, workload) -> int:
        """
        Provision a workload on the grid

        :param workload: workload to provision
        :type workload: Workload
        :return: the workload ID
        :rtype: int
        """
        url = self._base_url
        data = workload.to_dict()
        del data["info"]["result"]
        info = data.pop("info")
        data.update(info)
        resp = self._session.post(url, json=data)
        return resp.json().get("reservation_id")

    def list(
        self, customer_tid: int = None, next_action: str = None, page=None
    ) -> List[
        Union[
            Container,
            Gateway4to6,
            GatewayDelegate,
            GatewayProxy,
            GatewayReverseProxy,
            GatewaySubdomain,
            K8s,
            NetworkResource,
            Volume,
            ZdbNamespace,
            PublicIP,
        ]
    ]:
        """
        List workloads

        :param customer_tid: filter by customer ID, defaults to None
        :type customer_tid: int, optional
        :param next_action: filter by workload next action value, defaults to None
        :type next_action: str, optional
        :return: [description]
        :rtype: [type]
        """
        url = self._base_url
        if page:
            query = _build_query(customer_tid=customer_tid, next_action=next_action)
            workloads, _ = get_page(self._session, page, Decoder, url, query)
        else:
            workloads = list(self.iter(customer_tid, next_action))
        return workloads

    def iter(
        self, customer_tid: int = None, next_action: str = None
    ) -> Iterator[
        Union[
            Container,
            Gateway4to6,
            GatewayDelegate,
            GatewayProxy,
            GatewayReverseProxy,
            GatewaySubdomain,
            K8s,
            NetworkResource,
            Volume,
            ZdbNamespace,
            PublicIP,
        ]
    ]:
        """
        return an iterator that yield workloads

        :param customer_tid: filter by customer ID, defaults to None
        :type customer_tid: int, optional
        :param next_action: filter by workload next action value, defaults to None
        :type next_action: str, optional
        :yield: Workload
        :rtype: Iterator[Workload]
        """
        if next_action:
            next_action = _next_action(next_action)

        def filter_next_action(reservation):
            if next_action is None:
                return True
            return reservation.info.next_action == next_action

        url = self._base_url

        query = _build_query(customer_tid=customer_tid, next_action=next_action)
        yield from filter(filter_next_action, get_all(self._session, Decoder, url, query))

    def get(
        self, workload_id
    ) -> Union[
        Container,
        Gateway4to6,
        GatewayDelegate,
        GatewayProxy,
        GatewayReverseProxy,
        GatewaySubdomain,
        K8s,
        NetworkResource,
        Volume,
        ZdbNamespace,
        PublicIP,
    ]:
        """
        get a specific workload

        :param workload_id: workload ID
        :type workload_id: int
        :return: Workload
        :rtype: Workload
        """
        url = self._base_url + f"/{workload_id}"
        resp = self._session.get(url)
        return Decoder.from_dict(datadict=resp.json())

    def sign_provision(self, workload_id: int, tid: int, signature: bytes) -> bool:
        """
        add a provision signature to a workload

        this is required when the workload requires some extra signature to be provisioned

        :param workload_id: workload id
        :type workload_id: int
        :param tid: the ID of the user sending the signature
        :type tid: int
        :param signature: the signature
        :type signature: bytes
        :return: true if the signature was properly registered
        :rtype: bool
        """
        url = self._base_url + f"/{workload_id}/sign/provision"
        data = j.data.serializers.json.dumps({"signature": signature, "tid": tid, "epoch": j.data.time.now().timestamp})
        self._session.post(url, data=data)
        return True

    def sign_delete(self, workload_id: int, tid: int, signature: bytes) -> bool:
        """
        add a deletion signature to a workload

        this is required when the workload requires some extra signature to be deleted

        :param workload_id: workload id
        :type workload_id: int
        :param tid: the ID of the user sending the signature
        :type tid: int
        :param signature: the signature
        :type signature: bytes
        :return: true if the signature was properly registered
        :rtype: bool
        """
        url = self._base_url + f"/{workload_id}/sign/delete"

        if isinstance(signature, bytes):
            signature = binascii.hexlify(signature).decode()

        data = j.data.serializers.json.dumps({"signature": signature, "tid": tid, "epoch": j.data.time.now().timestamp})
        self._session.post(url, data=data)
        return True

    def list_workloads(
        self, customer_tid: int = None, next_action: str = None, page=None
    ) -> List[
        Union[
            Container,
            Gateway4to6,
            GatewayDelegate,
            GatewayProxy,
            GatewayReverseProxy,
            GatewaySubdomain,
            K8s,
            NetworkResource,
            Volume,
            ZdbNamespace,
            PublicIP,
        ]
    ]:
        """List workloads by gevent

        Args:
            customer_tid (int, optional): filter by customer ID. Defaults to None.
            next_action (str, optional): filter by workload next action value,. Defaults to None.
            page ([type], optional): page number to filter with. Defaults to None.

        Returns:
            List[ Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, PublicIP, ] ]: List of user's workloads
        """
        workloads = []
        url = self._base_url
        if page:
            query = _build_query(customer_tid=customer_tid, next_action=next_action)
            workloads, pages_no = get_page(self._session, page, Decoder, url, query)
        else:
            # get pages number
            query = _build_query(customer_tid=customer_tid, next_action=next_action)
            workloads, pages_no = get_page(self._session, 1, Decoder, url, query)

            def get_page_workloads(page):
                workloads.extend(self.list(customer_tid, next_action, page=page))

            threads = []
            for p in range(2, pages_no + 1):
                thread = gevent.spawn(get_page_workloads, p)
                threads.append(thread)
            gevent.joinall(threads)

        return workloads
