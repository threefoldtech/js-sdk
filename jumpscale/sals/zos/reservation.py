from .network import Network
from jumpscale.clients.explorer.models import Type

_order = [
    Type.Network_resource,
    Type.Network,
    Type.Zdb,
    Type.Volume,
    Type.Container,
    Type.Kubernetes,
    Type.Domain_delegate,
    Type.Subdomain,
    Type.Proxy,
    Type.Reverse_proxy,
    Type.Gateway4to6,
]


class Reservation:
    def __init__(self):
        self.workloads = []

    @property
    def sorted(self):
        """
        return the list of workload sorted in the other they should be deployed on the node
        """
        workloads = sorted(self.workloads, key=lambda w: _order.index(w.info.workload_type))
        out = []
        for w in workloads:
            if isinstance(w, Network):
                out.extend(w.network_resources)
            else:
                out.append(w)
        return out

    def __repr__(self):
        per_type = {}
        for w in self.workloads:
            wt = str(w.info.workload_type)
            if wt not in per_type:
                per_type[wt] = []

            if wt == "NETWORK_RESOURCE":
                per_type[wt].extend(w.network_resources)
            else:
                per_type[wt].append(w)

        return str(per_type)

    def __str__(self):
        return str(self)
