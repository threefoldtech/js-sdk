import base64
import copy
import datetime
import json
from jumpscale.god import j
from jumpscale.core.base import Base, fields, StoredFactory
from jumpscale.sals.chatflows.chatflows import StopChatFlow
from jumpscale.sals.reservation_chatflow.models import (
    TfgridSolution1,
    TfgridSolutionsPayment1,
)
from jumpscale.clients.explorer.models import TfgridDeployed_reservation1

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
        self.payments = StoredFactory(TfgridSolutionsPayment1)
        self.deployed_reservations = StoredFactory(TfgridDeployed_reservation1)
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

    ##############
    # payment and register
    def wallets_list(self):
        """
        List all stellar client wallets from bcdb. Based on explorer instance only either wallets with network type TEST or STD are returned
        rtype: list
        """
        if "devnet" in self._explorer.url or "testnet" in self._explorer.url:
            network_type = "TEST"
        else:
            network_type = "STD"

        wallets_list = j.clients.stellar.find(network=network_type)
        wallets = dict()
        for wallet in wallets_list:
            wallets[wallet.name] = wallet
        return wallets

    def escrow_qr_show(self, bot, reservation_create_resp, expiration_provisioning):
        """
        Show in chatflow the QR code with the details of the escrow information for payment
        """
        escrow_info = j.sals.zos.reservation_escrow_information_with_qrcodes(reservation_create_resp)
        escrow_address = escrow_info["escrow_address"]
        escrow_asset = escrow_info["escrow_asset"]
        reservationid = escrow_info["reservationid"]
        qrcode = escrow_info["qrcode"]
        remaning_time = j.data.time.get(expiration_provisioning).humanize()
        payment_details = self.get_payment_details(escrow_info, escrow_asset.split(":")[0])

        message_text = f"""
        <h3> Please make your payment </h3>
        Scan the QR code with your application (do not change the message) or enter the information below manually and proceed with the payment. Make sure to add the reservationid as memo_text.
        <p>If no payment is made {remaning_time} the reservation will be canceled</p>

        <h4> Wallet address: </h4>  {escrow_address} \n
        <h4> Currency: </h4>  {escrow_asset} \n
        <h4> Reservation id: </h4>  {reservationid} \n
        <h4> Payment details: </h4> {payment_details} \n
        """

        bot.qrcode_show(data=qrcode, msg=message_text, scale=4, update=True, html=True)

    def payment_create(
        self, rid, currency, escrow_address, escrow_asset, total_amount, payment_source, farmer_payments
    ):
        explorer_name = self._explorer.url.split(".")[1]
        payment_obj = self.payments.get(f"{explorer_name}:{rid}")
        payment_obj.explorer = self._explorer.url
        payment_obj.rid = rid
        payment_obj.currency = currency
        payment_obj.escrow_address = escrow_address
        payment_obj.escrow_asset = escrow_asset
        payment_obj.total_amount = total_amount
        payment_obj.transaction_fees = f"0.1 {currency}"
        payment_obj.payment_source = payment_source
        for farmer in farmer_payments:
            farmer_name = self._explorer.farms.get(farm_id=farmer["farmer_id"]).name
            payment_obj.farmer_payments[farmer_name] = farmer["total_amount"]
        return payment_obj

    def get_payment_details(self, escrow_info, currency):

        farmer_payments = escrow_info["farmer_payments"]
        total_amount = escrow_info["total_amount"]

        payment_details = ""
        payment_details += '<table style="width: 50%; font-family: arial, sans-serif; border-collapse: collapse;">'
        for farmer in farmer_payments:
            farmer_name = self._explorer.farms.get(farm_id=farmer["farmer_id"]).name
            payment_details += (
                f"<tr><td>Farmer {farmer_name}</td><td>{format(farmer['total_amount'],'.7f')} {currency}</td></tr>"
            )
        payment_details += f"<tr><td>Transaction Fees</td><td>{0.1} {currency}</td></tr>"
        payment_details += f"<tr><td>Total amount</td><td>{format(total_amount + 0.1,'.7f')} {currency}</td></tr>"
        payment_details += "</table>"

        return payment_details

    def payments_show(self, bot, reservation_create_resp, currency):
        """
        Show valid payment options in chatflow available. All available wallets possible are shown or usage of 3bot app is shown
        where a QR code is viewed for the user to scan and continue with their payment
        :rtype: wallet in case a wallet is used
        """

        payment = {"wallet": None, "free": False}
        if not (reservation_create_resp.escrow_information and reservation_create_resp.escrow_information.details):
            payment["free"] = True
            return payment, None
        escrow_info = j.sals.zos.reservation_escrow_information_with_qrcodes(reservation_create_resp)

        escrow_address = escrow_info["escrow_address"]
        escrow_asset = escrow_info["escrow_asset"]
        total_amount = escrow_info["total_amount"]
        rid = reservation_create_resp.reservation_id

        wallets = self.wallets_list()
        wallet_names = []
        for w in wallets.keys():
            wallet_names.append(w)
        wallet_names.append("3bot app")

        payment_details = self.get_payment_details(escrow_info, currency)

        message = f"""
        Billing details:
        <h4> Wallet address: </h4>  {escrow_address} \n
        <h4> Currency: </h4>  {escrow_asset} \n
        <h4> Payment details: </h4> {payment_details} \n
        <h4> Choose a wallet name to use for payment or proceed with payment through 3bot app </h4>
        """
        retry = False
        while True:

            result = bot.single_choice(message, wallet_names, html=True, retry=retry)

            if result not in wallet_names:
                retry = True
                continue
            if result == "3bot app":
                reservation = self._explorer.reservations.get(rid)
                self.escrow_qr_show(bot, reservation_create_resp, reservation.data_reservation.expiration_provisioning)
                payment_obj = self.payment_create(
                    rid=rid,
                    currency=currency,
                    escrow_address=escrow_address,
                    escrow_asset=escrow_asset,
                    total_amount=total_amount,
                    payment_source=result,
                    farmer_payments=escrow_info["farmer_payments"],
                )
                return payment, payment_obj
            else:
                payment["wallet"] = wallets[result]
                balances = payment["wallet"].get_balance().balances
                for balance in balances:
                    if balance.asset_code == currency:
                        current_balance = balance.balance
                        if float(current_balance) >= total_amount:
                            payment_obj = self.payment_create(
                                rid=rid,
                                currency=currency,
                                escrow_address=escrow_address,
                                escrow_asset=escrow_asset,
                                total_amount=total_amount,
                                payment_source=result,
                                farmer_payments=escrow_info["farmer_payments"],
                            )
                            return payment, payment_obj
                retry = True
                message = f"""
                <h2 style="color: #142850;"><b style="color: #00909e;">{total_amount} {currency}</b> are required, but only <b style="color: #00909e;">{current_balance} {currency}</b> are available in wallet <b style="color: #00909e;">{payment["wallet"].name}</b></h2>
                Billing details:
                <h4> Wallet address: </h4>  {escrow_address} \n
                <h4> Currency: </h4>  {escrow_asset} \n
                <h4> Payment details: </h4> {payment_details} \n
                <h4> Choose a wallet name to use for payment or proceed with payment through 3bot app </h4>
                """

    def payment_wait(self, bot, rid, threebot_app=False, reservation_create_resp=None):

        # wait to check payment is actually done next_action changed from:PAY
        def is_expired(reservation):
            return reservation.data_reservation.expiration_provisioning < j.data.time.get().timestamp

        reservation = self._explorer.reservations.get(rid)
        while True:
            remaning_time = j.data.time.get(reservation.data_reservation.expiration_provisioning).humanize()
            deploying_message = f"""
            # Payment being processed...\n
            Deployment will be cancelled if payment is not successful {remaning_time}
            """
            bot.md_show_update(j.core.text.strip(deploying_message), md=True)
            if reservation.next_action != "PAY":
                return
            if is_expired(reservation):
                res = f"# Failed to wait for payment for reservation:```{reservation.id}```:\n"
                for x in reservation.results:
                    if x.state == "ERROR":
                        res += f"\n### {x.category}: ```{x.message}```\n"
                link = f"{self._explorer.url}/reservations/{reservation.id}"
                res += f"<h2> <a href={link}>Full reservation info</a></h2>"
                j.sals.zos.reservation_cancel(rid)
                bot.stop(res, md=True, html=True)
            if threebot_app and reservation_create_resp:
                self.escrow_qr_show(bot, reservation_create_resp, reservation.data_reservation.expiration_provisioning)
            time.sleep(5)
            reservation = self._explorer.reservations.get(rid)

    def _reservation_failed(self, bot, reservation):
        failed = j.sals.zos.reservation_failed(reservation)
        if failed:
            res = f"# Sorry your reservation ```{reservation.id}``` has failed :\n"
            for x in reservation.results:
                if x.state == "ERROR":
                    res += f"\n### {x.category}: ```{x.message}```\n"
            link = f"{self._explorer.url}/reservations/{reservation.id}"
            res += f"<h2> <a href={link}>Full reservation info</a></h2>"
            j.sals.zos.reservation_cancel(reservation.id)
            bot.stop(res, md=True, html=True)

    def reservation_wait(self, bot, rid):
        def is_finished(reservation):
            count = 0
            count += len(reservation.data_reservation.volumes)
            count += len(reservation.data_reservation.zdbs)
            count += len(reservation.data_reservation.containers)
            count += len(reservation.data_reservation.kubernetes)
            count += len(reservation.data_reservation.proxies)
            count += len(reservation.data_reservation.reverse_proxies)
            count += len(reservation.data_reservation.subdomains)
            count += len(reservation.data_reservation.domain_delegates)
            count += len(reservation.data_reservation.gateway4to6)
            for network in reservation.data_reservation.networks:
                count += len(network.network_resources)
            return len(reservation.results) >= count

        def is_expired(reservation):
            return reservation.data_reservation.expiration_provisioning < j.data.time.get().timestamp

        reservation = self._explorer.reservations.get(rid)
        while True:
            remaning_time = j.data.time.get(reservation.data_reservation.expiration_provisioning).humanize()
            deploying_message = f"""
            # Deploying...\n
            Deployment will be cancelled if it is not successful {remaning_time}
            """
            bot.md_show_update(j.core.text.strip(deploying_message), md=True)
            self._reservation_failed(bot, reservation)
            if is_finished(reservation):
                return reservation.results
            if is_expired(reservation):
                res = f"# Sorry your reservation ```{reservation.id}``` failed to deploy in time:\n"
                for x in reservation.results:
                    if x.state == "ERROR":
                        res += f"\n### {x.category}: ```{x.message}```\n"
                link = f"{self._explorer.url}/reservations/{reservation.id}"
                res += f"<h2> <a href={link}>Full reservation info</a></h2>"
                j.sals.zos.reservation_cancel(rid)
                bot.stop(res, md=True, html=True)
            time.sleep(1)
            reservation = self._explorer.reservations.get(rid)

    def reservation_register(
        self, reservation, expiration, customer_tid, expiration_provisioning=1000, currency=None, bot=None
    ):
        """
        Register reservation

        :param reservation: Reservation object to register
        :type  reservation: object
        :param expiration: epoch time when the reservation should be canceled automaticly
        :type  expiration: int
        :param customer_tid: Id of the customer making the reservation
        :type  customer_tid: int
        :param expiration_provisioning: timeout on the deployment of the provisioning in seconds
        :type  expiration_provisioning: int

        :return: reservation_create object
        :rtype: Obj
        """
        expiration_provisioning += j.data.time.get().timestamp
        try:
            reservation_create = j.sals.zos.reservation_register(
                reservation,
                expiration,
                expiration_provisioning=expiration_provisioning,
                customer_tid=customer_tid,
                currencies=[currency],
            )
        except requests.HTTPError as e:
            try:
                msg = e.response.json()["error"]
            except (KeyError, json.JSONDecodeError):
                msg = e.response.text
            raise StopChatFlow(f"The following error occured: {msg}")

        rid = reservation_create.reservation_id
        reservation.id = rid

        # TODO: FIXME TO SET DEPLOYER in config
        if j.core.config.get_config().get("DEPLOYER") and customer_tid:
            # create a new object from deployed_reservation with the reservation and the tid
            explorer_name = self._explorer.url.split(".")[1]
            deployed_reservation = self.deployed_reservations.get(f"{explorer_name}:{rid}")
            deployed_reservation.reservation_id = rid
            deployed_reservation.customer_tid = customer_tid
            deployed_reservation.save()
        return reservation_create

    def reservation_register_and_pay(
        self, reservation, expiration=None, customer_tid=None, currency=None, bot=None, wallet=None
    ):
        payment_obj = None
        if customer_tid and expiration and currency:
            reservation_create = self.reservation_register(
                reservation, expiration, customer_tid=customer_tid, currency=currency, bot=bot
            )
        else:
            reservation_create = reservation
        if not wallet:
            payment, payment_obj = self.payments_show(bot, reservation_create, currency)
        else:
            payment = {"wallet": None, "free": False}
            if not (reservation_create.escrow_information and reservation_create.escrow_information.details):
                payment["free"] = True
            else:
                payment["wallet"] = wallet

        resv_id = reservation_create.reservation_id
        if payment["wallet"]:
            j.sals.zos.billing.payout_farmers(payment["wallet"], reservation_create)
            self.payment_wait(bot, resv_id, threebot_app=False)
        elif not payment["free"]:
            self.payment_wait(bot, resv_id, threebot_app=True, reservation_create_resp=reservation_create)

        self.reservation_wait(bot, resv_id)
        if payment_obj:
            payment_obj.save()
        return resv_id

    ##############

    # TODO: Reaming methods
    """
    validate_user
    _nodes_distribute
    nodes_filter
    farms_check
    farm_names_get
    nodes_get
    validate_node
    network_select
    farms_select
    ip_range_get
    network_create
    currency_get
    network_list
    solution_model_get
    reservation_metadata_add
    solution_name_add
    network_name_add
    solutions_get
    reservation_cancel_for_solution
    network_get
    delegate_domains_list
    gateway_list
    gateway_select
    gateway_get_kube_network_ip
    """
