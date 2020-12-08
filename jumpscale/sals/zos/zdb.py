from typing import Union

from jumpscale.clients.explorer.models import DiskType, WorkloadType, ZDBMode, ZdbNamespace

from .crypto import encrypt_for_node


class ZDBGenerator:
    def __init__(self, identity):
        self._identity = identity
        explorer = self._identity.explorer
        self._nodes = explorer.nodes

    def create(
        self,
        node_id: str,
        size: int,
        mode: Union[str, ZDBMode],
        password: str,
        pool_id: int,
        disk_type: Union[str, DiskType] = DiskType.SSD,
        public: bool = False,
    ) -> ZdbNamespace:
        """create 0-DB namespace workload

        Args:
          node_id(str): the ID of the node where to deploy the namespace
          size(int): the size of the namespace in GiB
          mode(Union[str,ZDBMode]): the mode of the 0-DB. It can be 'seq' or 'user'
          password(str): password of the namespace. if you don't want password use an empty string
          pool_id(int): the capacity pool ID
          disk_type(DiskType, optional): type of disk,can be SSD or HDD, defaults to DiskType.SSD
          public(bool, optional

        Returns:
          ZdbNamespace: ZdbNamespace
        """
        if isinstance(disk_type, str):
            disk_type = getattr(DiskType, disk_type)

        if isinstance(mode, str):
            mode = getattr(ZDBMode, mode.title())

        zdb = ZdbNamespace()
        zdb.info.node_id = node_id
        zdb.info.pool_id = pool_id
        zdb.info.workload_type = WorkloadType.Zdb
        zdb.size = size
        zdb.mode = mode
        if password:
            node = self._nodes.get(node_id)
            zdb.password = encrypt_for_node(self._identity, node.public_key_hex, password).decode()
        zdb.disk_type = disk_type
        return zdb
