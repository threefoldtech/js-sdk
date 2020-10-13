from typing import List

import netaddr
import re
import string

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
    """ """

    def __init__(self, identity):
        self._identity = identity
        explorer = self._identity.explorer
        self._gateways = explorer.gateway

    def correct_domain(self, domain):
        """
      removes any invalid chars from a domain and return a valid one
      only for _ it replaces it with - and for other chars it is removed
      """
        domain = domain.replace("_", "-")
        domain_regex = r"^(?!:\/\/)([a-zA-Z0-9-]+\.)*[a-zA-Z0-9][a-zA-Z0-9-]+\.[a-zA-Z]{2,11}?$"
        if not re.match(domain_regex, domain):
            domain_copy = domain
            chars = string.ascii_letters + string.digits + "-."
            for c in domain_copy:
                if c not in chars:
                    domain = domain.replace(c, "")
        # maybe the user add - at the begining of the domain or at the end let's deal with it
        domain_list = domain.split("//")
        for idx, part in enumerate(domain_list):
            domain_list[idx] = part.strip("-")
        domain = "//".join(domain_list)
        domain_list = domain.split(".")
        for idx, part in enumerate(domain_list):
            domain_list[idx] = part.strip("-")
        domain = ".".join(domain_list)
        return domain

    def sub_domain(self, gateway_id: str, domain: str, ips: List[str], pool_id: int) -> GatewaySubdomain:
        """create a sub-domain workload object

        Args:
          gateway_id(str): the ID of the gateway where the create the sub-domain
          domain(str): sub-domain to create
          ips(List[str]): list of target IP pointed by the sub-domain
          pool_id(int): capacity pool ID

        Returns:
          Subdomain: Subdomain

        """
        for ip in ips:
            if not _is_valid_ip(ip):
                raise Input(f"{ip} is not valid IP address")
        domain = self.correct_domain(domain)
        sb = GatewaySubdomain()
        sb.info.node_id = gateway_id
        sb.domain = domain
        sb.ips = ips
        sb.info.workload_type = WorkloadType.Subdomain
        sb.info.pool_id = pool_id
        return sb

    def delegate_domain(self, gateway_id: str, domain: str, pool_id: int) -> GatewayDelegate:
        """create a domain delegation workload object

        Args:
          gateway_id(str): the ID of the gateway that will manage the delegated domain
          domain(str): domain to delegate
          pool_id(int): capacity pool ID

        Returns:
          GatewayDelegate: GatewayDelegate

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
        """create a proxy workload object

        Args:
          gateway_id(str): the ID of the gateway where to configure the proxy
          domain(str): domain that will be proxied to the addr:port
          addr(str): destination address where to proxy the traffic
          port(int): destination port where to proxy the normal traffic
          port_tls(int): destination port where to proxy the TLS traffic
          pool_id(int): capacity pool ID

        Returns:
          GatewayProxy: GatewayProxy

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
        """create a reverse proxy workload object
        https://github.com/threefoldtech/tcprouter#reverse-tunneling

        Args:
          gateway_id(str): the ID of the gateway where to configure the reverse proxy
          domain(str): domain that will be proxied
          secret(str): secret to identity the incoming connection from TCP router client
          pool_id(int): capacity Pool ID

        Returns:
          GatewayReverseProxy: GatewayReverseProxy

        """
        p = GatewayReverseProxy()
        p.info.node_id = gateway_id
        p.info.pool_id = pool_id
        p.info.workload_type = WorkloadType.Reverse_proxy
        p.domain = domain
        node = self._gateways.get(gateway_id)
        p.secret = encrypt_for_node(self._identity, node.public_key_hex, secret).decode()
        return p

    def gateway_4to6(self, gateway_id: str, public_key: str, pool_id: int) -> Gateway4to6:
        """create a gateway4To6 workload object

        Args:
          gateway_id(str): the ID of the gateway where to configure the gateway
          public_key(str): wireguard public key to configure in the gateway
          pool_id(int): capacity pool ID

        Returns:
          Gateway4to6: Gateway4to6

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
