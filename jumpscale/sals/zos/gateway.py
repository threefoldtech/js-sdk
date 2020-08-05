import netaddr
from jumpscale.core.exceptions import Input
from .id import _next_workload_id
from jumpscale.clients.explorer.models import (
    GatewaySubdomain,
    GatewayDelegate,
    GatewayProxy,
    GatewayReverseProxy,
    Gateway4to6,
    WorkloadType,
)
from .crypto import encrypt_for_node


class GatewayGenerator:
    def __init__(self, explorer):
        self._gateways = explorer.gateway

    def sub_domain(self, node_id, domain, ips, pool_id):
        for ip in ips:
            if not _is_valid_ip(ip):
                raise Input(f"{ip} is not valid IP address")

        sb = GatewaySubdomain()
        sb.info.node_id = node_id
        sb.domain = domain
        sb.ips = ips
        sb.info.workload_type = WorkloadType.Subdomain
        sb.info.pool_id = pool_id
        return sb

    def delegate_domain(self, node_id, domain, pool_id):
        d = GatewayDelegate()
        d.info.node_id = node_id
        d.domain = domain
        d.info.workload_type = WorkloadType.Domain_delegate
        d.info.pool_id = pool_id
        return d

    def tcp_proxy(self, node_id, domain, addr, port, port_tls, pool_id):
        p = GatewayProxy()
        p.info.node_id = node_id
        p.info.pool_id = pool_id
        p.info.workload_type = WorkloadType.Proxy
        p.domain = domain
        p.addr = addr
        p.port = port
        p.port_tls = port_tls
        return p

    def tcp_proxy_reverse(self, node_id, domain, secret, pool_id):
        p = GatewayReverseProxy()
        p.info.node_id = node_id
        p.info.pool_id = pool_id
        p.info.workload_type = WorkloadType.Reverse_proxy
        p.domain = domain
        node = self._gateways.get(node_id)
        p.secret = encrypt_for_node(node.public_key_hex, secret).decode()
        return p

    def gateway_4to6(self, node_id, public_key, pool_id):
        gw = Gateway4to6()
        gw.public_key = public_key
        gw.info.node_id = node_id
        gw.info.pool_id = pool_id
        gw.info.workload_type = WorkloadType.Gateway4to6
        return gw


def _is_valid_ip(ip):
    try:
        netaddr.IPAddress(ip)
        return True
    except netaddr.AddrFormatError:
        return False
