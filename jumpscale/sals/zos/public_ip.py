from jumpscale.core.exceptions import Input
from jumpscale.clients.explorer.models import PublicIP, WorkloadType
from typing import Union


class PublicIPSGenerator:
    """ """

    def create(self, node_id: str, pool_id: int, ip: str, destination_ip: str) -> PublicIP:
        """Create a public IP reservation

        Args:
          node_id(str): id of the node where to reserve the PublicIP
          pool_id(int) the capacity pool ID
          ip(str) the public IP that needs to be reserved.
          destination_ip(str) the private destination ip on the node.

        Returns:
          PublicIP: the newly created publicIP object
        """

        public_ip = PublicIP()
        public_ip.ip = ip
        public_ip.destination_ip = destination_ip
        public_ip.info.node_id = node_id
        public_ip.info.pool_id = pool_id
        public_ip.info.workload_type = WorkloadType.Public_IP
        return public_ip

