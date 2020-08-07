from typing import List

from jumpscale.clients.explorer.models import K8s, WorkloadType
from jumpscale.core.exceptions import Input

from .crypto import encrypt_for_node


class KubernetesGenerator:
    def __init__(self, explorer):
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
    ) -> K8s:
        """
        create a kubernetes marster workload object

        :param node_id: node ID on which to deploy the k8s master
        :type node_id: str
        :param network_name: name of the network to use
        :type network_name: str
        :param cluster_secret: secret of the cluster. all the member of a same cluster must share the same secret
        :type cluster_secret: str
        :param ip_address: ip address of the k8s master
        :type ip_address: str
        :param size: size of the VM.
        :type size: int
        :param ssh_keys: list of public SSH key to authorize in the VM
        :type ssh_keys: List[str]
        :param pool_id: capacity pool ID
        :type pool_id: int
        :raises Input: if size is not supported
        :return: K8s
        :rtype: K8s
        """
        if size not in [1, 2]:
            raise Input("size can only be 1 or 2")

        master = K8s()
        master.info.node_id = node_id
        master.info.workload_type = WorkloadType.Kubernetes
        master.info.pool_id = pool_id

        node = self._nodes.get(node_id)
        master.cluster_secret = encrypt_for_node(node.public_key_hex, cluster_secret).decode()
        master.network_id = network_name
        master.ipaddress = ip_address
        master.size = size
        if not isinstance(ssh_keys, list):
            ssh_keys = [ssh_keys]
        master.ssh_keys = ssh_keys

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
    ) -> K8s:
        """
        create a kubernetes worker workload object

        :param node_id: node ID on which to deploy the k8s master
        :type node_id: str
        :param network_name: name of the network to use
        :type network_name: str
        :param cluster_secret: secret of the cluster. all the member of a same cluster must share the same secret
        :type cluster_secret: str
        :param ip_address: ip address of the k8s master
        :type ip_address: str
        :param size: size of the VM.
        :type size: int
        :param ssh_keys: list of public SSH key to authorize in the VM
        :type ssh_keys: List[str]
        :param master_ip: IP address of the master node of this cluster
        :type master_ip: str
        :param pool_id: capacity pool ID
        :type pool_id: int
        :raises Input: if size is not supported
        :return: K8s
        :rtype: K8s
        """
        worker = self.add_master(
            node_id=node_id,
            network_name=network_name,
            cluster_secret=cluster_secret,
            ip_address=ip_address,
            size=size,
            ssh_keys=ssh_keys,
            pool_id=pool_id,
        )
        worker.master_ips = [master_ip]
        return worker
