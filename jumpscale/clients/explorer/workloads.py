from jumpscale.loader import j
from .pagination import get_page, get_all
from .models import (
    TfgridWorkloadsReservationVolume1,
    TfgridWorkloadsReservationContainer1,
    TfgridWorkloadsReservationZdb1,
    TfgridWorkloadsReservationK8s1,
    TfgridWorkloadsReservationGatewayProxy1,
    TfgridWorkloadsReservationGatewayReverse_proxy1,
    TfgridWorkloadsReservationGatewaySubdomain1,
    TfgridDomainsDelegate1,
    TfgridWorkloadsReservationGateway4to61,
    TfgridWorkloadsNetworkNet_resource1,
    TfgridWorkloadsReservationInfo1,
    NextAction,
    Type,
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
            Type.Volume: TfgridWorkloadsReservationVolume1,
            Type.Container: TfgridWorkloadsReservationContainer1,
            Type.Zdb: TfgridWorkloadsReservationZdb1,
            Type.Kubernetes: TfgridWorkloadsReservationK8s1,
            Type.Proxy: TfgridWorkloadsReservationGatewayProxy1,
            Type.Reverse_proxy: TfgridWorkloadsReservationGatewayReverse_proxy1,
            Type.Subdomain: TfgridWorkloadsReservationGatewaySubdomain1,
            Type.Domain_delegate: TfgridDomainsDelegate1,
            Type.Gateway4to6: TfgridWorkloadsReservationGateway4to61,
            Type.Network_resource: TfgridWorkloadsNetworkNet_resource1,
        }

        self._info = TfgridWorkloadsReservationInfo1

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
        self._model_info = TfgridWorkloadsReservationInfo1

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
