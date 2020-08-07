from typing import Union

from jumpscale.clients.explorer.models import DiskType, WorkloadType, ZDBMode, ZdbNamespace

from .crypto import encrypt_for_node


class ZDBGenerator:
    def __init__(self, explorer):
        self._nodes = explorer.nodes

    def create(
        self,
        node_id: str,
        size: int,
        mode: Union[str, ZDBMode],
        password: str,
        pool_id: int,
        disk_type: DiskType = DiskType.SSD,
        public: bool = False,
    ) -> ZdbNamespace:
        """
        create 0-DB namespace workload

        :param node_id: the ID of the node where to deploy the namespace
        :type node_id: str
        :param size: the size of the namespace in GiB
        :type size: int
        :param mode: the mode of the 0-DB. It can be 'seq' or 'user'
        :type mode: Union[str,ZDBMode]
        :param password: password of the namespace. if you don't want password use an empty string
        :type password: str
        :param pool_id: the capacity pool ID
        :type pool_id: int
        :param disk_type: type of disk,can be SSD or HDD, defaults to DiskType.SSD
        :type disk_type: DiskType, optional
        :param public:  if public is True, anyone can write to the namespace without being authenticated, defaults to False
        :type public: bool, optional
        :raise Input: if disk_type is not supported
        :raise Input: if mode is not supported
        :return: ZdbNamespace
        :rtype: ZdbNamespace
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
