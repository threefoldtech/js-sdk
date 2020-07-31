from jumpscale.loader import j
from .pagination import get_page, get_all
from .models import (
    Volume,
    Container,
    ZdbNamespace,
    K8s,
    GatewayProxy,
    GatewayReverseProxy,
    GatewaySubdomain,
    GatewayDelegate,
    Gateway4to6,
    NetworkResource,
    ReservationInfo,
    NextAction,
    WorkloadType,
)
import binascii


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
        }

        self._info = ReservationInfo

    def workload(self):
        info = self._info.from_dict(self.data)
        model = self._models.get(info.workload_type)
        if not model:
            raise j.core.exceptions.Input("unsupported workload type %s" % info.workload_type)
        workload = model.from_dict(self.data)
        workload.info = info
        return workload


class Workoads:
    def __init__(self, client):
        self._session = client._session
        self._client = client
        self._model_info = ReservationInfo

    @property
    def _base_url(self):
        return self._client.url + "/reservations/workloads"

    def new(self):
        return self._model_info()

    def create(self, workload):
        url = self._base_url
        data = workload.to_dict()
        del data["info"]["result"]
        info = data.pop("info")
        data.update(info)
        resp = self._session.post(url, json=data)
        return resp.json().get("reservation_id")

    def list(self, customer_tid=None, next_action=None, page=None):
        url = self._base_url
        if page:
            query = {}
            if customer_tid:
                query["customer_tid"] = customer_tid
            if next_action:
                query["next_action"] = self._next_action(next_action).value
            workloads, _ = get_page(self._session, page, Decoder, url, query)
        else:
            workloads = list(self.iter(customer_tid, next_action))
        return workloads

    def _next_action(self, next_action):
        if isinstance(next_action, str):
            next_action = NextAction[next_action.upper()]
        return next_action

    def iter(self, customer_tid=None, next_action=None):
        if next_action:
            next_action = self._next_action(next_action)

        def filter_next_action(reservation):
            if next_action is None:
                return True
            return reservation.info.next_action == next_action

        url = self._base_url

        query = {}
        if customer_tid:
            query["customer_tid"] = customer_tid
        if next_action:
            query["next_action"] = next_action.value
        yield from filter(filter_next_action, get_all(self._session, Decoder, url, query))

    def get(self, workload_id):
        url = self._base_url + f"/{workload_id}"
        resp = self._session.get(url)
        return Decoder.from_dict(datadict=resp.json())

    def sign_provision(self, workload_id, tid, signature):
        url = self._base_url + f"/{workload_id}/sign/provision"
        data = j.data.serializers.json.dumps({"signature": signature, "tid": tid, "epoch": j.data.time.now().timestamp})
        self._session.post(url, data=data)
        return True

    def sign_delete(self, workload_id, tid, signature):
        url = self._base_url + f"/{workload_id}/sign/delete"

        if isinstance(signature, bytes):
            signature = binascii.hexlify(signature).decode()

        data = j.data.serializers.json.dumps({"signature": signature, "tid": tid, "epoch": j.data.time.now().timestamp})
        self._session.post(url, data=data)
        return True
