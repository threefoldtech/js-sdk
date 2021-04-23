from typing import List

from jumpscale.clients.explorer.models import VirtualMachine, WorkloadType


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
        flist: str,
        ip_address: str,
        ssh_keys: List[str],
        pool_id: int,
        public_ip_wid: int = 0,
        cpu: int = 1,
        memory: int = 1024,
        disk_size: int = 256,
    ) -> VirtualMachine:
        """create a virtual machine

        Args:
          node_id(str): node ID on which to deploy the vm
          network_name(str): name of the network to use
          ip_address(str): ip address of the vm
          ssh_keys(List[str]): list of public SSH key to authorize in the VM
          pool_id(int): capacity pool ID
          flist(str): the flist url of the vm
          public_ip_wid(int): The workload public ip
        Returns:
          vm: VirtualMachine

        """
        vm = VirtualMachine()
        vm.info.node_id = node_id
        vm.info.workload_type = WorkloadType.VirtualMachine
        vm.info.pool_id = pool_id

        vm.network_id = network_name
        vm.ipaddress = ip_address
        if not isinstance(ssh_keys, list):
            ssh_keys = [ssh_keys]
        vm.ssh_keys = ssh_keys
        vm.public_ip = public_ip_wid
        vm.flist = flist
        vm.capacity.cpu = cpu
        vm.capacity.memory = memory
        vm.capacity.disk_size = disk_size

        return vm
