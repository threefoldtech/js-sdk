from jumpscale.loader import j
from jumpscale.clients.explorer.models import NextAction
import binascii
from .signature import sign_workload, sign_delete_request


class Workloads:
    def __init__(self, explorer):
        self._workloads = explorer.workloads

    def list(self, customer_tid, next_action=None):
        return self._workloads.list(customer_tid, next_action)

    def iter(self, customer_tid=None, next_action=None):
        return self._workloads.iter(customer_tid, next_action)

    def get(self, workload_id):
        return self._workloads.get(workload_id)

    def deploy(self, workload):
        me = j.core.identity.me
        workload.info.customer_tid = me.tid
        workload.info.workload_id = 1
        workload.info.epoch = j.data.time.now().timestamp
        workload.info.next_action = NextAction.DEPLOY
        workload.info.signing_request_delete.signers = [me.tid]
        workload.info.signing_request_delete.quorum_min = 1
        signature = sign_workload(workload, me.nacl.signing_key)
        workload.info.customer_signature = binascii.hexlify(signature).decode()
        return self._workloads.create(workload)

    def decomission(self, workload_id):
        me = j.core.identity.me
        workload = self.get(workload_id)
        signature = sign_delete_request(workload, me.tid, me.nacl.signing_key)
        return self._workloads.sign_delete(workload_id, me.tid, signature)
