import binascii
from typing import List, Union

import base58
import netaddr
from nacl import public, signing

from jumpscale.clients.explorer.models import (
    Container,
    ContainerLogs,
    ContainerStats,
    ContainerNetworkConnection,
    DiskType,
    WorkloadType,
)

from jumpscale.core.exceptions import Input
from jumpscale.tools.zos.monitor import ContainerStatsMonitor

from .crypto import encrypt_for_node


class ContainerGenerator:
    def __init__(self, identity):
        self._identity = identity

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
        """Create a container workload object

        Args:
          node_id(str): id of the node where to deploy the container
          network_name(str): name of the network to use in the container
          ip_address(str): container IP address in the network
          flist(str): url to start the container with
          capacity_pool_id(str): id of the capacity pool to use
          env(dict, optional): Environment variables to set, defaults to {}
          cpu(int, optional): virtual CPU to allocate to the container, defaults to 1
          memory(int, optional): Amount of memory to allocate to the container in bytes, defaults to 1024
          disk_size(int, optional): Size of the root filesystem of the container in MiB, defaults to 256
          entrypoint(str, optional): Command to start in the container, defaults to ""
          interactive(bool, optional): Enable CoreX, web based process manager in the container. If enabled, entrypoint is not automatically started in the container, default to False
          secret_env(dict, optional): Same as env argument, but here the value are encrypted with the public key of the node. Use this to send sensitive information to the container, defaults to {}
          public_ipv6(bool, optional): requres a public IPv6 address in the container, defaults to False
          storage_url(str, optional): Address of the server where the data of the flist are stored, defaults to "zdb://hub.grid.tf:9900"

        Returns:
          Container: Container
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
        cont.capacity.disk_type = DiskType.SSD

        return cont

    def encrypt_secret(self, node_id: str, value: str) -> str:
        """encrypt value with the public key of the node identity by node_id
        use this method to generate the content of 'secret_env' argument of the create method

        Args:
          node_id(str): target node ID
          value(str): value to encrypt
          node_id: str:
          value: str:

        Returns:
          str: encrypted string
        """
        bkey = base58.b58decode(node_id)
        node_public_hex = binascii.hexlify(bkey)

        encrypted = encrypt_for_node(self._identity, node_public_hex, value)
        return encrypted.decode()

    def add_logs(
        self, container: Container, channel_type: str, channel_host: str, channel_port: str, channel_name: str
    ) -> ContainerLogs:
        """Enable log forwarding for the container

        Args:
          cont(tfgrid.workloads.reservation.container.1): container instance
          channel_type(str): type of channel the logs will be streamed to
          channel_host(str): IP of host that the logs will be streamed to
          channel_port(int): port of host that the logs will be streamed to
          channel_name(str): name of channel that will be published to

        Returns:
          tfgrid.workloads.reservation.container.logs.1: logs object added to the container

        """
        stdout = f"redis://{channel_host}:{channel_port}/{channel_name}-stdout"
        stderr = f"redis://{channel_host}:{channel_port}/{channel_name}-stderr"

        cont_logs = ContainerLogs()
        cont_logs.type = channel_type
        cont_logs.data.secret_stdout = self.encrypt_secret(container.info.node_id, stdout)
        cont_logs.data.secret_stderr = self.encrypt_secret(container.info.node_id, stderr)
        container.logs.append(cont_logs)

        return cont_logs

    def add_stats(self, container: Container, redis_endpoint: str) -> ContainerStats:
        """Enable statistics forwarding for the container

        Args:
          container(Container): container instance
          redis_endpoint(str): redis endpoint (redis://host:port/channel)

        Returns:
          ContainerStats: stats object added to the container

        """
        cont_stats = ContainerStats()
        cont_stats.type = "redis"
        cont_stats.data.endpoint = redis_endpoint
        container.stats.append(cont_stats)

        return cont_stats

    def monitor(self, container):
        """Try to reach endpoint from container statistics and fetch stats when available"""
        if not container.stats:
            return False

        stats = ContainerStatsMonitor()
        stats.endpoint(container.stats[0].data.endpoint)
        stats.monitor()

    def monitor_reservation(self, reservation):
        """Try to reach endpoint from container reservation data and monitor stats"""
        stats = ContainerStatsMonitor()
        stats.reservation(reservation)
        stats.monitor()
