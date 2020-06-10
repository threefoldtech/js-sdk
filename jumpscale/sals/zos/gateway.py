import netaddr
from jumpscale.core.exceptions import Input
from .id import _next_workload_id
from jumpscale.clients.explorer.models import (
    TfgridWorkloadsReservationGatewaySubdomain1,
    TfgridWorkloadsReservationGatewayDelegate1,
    TfgridWorkloadsReservationGatewayProxy1,
    TfgridWorkloadsReservationGatewayReverse_proxy1,
    TfgridWorkloadsReservationGateway4to61,
)
from .crypto import encrypt_for_node


class Gateway:
    def __init__(self, explorer):
        self._gateways = explorer.gateway

    def sub_domain(self, reservation, node_id, domain, ips):
        for ip in ips:
            if not _is_valid_ip(ip):
                raise Input(f"{ip} is not valid IP address")

        sb = TfgridWorkloadsReservationGatewaySubdomain1()
        sb.node_id = node_id
        sb.workload_id = _next_workload_id(reservation)
        sb.domain = domain
        sb.ips = ips
        reservation.data_reservation.subdomains.append(sb)
        return sb

    def delegate_domain(self, reservation, node_id, domain):
        d = TfgridWorkloadsReservationGatewayDelegate1()
        d.node_id = node_id
        d.workload_id = _next_workload_id(reservation)
        d.domain = domain
        reservation.data_reservation.domain_delegates.append(d)
        return d

    def tcp_proxy(self, reservation, node_id, domain, addr, port, port_tls=None):
        p = TfgridWorkloadsReservationGatewayProxy1()
        p.node_id = node_id
        p.workload_id = _next_workload_id(reservation)
        p.domain = domain
        p.addr = addr
        p.port = port
        p.port_tls = port_tls
        reservation.data_reservation.proxies.append(p)
        return p

    def tcp_proxy_reverse(self, reservation, node_id, domain, secret):
        p = TfgridWorkloadsReservationGatewayReverse_proxy1()
        p.node_id = node_id
        p.domain = domain
        p.workload_id = _next_workload_id(reservation)
        node = self._gateways.get(node_id)
        p.secret = encrypt_for_node(node.public_key_hex, secret).decode()
        reservation.data_reservation.reverse_proxies.append(p)
        return p

    def gateway_4to6(self, reservation, node_id, public_key):
        gw = TfgridWorkloadsReservationGateway4to61()
        gw.public_key = public_key
        gw.node_id = node_id
        gw.workload_id = _next_workload_id(reservation)
        reservation.data_reservation.gateway4to6.append(gw)
        return gw


def _is_valid_ip(ip):
    try:
        netaddr.IPAddress(ip)
        return True
    except netaddr.AddrFormatError:
        return False
