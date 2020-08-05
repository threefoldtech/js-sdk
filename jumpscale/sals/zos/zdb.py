from .crypto import encrypt_for_node
from jumpscale.clients.explorer.models import ZdbNamespace, DiskType, WorkloadType


class ZDBGenerator:
    def __init__(self, explorer):
        self._nodes = explorer.nodes

    def create(self, node_id, size, mode, password, pool_id, disk_type=DiskType.SSD, public=False):
        """add a 0-db namespace workload to the reservation

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation obejct to add the volume to
            node_id (str): id of the node to reserve the volume
            size (int): size of the namespace in GiB
            mode (str): mode of the 0-db, can be 'seq' or 'user'
            password (str): password of the namespace. if you don't want password use an empty string
            disk_type (str, optional): type of disk,can be SSD or HDD. Defaults to "SSD".
            public (bool, optional): if public is True, anyone can write to the namespace without being authenticated. Defaults to False.

        Raises:
            Input: if disk_type os not supported
            Input: if mode is not suported

        Returns:
            [type]: newly created zdb workload
        """

        zdb = ZdbNamespace()
        zdb.info.node_id = node_id
        zdb.info.pool_id = pool_id
        zdb.info.workload_type = WorkloadType.Zdb
        zdb.size = size
        zdb.mode = mode
        if password:
            node = self._nodes.get(node_id)
            zdb.password = encrypt_for_node(node.public_key_hex, password).decode()
        zdb.disk_type = disk_type
        return zdb
