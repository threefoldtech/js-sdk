from .reservation_chatflow import reservation_chatflow
from .deployer import deployer
from .solutions import solutions
from jumpscale.sals.chatflows.chatflows import StopChatFlow
from contextlib import ContextDecorator
from jumpscale.sals.zos.zos import Zosv2
from jumpscale.clients.explorer.models import WorkloadType
from jumpscale.loader import j


NODE_BLOCKING_WORKLOAD_TYPES = [
    WorkloadType.Container,
    WorkloadType.Network_resource,
    WorkloadType.Volume,
    WorkloadType.Zdb,
]


class DeploymentFailed(StopChatFlow):
    def __init__(self, msg=None, solution_uuid=None, wid=None, **kwargs):
        super().__init__(msg, **kwargs)
        self.solution_uuid = solution_uuid
        self.wid = wid


class deployment_context(ContextDecorator):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        if exc_type != DeploymentFailed:
            return
        if exc.solution_uuid:
            # cancel related workloads
            j.logger.info(f"canceling workload ids of solution_uuid: {exc.solution_uuid}")
            solutions.cancel_solution_by_uuid(exc.solution_uuid)
        if exc.wid:
            # block the failed node if the workload is network or container
            zos = Zosv2()
            workload = zos.workloads.get(exc.wid)
            if workload.info.workload_type in NODE_BLOCKING_WORKLOAD_TYPES:
                j.logger.info(f"blocking node {workload.info.node_id} for failed workload {workload.id}")
                reservation_chatflow.block_node(workload.info.node_id)


# TODO: remove the below on releasing jsng 11.0.0a3

import jumpscale.tools.http
from jumpscale.core.exceptions import Input
import gevent


def wait_http_test(url: str, timeout: int = 60, verify: bool = True) -> bool:
    """Will wait until url is reachable

    Args:
        url (str): url
        timeout (int, optional): how long to wait for the connection. Defaults to 60.
        verify (bool, optional): boolean indication to verify the servers TLS certificate or not.


    Returns:
        bool: true if the test succeeds
    """
    for _ in range(timeout):
        try:
            if check_url_reachable(url, timeout=1, verify=verify):
                return True
        except:
            pass

        gevent.sleep(1)
    else:
        return False


def check_url_reachable(url: str, timeout=5, verify=True):
    """Check that given url is reachable

    Args:
        url (str): url to test
        timeout (int, optional): timeout of test. Defaults to 5.
        verify (bool, optional): boolean indication to verify the servers TLS certificate or not.

    Raises:
        Input: raises if not correct url

    Returns:
        bool: True if the test succeeds, False otherwise
    """
    try:
        code = jumpscale.tools.http.get(url, timeout=timeout, verify=verify).status_code
        return code == 200
    except jumpscale.tools.http.exceptions.MissingSchema:
        raise Input("Please specify correct url with correct scheme")
    except jumpscale.tools.http.exceptions.ConnectionError:
        return False
