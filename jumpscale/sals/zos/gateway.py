from typing import List

import netaddr

from jumpscale.clients.explorer.models import (
    Gateway4to6,
    GatewayDelegate,
    GatewayProxy,
    GatewayReverseProxy,
    GatewaySubdomain,
    WorkloadType,
)
from jumpscale.core.exceptions import Input

from .crypto import encrypt_for_node


class GatewayGenerator:
    def __init__(self, explorer):
        self._gateways = explorer.gateway

    def sub_domain(self, gateway_id: str, domain: str, ips: List[str], pool_id: int) -> GatewaySubdomain:
        """
        create a sub-domain workload object

        :param gateway_id: the ID of the gateway where the create the sub-domain
        :type gateway_id: str
        :param domain: sub-domain to create
        :type domain: str
        :param ips: list of target IP pointed by the sub-domain
        :type ips: List[str]
        :param pool_id: capacity pool ID
        :type pool_id: int
        :return: Subdomain
        :rtype: Subdomain
        """
        for ip in ips:
            if not _is_valid_ip(ip):
                raise Input(f"{ip} is not valid IP address")

        sb = GatewaySubdomain()
        sb.info.node_id = gateway_id
        sb.domain = domain
        sb.ips = ips
        sb.info.workload_type = WorkloadType.Subdomain
        sb.info.pool_id = pool_id
        return sb

    def delegate_domain(self, gateway_id: str, domain: str, pool_id: int) -> GatewayDelegate:
        """
        create a domain delegation workload object

        :param gateway_id: the ID of the gateway that will manage the delegated domain
        :type gateway_id: str
        :param domain: domain to delegate
        :type domain: str
        :param pool_id: capacity pool ID
        :type pool_id: int
        :return: GatewayDelegate
        :rtype: GatewayDelegate
        """
        d = GatewayDelegate()
        d.info.node_id = gateway_id
        d.domain = domain
        d.info.workload_type = WorkloadType.Domain_delegate
        d.info.pool_id = pool_id
        return d

    def tcp_proxy(
        self, gateway_id: str, domain: str, addr: str, port: int, port_tls: int, pool_id: int
    ) -> GatewayProxy:
        """
        create a proxy workload object

        :param gateway_id: the ID of the gateway where to configure the proxy
        :type gateway_id: str
        :param domain: domain that will be proxied to the addr:port
        :type domain: str
        :param addr: destination address where to proxy the traffic
        :type addr: str
        :param port: destination port where to proxy the normal traffic
        :type port: int
        :param port_tls:  destination port where to proxy the TLS traffic
        :type port_tls: int
        :param pool_id: capacity pool ID
        :type pool_id: int
        :return: GatewayProxy
        :rtype: GatewayProxy
        """
        p = GatewayProxy()
        p.info.node_id = gateway_id
        p.info.pool_id = pool_id
        p.info.workload_type = WorkloadType.Proxy
        p.domain = domain
        p.addr = addr
        p.port = port
        p.port_tls = port_tls
        return p

    def tcp_proxy_reverse(self, gateway_id: str, domain: str, secret: str, pool_id: int) -> GatewayReverseProxy:
        """
        create a reverse proxy workload object
        https://github.com/threefoldtech/tcprouter#reverse-tunneling

        :param gateway_id: the ID of the gateway where to configure the reverse proxy
        :type gateway_id: str
        :param domain: domain that will be proxied
        :type domain: str
        :param secret: secret to identity the incoming connection from TCP router client
        :type secret: str
        :param pool_id: capacity Pool ID
        :type pool_id: int
        :return: GatewayReverseProxy
        :rtype: GatewayReverseProxy
        """
        p = GatewayReverseProxy()
        p.info.node_id = gateway_id
        p.info.pool_id = pool_id
        p.info.workload_type = WorkloadType.Reverse_proxy
        p.domain = domain
        node = self._gateways.get(gateway_id)
        p.secret = encrypt_for_node(node.public_key_hex, secret).decode()
        return p

    def gateway_4to6(self, gateway_id: str, public_key: str, pool_id: int) -> Gateway4to6:
        """
        create a gateway4To6 workload object

        :param gateway_id: the ID of the gateway where to configure the gateway
        :type gateway_id: str
        :param public_key: wireguard public key to configure in the gateway
        :type public_key: str
        :param pool_id: capacity pool ID
        :type pool_id: int
        :return: Gateway4to6
        :rtype: Gateway4to6
        """
        gw = Gateway4to6()
        gw.public_key = public_key
        gw.info.node_id = gateway_id
        gw.info.pool_id = pool_id
        gw.info.workload_type = WorkloadType.Gateway4to6
        return gw


def _is_valid_ip(ip):
    try:
        netaddr.IPAddress(ip)
        return True
    except netaddr.AddrFormatError:
        return False
