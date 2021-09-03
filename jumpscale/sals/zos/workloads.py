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
    VirtualMachine,
    Volume,
    ZdbNamespace,
    PublicIP,
)
from jumpscale.loader import j

from .signature import sign_delete_request, sign_workload


class Workloads:
    """ """

    def __init__(self, identity):
        self._identity = identity
        explorer = self._identity.explorer
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
            PublicIP,
        ]
    ]:
        """list workloads and optionally filter them by owner or next_action state

        Args:
          customer_tid(int): filter by user ID
          next_action(Union[NextAction, str], optional): filter by next_action state, defaults to None

        Returns:
          List[ Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, PublicIP, ] ]: description]

        """
        if isinstance(next_action, NextAction):
            next_action = next_action.name
        return self._workloads.list(customer_tid, next_action)

    def list_workloads(
        self, customer_tid: int, next_action: Union[NextAction, str] = None, page=None
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
        """list workloads by gevent and optionally filter them by owner or next_action state

        Args:
          customer_tid(int): filter by user ID
          next_action(Union[NextAction, str], optional): filter by next_action state, defaults to None
          page ([type], optional): page number to filter with. Defaults to None.

        Returns:
          List[ Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, PublicIP, ] ]: description]

        """
        if isinstance(next_action, NextAction):
            next_action = next_action.name
        return self._workloads.list_workloads(customer_tid, next_action, page=page)

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
            PublicIP,
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
            Iterator[ Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, PublicIP, ] ]
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
        PublicIP,
    ]:
        """get a specific workload

        Args:
          workload_id(int): workload id
          workload_id: int:

        Returns:
          Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, PublicIP, ]: workload

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
            PublicIP,
            VirtualMachine,
        ],
    ) -> int:
        """deploy a workload on a node

        Args:
          workload(Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, PublicIP, ]): the workload to provision

        Returns:
          int: the workload ID

        """
        me = self._identity
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
        me = self._identity
        workload = self.get(workload_id)
        if workload.info.next_action.value > 3:
            # workload is not deployed
            return
        signature = sign_delete_request(workload, me.tid, me.nacl.signing_key)
        return self._workloads.sign_delete(workload_id, me.tid, signature)

    def wait(self, wid, timeout=5):
        expiration = j.data.time.now().timestamp + timeout * 60
        while j.data.time.now().timestamp < expiration:
            workload = self.get(wid)
            if not workload.info.result.workload_id:
                continue

            success = workload.info.result.state.value == 1
            msg = workload.info.result.message
            return success, msg
        raise j.exceptions.Timeout(f"waiting for workload {wid} timeout")
