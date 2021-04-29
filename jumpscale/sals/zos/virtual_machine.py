from typing import List

from jumpscale.clients.explorer.models import VirtualMachine, WorkloadType
from jumpscale.core.exceptions import Input


class VMGenerator:
    """ """

    def __init__(self, identity):
        self._identity = identity
        explorer = identity.explorer
        self._nodes = explorer.nodes

    def create(
        self,
        node_id: str,
        network_name: str,
        name: str,
        ip_address: str,
        ssh_keys: List[str],
        pool_id: int,
        size: int,
        public_ip_wid: int = 0,
    ) -> VirtualMachine:
        """create a virtual machine

        Args:
          node_id(str): node ID on which to deploy the vm
          network_name(str): name of the network to use
          ip_address(str): ip address of the vm
          ssh_keys(List[str]): list of public SSH key to authorize in the VM
          pool_id(int): capacity pool ID
          name(str): the name of the vm image to deploy
          public_ip_wid(int): The workload public ip
        Returns:
          vm: VirtualMachine

        """
        if size not in range(1, 19):
            raise Input(f"VM size {size} is not supported")

        vm = VirtualMachine()
        vm.info.node_id = node_id
        vm.info.workload_type = WorkloadType.Virtual_Machine
        vm.info.pool_id = pool_id

        vm.network_id = network_name
        vm.ipaddress = ip_address
        if not isinstance(ssh_keys, list):
            ssh_keys = [ssh_keys]
        vm.ssh_keys = ssh_keys
        vm.public_ip = public_ip_wid
        vm.name = name
        vm.size = size

        return vm
