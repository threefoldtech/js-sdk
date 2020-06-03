import base64
import copy
import json
from jumpscale.god import j
from jumpscale.core.base import Base, fields, StoredFactory

from jumpscale.sals.reservation_chatflow.models import (
    TfgridSolution1,
    TfgridSolutionsPayment1,
)
from jumpscale.core import identity

import netaddr
import random
import requests
import time


class Network:
    def __init__(self, network, expiration, bot, reservations, currency, resv_id):
        self._network = network
        self._expiration = expiration
        self.name = network.name
        self._used_ips = []
        self._is_dirty = False
        self._sal = j.sals.reservation_chatflow
        self._bot = bot
        self._fill_used_ips(reservations)
        self.currency = currency
        self.resv_id = resv_id

    def _fill_used_ips(self, reservations):
        for reservation in reservations:
            if reservation.next_action != "DEPLOY":
                continue
            for kubernetes in reservation.data_reservation.kubernetes:
                if kubernetes.network_id == self._network.name:
                    self._used_ips.append(kubernetes.ipaddress)
            for container in reservation.data_reservation.containers:
                for nc in container.network_connection:
                    if nc.network_id == self._network.name:
                        self._used_ips.append(nc.ipaddress)

    def add_node(self, node):
        network_resources = self._network.network_resources
        used_ip_ranges = set()
        for network_resource in network_resources:
            if network_resource.node_id == node.node_id:
                return
            used_ip_ranges.add(network_resource.iprange)
            for peer in network_resource.peers:
                used_ip_ranges.add(peer.iprange)
        else:
            network_range = netaddr.IPNetwork(self._network.iprange)
            for idx, subnet in enumerate(network_range.subnet(24)):
                if str(subnet) not in used_ip_ranges:
                    break
            else:
                self._bot.stop("Failed to find free network")
            j.sals.zos.network.add_node(self._network, node.node_id, str(subnet))
            self._is_dirty = True

    def get_node_range(self, node):
        for network_resource in self._network.network_resources:
            if network_resource.node_id == node.node_id:
                return network_resource.iprange
        self._bot.stop(f"Node {node.node_id} is not part of network")

    def update(self, tid, currency=None, bot=None):
        if self._is_dirty:
            reservation = j.sals.zos.reservation_create()
            reservation.data_reservation.networks.append(self._network._ddict)
            reservation_create = self._sal.reservation_register(
                reservation, self._expiration, tid, currency=currency, bot=bot
            )
            rid = reservation_create.reservation_id
            payment = j.sals.reservation_chatflow.payments_show(self._bot, reservation_create, currency)
            if payment["free"]:
                pass
            elif payment["wallet"]:
                j.sals.zos.billing.payout_farmers(payment["wallet"], reservation_create)
                j.sals.reservation_chatflow.payment_wait(bot, rid, threebot_app=False)
            else:
                j.sals.reservation_chatflow.payment_wait(
                    bot, rid, threebot_app=True, reservation_create_resp=reservation_create,
                )
            return self._sal.reservation_wait(self._bot, rid)
        return True

    def copy(self, customer_tid):
        explorer = j.clients.explorer.default
        reservation = explorer.reservations.get(self.resv_id)
        networks = self._sal.network_list(customer_tid, [reservation])
        for key in networks.keys():
            network, expiration, currency, resv_id = networks[key]
            if network.name == self.name:
                network_copy = Network(network, expiration, self._bot, [reservation], currency, resv_id)
                break
        if network_copy:
            network_copy._used_ips = copy.copy(self._used_ips)
        return network_copy

    def ask_ip_from_node(self, node, message):
        ip_range = self.get_node_range(node)
        freeips = []
        hosts = netaddr.IPNetwork(ip_range).iter_hosts()
        next(hosts)  # skip ip used by node
        for host in hosts:
            ip = str(host)
            if ip not in self._used_ips:
                freeips.append(ip)
        ip_address = self._bot.drop_down_choice(message, freeips, required=True)
        self._used_ips.append(ip_address)
        return ip_address

    def get_free_ip(self, node):
        ip_range = self.get_node_range(node)
        hosts = netaddr.IPNetwork(ip_range).iter_hosts()
        next(hosts)  # skip ip used by node
        for host in hosts:
            ip = str(host)
            if ip not in self._used_ips:
                return ip
        return None


class ReservationChatflow:
    def __init__(self, **kwargs):
        self.solutions = StoredFactory(TfgridSolution1)
        self._explorer = j.clients.explorer.get_default()
        self.solutions_explorer_get()
        self.me = identity.get_identity()

    #####################################################################
    ############## solutions explorer get ###############################
    def reservation_metadata_decrypt(self, metadata_encrypted):
        # TODO: REPLACE WHEN IDENTITY IS READY
        return self.me.encryptor.decrypt(base64.b85decode(metadata_encrypted.encode())).decode()

    def solution_type_check(self, reservation):
        containers = reservation.data_reservation.containers
        volumes = reservation.data_reservation.volumes
        zdbs = reservation.data_reservation.zdbs
        kubernetes = reservation.data_reservation.kubernetes
        networks = reservation.data_reservation.networks
        if containers == [] and volumes == [] and zdbs == [] and kubernetes == [] and networks:
            return "network"
        elif kubernetes != []:
            return "kubernetes"
        elif len(containers) != 0:
            if "ubuntu" in containers[0].flist:
                return "ubuntu"
            elif "minio" in containers[0].flist:
                return "minio"
            elif "gitea" in containers[0].flist:
                return "gitea"
            elif "tcprouter" in containers[0].flist:
                return "exposed"
            return "flist"
        elif reservation.data_reservation.domain_delegates:
            return "delegated_domain"
        return "unknown"

    def solution_ubuntu_info_get(self, metadata, reservation):
        envs = reservation.data_reservation.containers[0].environment
        env_variable = ""
        metadata["form_info"]["Public key"] = envs["pub_key"].strip(" ")
        envs.pop("pub_key")
        metadata["form_info"]["CPU"] = reservation.data_reservation.containers[0].capacity.cpu
        metadata["form_info"]["Memory"] = reservation.data_reservation.containers[0].capacity.memory
        metadata["form_info"]["Root filesystem Type"] = str(
            reservation.data_reservation.containers[0].capacity.disk_type
        )
        metadata["form_info"]["Root filesystem Size"] = (
            reservation.data_reservation.containers[0].capacity.disk_size or 256
        )
        for key, value in envs.items():
            env_variable += f"{key}={value},"
        metadata["form_info"]["Env variables"] = str(env_variable)
        metadata["form_info"]["IP Address"] = reservation.data_reservation.containers[0].network_connection[0].ipaddress
        return metadata

    def solution_exposed_info_get(self, reservation):
        def get_arg(cmd, arg):
            idx = cmd.index(arg)
            if idx:
                return cmd[idx + 1]
            return None

        info = {}
        for container in reservation.data_reservation.containers:
            if "tcprouter" in container.flist:
                entrypoint = container.entrypoint.split()
                local = get_arg(entrypoint, "-local")
                if local:
                    info["Port"] = local.split(":")[-1]
                localtls = get_arg(entrypoint, "-local-tls")
                if localtls:
                    info["port-tls"] = localtls.split(":")[-1]
                remote = get_arg(entrypoint, "-remote")
                if remote:
                    info["Name Server"] = remote.split(":")[0]
        for proxy in reservation.data_reservation.reverse_proxies:
            info["Domain"] = proxy.domain
        return info

    def solution_flist_info_get(self, metadata, reservation):
        envs = reservation.data_reservation.containers[0].environment
        env_variable = ""
        for key, value in envs.items():
            env_variable += f"{key}={value}, "
        metadata["form_info"]["CPU"] = reservation.data_reservation.containers[0].capacity.cpu
        metadata["form_info"]["Memory"] = reservation.data_reservation.containers[0].capacity.memory
        metadata["form_info"]["Root filesystem Type"] = str(
            reservation.data_reservation.containers[0].capacity.disk_type
        )
        metadata["form_info"]["Root filesystem Size"] = (
            reservation.data_reservation.containers[0].capacity.disk_size or 256
        )
        metadata["form_info"]["Env variables"] = str(env_variable)
        metadata["form_info"]["Flist link"] = reservation.data_reservation.containers[0].flist
        metadata["form_info"]["Interactive"] = reservation.data_reservation.containers[0].interactive
        if metadata["form_info"]["Interactive"]:
            metadata["form_info"]["Port"] = "7681"
        metadata["form_info"]["Entry point"] = reservation.data_reservation.containers[0].entrypoint
        metadata["form_info"]["IP Address"] = reservation.data_reservation.containers[0].network_connection[0].ipaddress
        return metadata

    def solution_domain_delegates_info_get(self, reservation):
        delegated_domain = reservation.data_reservation.domain_delegates[0]
        return {"Domain": delegated_domain.domain, "Gateway": delegated_domain.node_id}

    def reservation_save(self, rid, name, solution_type, form_info=None):
        form_info = form_info or []
        explorer_name = self._explorer.url.split(".")[1]
        reservation = self.solutions.get(f"{explorer_name}:{rid}")
        reservation.rid = rid
        reservation.name = name
        reservation.solution_type = solution_type
        reservation.form_info = form_info
        reservation.explorer = self._explorer.url
        reservation.save()

    def solutions_explorer_get(self):

        # delete old instances, to get the new ones from explorer
        for obj in self.solutions.list_all():
            self.solutions.delete(obj)

        customer_tid = self.me.tid
        reservations = self._explorer.reservations.list(customer_tid, "DEPLOY")
        networks = []
        dupnames = {}
        for reservation in sorted(reservations, key=lambda res: res.id, reverse=True):
            info = {}
            if reservation.metadata:
                try:
                    metadata = self.reservation_metadata_decrypt(reservation.metadata)
                    metadata = json.loads(metadata)
                except Exception:
                    continue

                if "form_info" not in metadata:
                    solution_type = self.solution_type_check(reservation)
                else:
                    solution_type = metadata["form_info"]["chatflow"]
                    metadata["form_info"].pop("chatflow")
                if solution_type == "unknown":
                    continue
                elif solution_type == "ubuntu":
                    metadata = self.solution_ubuntu_info_get(metadata, reservation)
                elif solution_type == "flist":
                    metadata = self.solution_flist_info_get(metadata, reservation)
                elif solution_type == "network":
                    if metadata["name"] in networks:
                        continue
                    networks.append(metadata["name"])
                elif solution_type == "gitea":
                    metadata["form_info"]["Public key"] = reservation.data_reservation.containers[0].environment[
                        "pub_key"
                    ]
                elif solution_type == "exposed":
                    meta = metadata
                    metadata = {"form_info": meta}
                    metadata["form_info"].update(self.solution_exposed_info_get(reservation))
                    metadata["name"] = metadata["form_info"]["Domain"]
                info = metadata["form_info"]
                name = metadata["name"]
            else:
                solution_type = self.solution_type_check(reservation)
                info = {}
                name = f"unknown_{reservation.id}"
                if solution_type == "unknown":
                    continue
                elif solution_type == "network":
                    name = reservation.data_reservation.networks[0].name
                    if name in networks:
                        continue
                    networks.append(name)
                elif solution_type == "delegated_domain":
                    info = self.solution_domain_delegates_info_get(reservation)
                    if not info.get("Solution name"):
                        name = f"unknown_{reservation.id}"
                    else:
                        name = info["Solution name"]
                elif solution_type == "exposed":
                    info = self.solution_exposed_info_get(reservation)
                    info["Solution name"] = name
                    name = info["Domain"]

            count = dupnames.setdefault(solution_type, {}).setdefault(name, 1)
            if count != 1:
                dupnames[solution_type][name] = count + 1
                name = f"{name}_{count}"
            self.reservation_save(reservation.id, name, solution_type, form_info=info)

    ######################################################################
