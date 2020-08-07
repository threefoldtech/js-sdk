import binascii
from typing import List, Union

import base58
import netaddr
from nacl import public, signing

from jumpscale.clients.explorer.models import (
    Container,
    ContainerLogs,
    ContainerNetworkConnection,
    DiskType,
    WorkloadType,
)
from jumpscale.core.exceptions import Input


class ContainerGenerator:
    def create(
        self,
        node_id: str,
        network_name: str,
        ip_address: str,
        flist: str,
        capacity_pool_id: str,
        env: dict = {},
        cpu: int = 1,
        memory: int = 1024,
        disk_size: int = 256,
        entrypoint: str = "",
        interactive: bool = False,
        secret_env: dict = {},
        public_ipv6: bool = False,
        storage_url: str = "zdb://hub.grid.tf:9900",
    ) -> Container:
        """
        Create a container workload object

        :param node_id:  id of the node where to deploy the container
        :type node_id: str
        :param network_name: name of the network to use in the container
        :type network_name: str
        :param ip_address: container IP address in the network
        :type ip_address: str
        :param flist: url to start the container with
        :type flist: str
        :param capacity_pool_id: id of the capacity pool to use
        :type capacity_pool_id: str
        :param env: Environment variables to set, defaults to {}
        :type env: dict, optional
        :param cpu: virtual CPU to allocate to the container, defaults to 1
        :type cpu: int, optional
        :param memory: Amount of memory to allocate to the container in bytes, defaults to 1024
        :type memory: int, optional
        :param disk_size: Size of the root filesystem of the container in MiB, defaults to 256
        :type disk_size: int, optional
        :param entrypoint: Command to start in the container, defaults to ""
        :type entrypoint: str, optional
        :param interactive: Enable CoreX, web based process manager in the container. If enabled, entrypoint is not automatically started in the container, default to False
        :type interactive: bool, optional
        :param secret_env: Same as env argument, but here the value are encrypted with the public key of the node. Use this to send sensitive information to the container, defaults to {}
        :type secret_env: dict, optional
        :param public_ipv6: requres a public IPv6 address in the container, defaults to False
        :type public_ipv6: bool, optional
        :param storage_url: Address of the server where the data of the flist are stored, defaults to "zdb://hub.grid.tf:9900"
        :type storage_url: str, optional
        :return: Container
        :rtype: Container
        """

        cont = Container()
        cont.info.node_id = node_id
        cont.info.pool_id = capacity_pool_id
        cont.info.workload_type = WorkloadType.Container

        cont.flist = flist
        cont.storage_url = storage_url
        cont.environment = env
        cont.secret_environment = secret_env
        cont.entrypoint = entrypoint
        cont.interactive = interactive

        net = ContainerNetworkConnection()
        net.network_id = network_name
        net.ipaddress = ip_address
        net.public_ip6 = public_ipv6
        cont.network_connection.append(net)

        cont.capacity.cpu = cpu
        cont.capacity.memory = memory
        cont.capacity.disk_size = disk_size
        cont.capacity.disk_type = disk_type

        return cont

    def encrypt_secret(self, node_id: str, value: str) -> str:
        """
        encrypt value with the public key of the node identity by node_id
        use this method to generate the content of 'secret_env' argument of the create method

        :param node_id: target node ID
        :type node_id: str
        :param value: value to encrypt
        :type value: str
        :return: encrypted string
        :rtype: str
        """
        key = base58.b58decode(node_id)
        pk = signing.VerifyKey(key)
        encryption_key = pk.to_curve25519_public_key()

        box = public.SealedBox(encryption_key)
        result = box.encrypt(value.encode())

        return binascii.hexlify(result).decode()

    def add_logs(
        self, container: Container, channel_type: str, channel_host: str, channel_port: str, channel_name: str
    ) -> ContainerLogs:
        """
        Enable log forwarding for the container

        :param cont: container instance
        :type cont: tfgrid.workloads.reservation.container.1
        :param channel_type: type of channel the logs will be streamed to
        :type channel_type: str
        :param channel_host: IP of host that the logs will be streamed to
        :type channel_host: str
        :param channel_port: port of host that the logs will be streamed to
        :type channel_port: int
        :param channel_name: name of channel that will be published to
        :type channel_name: str
        :return: logs object added to the container
        :rtype: tfgrid.workloads.reservation.container.logs.1

        """
        cont_logs = ContainerLogs()
        cont_logs.type = channel_type
        cont_logs.data.stdout = f"redis://{channel_host}:{channel_port}/{channel_name}-stdout"
        cont_logs.data.stderr = f"redis://{channel_host}:{channel_port}/{channel_name}-stderr"
        cont.logs.append(cont_logs)
        return cont_logs
