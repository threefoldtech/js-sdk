import binascii
from typing import Iterator, List, Union

from jumpscale.clients.explorer.models import NextAction
from jumpscale.loader import j

from .signature import sign_delete_request, sign_workload


class Workloads:
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
        """
        list workloads and optionally filter them by owner or next_action state

        :param customer_tid: filter by user ID
        :type customer_tid: int
        :param next_action: filter by next_action state, defaults to None
        :type next_action: Union[NextAction, str], optional
        :return: [description]
        :rtype: List[ Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, ] ]
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
        iterate over the workloads and optionally filter them by owner or next_action state

        :param customer_tid: filter by user ID
        :type customer_tid: int
        :param next_action: filter by next_action state, defaults to None
        :type next_action: Union[NextAction, str], optional
        :yield: workloads
        :rtype: Iterator[ Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, ] ]
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
        """
        get a specific workload

        :param workload_id:workload id
        :type workload_id: int
        :return: workload
        :rtype: Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, ]
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
        """
        deploy a workload on a node

        :param workload: the workload to provision
        :type workload: Union[ Container, Gateway4to6, GatewayDelegate, GatewayProxy, GatewayReverseProxy, GatewaySubdomain, K8s, NetworkResource, Volume, ZdbNamespace, ]
        :return: the workload ID
        :rtype: int
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
        """
        decomission a workload

        :param workload_id: workload ID
        :type workload_id: int
        """
        me = j.core.identity.me
        workload = self.get(workload_id)
        signature = sign_delete_request(workload, me.tid, me.nacl.signing_key)
        return self._workloads.sign_delete(workload_id, me.tid, signature)
