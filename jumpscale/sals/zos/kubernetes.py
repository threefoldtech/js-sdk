from typing import List

from jumpscale.clients.explorer.models import K8s, WorkloadType
from jumpscale.core.exceptions import Input

from .crypto import encrypt_for_node


class KubernetesGenerator:
    """ """

    def __init__(self, identity):
        self._identity = identity
        explorer = identity.explorer
        self._nodes = explorer.nodes

    def add_master(
        self,
        node_id: str,
        network_name: str,
        cluster_secret: str,
        ip_address: str,
        size: int,
        ssh_keys: List[str],
        pool_id: int,
        public_ip_wid: int = 0,
        disable_default_ingress=True,
        datastore_endpoint="",
    ) -> K8s:
        """create a kubernetes marster workload object

        Args:
          node_id(str): node ID on which to deploy the k8s master
          network_name(str): name of the network to use
          cluster_secret(str): secret of the cluster. all the member of a same cluster must share the same secret
          ip_address(str): ip address of the k8s master
          size(int): size of the VM.
          ssh_keys(List[str]): list of public SSH key to authorize in the VM
          pool_id(int): capacity pool ID

        Returns:
          K8s: K8s

        Raises:
          Input: if size is not supported

        """
        if size not in range(1, 19):
            raise Input(f"VM size {size} is not supported")

        master = K8s()
        master.info.node_id = node_id
        master.info.workload_type = WorkloadType.Kubernetes
        master.info.pool_id = pool_id

        node = self._nodes.get(node_id)
        master.cluster_secret = encrypt_for_node(self._identity, node.public_key_hex, cluster_secret).decode()
        master.network_id = network_name
        master.ipaddress = ip_address
        master.size = size
        if not isinstance(ssh_keys, list):
            ssh_keys = [ssh_keys]
        master.ssh_keys = ssh_keys
        master.public_ip = public_ip_wid
        master.disable_default_ingress = disable_default_ingress
        master.datastore_endpoint = datastore_endpoint

        return master

    def add_worker(
        self,
        node_id: str,
        network_name: str,
        cluster_secret: str,
        ip_address: str,
        size: int,
        master_ip: str,
        ssh_keys: List[str],
        pool_id: int,
        public_ip_wid: int = 0,
    ) -> K8s:
        """create a kubernetes worker workload object

        Args:
          node_id(str): node ID on which to deploy the k8s master
          network_name(str): name of the network to use
          cluster_secret(str): secret of the cluster. all the member of a same cluster must share the same secret
          ip_address(str): ip address of the k8s master
          size(int): size of the VM.
          ssh_keys(List[str]): list of public SSH key to authorize in the VM
          master_ip(str): IP address of the master node of this cluster
          pool_id(int): capacity pool ID

        Returns:
          K8s: K8s

        Raises:
          Input: if size is not supported

        """
        worker = self.add_master(
            node_id=node_id,
            network_name=network_name,
            cluster_secret=cluster_secret,
            ip_address=ip_address,
            size=size,
            ssh_keys=ssh_keys,
            pool_id=pool_id,
            public_ip_wid=public_ip_wid,
            disable_default_ingress=False,
        )
        worker.master_ips = [master_ip]
        return worker
