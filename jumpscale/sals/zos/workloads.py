import binascii
from typing import Iterator, List, Union

from jumpscale.clients.explorer.models import (
    Container,
    Gateway4to6,
    GatewayDelegate,
    GatewayProxy,
    GatewayReverseProxy,
    GatewaySubdomain,
    K8s,
    NetworkResource,
    NextAction,
    Volume,
    ZdbNamespace,
)
from jumpscale.loader import j

from .signature import sign_delete_request, sign_workload


class Workloads:
    """ """

    def __init__(self, explorer):
        self._workloads = explorer.workloads

    def list(
        self, customer_tid: int, next_action: Union[NextAction, str] = None
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
        ]
    ]:
        """list workloads and optionally filter them by owner or next_action state

        Args:
          customer_tid(int): filter by user ID
          next_action(Union[NextAction, str], optional): filter by next_action state, defaults to None

        Returns:
          List[ Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, ] ]: description]

        """
        if isinstance(next_action, NextAction):
            next_action = next_action.name
        return self._workloads.list(customer_tid, next_action)

    def iter(
        self, customer_tid: int, next_action: Union[NextAction, str] = None
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
        ]
    ]:
        """
        Iterate of the workloads

        Args:
            customer_tid (int): filter by user tid
            next_action (Union[NextAction, str], optional): filter by next action. Defaults to None.

        Returns:
            Iterator:

        Yields:
            Iterator[ Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, ] ]
        """
        return self._workloads.iter(customer_tid, next_action)

    def get(
        self, workload_id: int
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
    ]:
        """get a specific workload

        Args:
          workload_id(int): workload id
          workload_id: int:

        Returns:
          Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, ]: workload

        """
        return self._workloads.get(workload_id)

    def deploy(
        self,
        workload: Union[
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
        ],
    ) -> int:
        """deploy a workload on a node

        Args:
          workload(Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, ]): the workload to provision

        Returns:
          int: the workload ID

        """
        me = j.core.identity.me
        workload.info.customer_tid = me.tid
        workload.info.workload_id = 1
        workload.info.epoch = j.data.time.now().timestamp
        workload.info.next_action = NextAction.DEPLOY
        if me.tid not in workload.info.signing_request_delete.signers:
            workload.info.signing_request_delete.signers.append(me.tid)
        if not workload.info.signing_request_delete.quorum_min:
            workload.info.signing_request_delete.quorum_min = 1
        signature = sign_workload(workload, me.nacl.signing_key)
        workload.info.customer_signature = binascii.hexlify(signature).decode()
        return self._workloads.create(workload)

    def decomission(self, workload_id: int):
        """decomission a workload

        Args:
          workload_id(int): workload ID
          workload_id: int:

        Returns:

        """
        me = j.core.identity.me
        workload = self.get(workload_id)
        signature = sign_delete_request(workload, me.tid, me.nacl.signing_key)
        return self._workloads.sign_delete(workload_id, me.tid, signature)
