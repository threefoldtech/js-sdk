import base64
import copy
import json
from jumpscale.loader import j
from jumpscale.core.base import StoredFactory
from jumpscale.sals.chatflows.chatflows import StopChatFlow
from jumpscale.clients.stellar.stellar import Network as StellarNetwork
from jumpscale.clients.explorer.models import NextAction, Type
from nacl.public import Box
import netaddr
import random
import requests
import time
from collections import defaultdict


class NetworkView:
    def __init__(self, name, workloads=None):
        self.name = name
        if not workloads:
            workloads = j.sals.zos.workloads.list(j.core.identity.me.tid, NextAction.DEPLOY)
        self.workloads = workloads
        self.used_ips = []
        self.network_workloads = []
        self._fill_used_ips(self.workloads)
        self._init_network_workloads(self.workloads)
        self.iprange = self.network_workloads[0].network_iprange

    def _init_network_workloads(self, workloads):
        for workload in workloads:
            if workload.info.next_action != NextAction.DEPLOY:
                continue
            if workload.info.workload_type == Type.Network_resource and workload.name == self.name:
                self.network_workloads.append(workload)

    def _fill_used_ips(self, workloads):
        for workload in workloads:
            if workload.info.next_action != NextAction.DEPLOY:
                continue
            if workload.info.workload_type == Type.Kubernetes:
                self.used_ips.append(workload.ipaddress)
            elif workload.info.workload_type == Type.Container:
                for conn in workload.network_connection:
                    if conn.network_id == self.name:
                        self.used_ips.append(conn.ipaddress)

    def add_node(self, node, pool_id):
        used_ip_ranges = set()
        for workload in self.network_workloads:
            if workload.info.node_id == node.node_id:
                return
            used_ip_ranges.add(workload.iprange)
            for peer in workload.peers:
                used_ip_ranges.add(peer.iprange)
        else:
            network_range = netaddr.IPNetwork(self.iprange)
            for idx, subnet in enumerate(network_range.subnet(24)):
                if str(subnet) not in used_ip_ranges:
                    break
            else:
                raise StopChatFlow("Failed to find free network")
            network = j.sals.zos.network.create(self.iprange, self.name)
            node_workloads = {}
            for net_workload in self.network_workloads:
                node_workloads[net_workload.info.node_id] = net_workload
            network.network_resources = list(node_workloads.values())  # add only latest network resource for each node
            j.sals.zos.network.add_node(network, node.node_id, str(subnet), self.pool_id)
            return network

    def get_node_range(self, node):
        for workload in self.network_workloads:
            if workload.info.node_id == node.node_id:
                return workload.iprange
        raise StopChatFlow(f"Node {node.node_id} is not part of network")

    def copy(self):
        return NetworkView(self.name)

    def get_node_free_ips(self, node):
        ip_range = self.get_node_range(node)
        freeips = []
        hosts = netaddr.IPNetwork(ip_range).iter_hosts()
        next(hosts)  # skip ip used by node
        for host in hosts:
            ip = str(host)
            if ip not in self.used_ips:
                freeips.append(ip)
        return freeips

    def get_free_ip(self, node):
        ip_range = self.get_node_range(node)
        hosts = netaddr.IPNetwork(ip_range).iter_hosts()
        next(hosts)  # skip ip used by node
        for host in hosts:
            ip = str(host)
            if ip not in self.used_ips:
                self.used_ips.append(ip)
                return ip
        return None


class ChatflowDeployer:
    def __init__(self):
        self.workloads = defaultdict(
            lambda: defaultdict(lambda: defaultdict(list))
        )  # Next Action: workload_type: pool_id: [workloads]

    def load_user_workloads(self, next_action=NextAction.DEPLOY):
        all_workloads = j.sals.zos.workloads.list(j.core.identity.me.tid, next_action)
        self.workloads.pop(next_action, None)
        for workload in all_workloads:
            if workload.info.metadata:
                workload.info.metadata = self.decrypt_metadata(workload.info.metadata)
            self.workloads[workload.info.next_action][workload.info.workload_type][workload.info.pool_id].append(
                workload
            )

    def decrypt_metadata(self, encrypted_metadata):
        try:
            pk = j.core.identity.me.nacl.signing_key.verify_key.to_curve25519_public_key()
            sk = j.core.identity.me.nacl.signing_key.to_curve25519_private_key()
            box = Box(sk, pk)
            return box.decrypt(base64.b85decode(encrypted_metadata.encode())).decode()
        except:
            return "{}"

    def list_networks(self, next_action=NextAction.DEPLOY, sync=True):
        if sync:
            self.load_user_workloads(next_action=next_action)
        networks = {}  # name: last child network resource
        for pool_id in self.workloads[next_action][Type.Network_resource]:
            for workload in self.workloads[next_action][Type.Network_resource][pool_id]:
                networks[workload.name] = workload
        all_workloads = []
        for pools_workloads in self.workloads[next_action].values():
            for pool_id, workload_list in pools_workloads.items():
                all_workloads += workload_list
        network_views = {}
        for network_name in networks:
            network_views[network_name] = NetworkView(network_name, all_workloads)
        return network_views


deployer = ChatflowDeployer()
