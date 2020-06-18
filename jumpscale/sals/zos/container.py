import netaddr
from jumpscale.core.exceptions import Input
import base58
from nacl import signing
from .id import _next_workload_id
from nacl import public
import binascii
from jumpscale.clients.explorer.models import (
    TfgridWorkloadsReservationContainer1,
    TfgridWorkloadsReservationContainerLogs1,
    TfgridWorkloadsReservationNetworkConnection1,
    DiskType,
)


class Container:
    def create(
        self,
        reservation,
        node_id,
        network_name,
        ip_address,
        flist,
        env={},
        cpu=1,
        memory=1024,
        disk_size=256,
        disk_type=DiskType.SSD,
        entrypoint="",
        interactive=False,
        secret_env={},
        public_ipv6=False,
        storage_url="zdb://hub.grid.tf:9900",
    ):
        """Creates and add a container to the reservation

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation object
            node_id (str): id of the node of the container
            network_name (str): identifier of the network
            ip_address (str): container ip address in the network
            flist (str): flist url to start the container with
            env (dict, optional): Environment variables to set. Defaults to {}.
            cpu (int, optional): CPU capacity. Defaults to 1.
            memory (int, optional): Memory capacity. Defaults to 1024.
            entrypoint (str, optional): Container init command. Defaults to "".
            interactive (bool, optional): Specifies interactive contaienr start or not. Defaults to False.
            secret_env (dict, optional): Secret Environment variables to set. Defaults to {}.
            public_ipv6 (bool, optional): IPV6 container ip address in the network. Defaults to False.
            storage_url (str, optional): Server used as storage backend. Defaults to "zdb://hub.grid.tf:9900".

        Raises:
            jumpscale.core.exceptions.Input: If ip not in specified network range

        Returns:
            jumpscale.clients.explorer.models.TfgridWorkloadsReservationContainer1: container object
        """

        cont = TfgridWorkloadsReservationContainer1()
        cont.node_id = node_id
        cont.workload_id = _next_workload_id(reservation)

        cont.flist = flist
        cont.storage_url = storage_url
        cont.environment = env
        cont.secret_environment = secret_env
        cont.entrypoint = entrypoint
        cont.interactive = interactive

        nw = None
        for nw in reservation.data_reservation.networks:
            if nw.name == network_name:
                ip = netaddr.IPAddress(ip_address)
                subnet = netaddr.IPNetwork(nw.iprange)
                if ip not in subnet:
                    raise Input(
                        f"ip address {str(ip)} is not in the range of the network resource of the node {str(subnet)}"
                    )

        net = TfgridWorkloadsReservationNetworkConnection1()
        net.network_id = network_name
        net.ipaddress = ip_address
        net.public_ip6 = public_ipv6
        cont.network_connection.append(net)

        cont.capacity.cpu = cpu
        cont.capacity.memory = memory
        cont.capacity.disk_size = disk_size
        cont.capacity.disk_type = disk_type
        reservation.data_reservation.containers.append(cont)

        return cont

    def encrypt_secret(self, node_id, value):
        key = base58.b58decode(node_id)
        pk = signing.VerifyKey(key)
        encryption_key = pk.to_curve25519_public_key()

        box = public.SealedBox(encryption_key)
        result = box.encrypt(value.encode())

        return binascii.hexlify(result).decode()

    def add_logs(self, cont, channel_type, channel_host, channel_port, channel_name):
        """
        Add logs to the container of a reservation

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
        cont_logs = TfgridWorkloadsReservationContainerLogs1()
        cont_logs.type = channel_type
        cont_logs.data.stdout = f"redis://{channel_host}:{channel_port}/{channel_name}-stdout"
        cont_logs.data.stderr = f"redis://{channel_host}:{channel_port}/{channel_name}-stderr"
        cont.logs.append(cont_logs)
        return cont_logs
