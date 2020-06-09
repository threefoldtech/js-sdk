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
    SolutionType,
)
from jumpscale.clients.explorer.models import TfgridDeployed_reservation1, Next_action
from jumpscale.clients.stellar.stellar import Network as StellarNetwork
from jumpscale.core import identity

import netaddr
import random
import requests
import time
import base64
from nacl.public import Box


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
            if reservation.next_action != Next_action.DEPLOY:
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
            reservation.data_reservation.networks.append(self._network)
            reservation_create = self._sal.register_reservation(
                reservation, self._expiration, tid, currency=currency, bot=bot
            )
            rid = reservation_create.reservation_id
            payment, _ = j.sals.reservation_chatflow.show_payments(self._bot, reservation_create, currency)
            if payment["free"]:
                pass
            elif payment["wallet"]:
                j.sals.zos.billing.payout_farmers(payment["wallet"], reservation_create)
                j.sals.reservation_chatflow.wait_payment(bot, rid, threebot_app=False)
            else:
                j.sals.reservation_chatflow.wait_payment(
                    bot, rid, threebot_app=True, reservation_create_resp=reservation_create,
                )
            return self._sal.wait_reservation(self._bot, rid)
        return True

    def copy(self, customer_tid):
        explorer = j.clients.explorer.default
        reservation = explorer.reservations.get(self.resv_id)
        networks = self._sal.list_networks(customer_tid, [reservation])
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
        self.me = j.core.identity
        self.solutions = StoredFactory(TfgridSolution1)
        self.payments = StoredFactory(TfgridSolutionsPayment1)
        self.deployed_reservations = StoredFactory(TfgridDeployed_reservation1)
        self._explorer = j.clients.explorer.get_default()
        self.get_solutions_explorer()

    def decrypt_reservation_metadata(self, metadata_encrypted):
        pk = j.core.identity.nacl.signing_key.verify_key.to_curve25519_public_key()
        sk = j.core.identity.nacl.signing_key.to_curve25519_private_key()
        box = Box(sk, pk)
        return box.decrypt(base64.b85decode(metadata_encrypted.encode())).decode()

    def check_solution_type(self, reservation):
        containers = reservation.data_reservation.containers
        volumes = reservation.data_reservation.volumes
        zdbs = reservation.data_reservation.zdbs
        kubernetes = reservation.data_reservation.kubernetes
        networks = reservation.data_reservation.networks
        if containers == [] and volumes == [] and zdbs == [] and kubernetes == [] and networks:
            return SolutionType.Network
        elif kubernetes != []:
            return SolutionType.Kubernetes
        elif len(containers) != 0:
            if "ubuntu" in containers[0].flist:
                return SolutionType.Ubuntu
            elif "minio" in containers[0].flist:
                return SolutionType.Minio
            elif "gitea" in containers[0].flist:
                return SolutionType.Gitea
            elif "tcprouter" in containers[0].flist:
                return SolutionType.Exposed
            return "flist"
        elif reservation.data_reservation.domain_delegates:
            return SolutionType.DelegatedDomain
        return SolutionType.Unkown

    def get_solution_ubuntu_info(self, metadata, reservation):
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

    def get_solution_exposed_info(self, reservation):
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

    def get_solution_flist_info(self, metadata, reservation):
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

    def get_solution_domain_delegates_info(self, reservation):
        delegated_domain = reservation.data_reservation.domain_delegates[0]
        return {"Domain": delegated_domain.domain, "Gateway": delegated_domain.node_id}

    def save_reservation(self, rid, name, solution_type, form_info=None):
        form_info = form_info or {}
        explorer_name = self._explorer.url.split(".")[1]
        reservation = self.solutions.get(f"{explorer_name}_{rid}")
        reservation.rid = rid
        reservation.name = name
        reservation.solution_type = solution_type
        reservation.form_info = form_info
        reservation.explorer = self._explorer.url
        reservation.save()

    def get_solutions_explorer(self):
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
                    metadata = self.decrypt_reservation_metadata(reservation.metadata)
                    metadata = json.loads(metadata)
                except Exception:
                    continue

                if "form_info" not in metadata:
                    solution_type = self.check_solution_type(reservation)
                else:
                    solution_type = metadata["form_info"]["chatflow"]
                    metadata["form_info"].pop("chatflow")
                if solution_type == SolutionType.Unknown:
                    continue
                elif solution_type == SolutionType.Ubuntu:
                    metadata = self.get_solution_ubuntu_info(metadata, reservation)
                elif solution_type == SolutionType.Flist:
                    metadata = self.get_solution_flist_info(metadata, reservation)
                elif solution_type == SolutionType.Network:
                    if metadata["name"] in networks:
                        continue
                    networks.append(metadata["name"])
                elif solution_type == SolutionType.Gitea:
                    metadata["form_info"]["Public key"] = reservation.data_reservation.containers[0].environment[
                        "pub_key"
                    ]
                elif solution_type == SolutionType.Exposed:
                    meta = metadata
                    metadata = {"form_info": meta}
                    metadata["form_info"].update(self.get_solution_exposed_info(reservation))
                    metadata["name"] = metadata["form_info"]["Domain"]
                info = metadata["form_info"]
                name = metadata["name"]
            else:
                solution_type = self.check_solution_type(reservation)
                info = {}
                name = f"unknown_{reservation.id}"
                if solution_type == SolutionType.Unknown:
                    continue
                elif solution_type == SolutionType.Network:
                    name = reservation.data_reservation.networks[0].name
                    if name in networks:
                        continue
                    networks.append(name)
                elif solution_type == SolutionType.DelegatedDomain:
                    info = self.get_solution_domain_delegates_info(reservation)
                    if not info.get("Solution name"):
                        name = f"unknown_{reservation.id}"
                    else:
                        name = info["Solution name"]
                elif solution_type == SolutionType.Exposed:
                    info = self.get_solution_exposed_info(reservation)
                    info["Solution name"] = name
                    name = info["Domain"]

            count = dupnames.setdefault(solution_type, {}).setdefault(name, 1)
            if count != 1:
                dupnames[solution_type][name] = count + 1
                name = f"{name}_{count}"
            self.save_reservation(reservation.id, name, solution_type, form_info=info)

    def list_wallets(self):
        """
        List all stellar client wallets from bcdb. Based on explorer instance only either wallets with network type TEST or STD are returned
        rtype: list
        """
        if "devnet" in self._explorer.url or "testnet" in self._explorer.url:
            network_type = StellarNetwork.TEST
        else:
            network_type = StellarNetwork.STD

        wallets_list = j.clients.stellar.list_all()
        wallets = dict()
        for wallet_name in wallets_list:
            wallet = j.clients.stellar.find(wallet_name)
            if wallet.network != network_type:
                continue
            wallets[wallet_name] = wallet
        return wallets

    def show_escrow_qr(self, bot, reservation_create_resp, expiration_provisioning):
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

    def create_payment(
        self, rid, currency, escrow_address, escrow_asset, total_amount, payment_source, farmer_payments
    ):
        explorer_name = self._explorer.url.split(".")[1]
        payment_obj = self.payments.get(f"{explorer_name}_{rid}")
        payment_obj.explorer = self._explorer.url
        payment_obj.rid = rid
        payment_obj.currency = currency
        payment_obj.escrow_address = escrow_address
        payment_obj.escrow_asset = escrow_asset
        payment_obj.total_amount = str(total_amount)
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

    def show_payments(self, bot, reservation_create_resp, currency):
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

        wallets = self.list_wallets()
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
                self.show_escrow_qr(bot, reservation_create_resp, reservation.data_reservation.expiration_provisioning)
                payment_obj = self.create_payment(
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
                            payment_obj = self.create_payment(
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

    def wait_payment(self, bot, rid, threebot_app=False, reservation_create_resp=None):

        # wait to check payment is actually done next_action changed from:PAY
        def is_expired(reservation):
            return reservation.data_reservation.expiration_provisioning.timestamp() < j.data.time.get().timestamp

        reservation = self._explorer.reservations.get(rid)
        while True:
            remaning_time = j.data.time.get(reservation.data_reservation.expiration_provisioning).humanize()
            deploying_message = f"""
# Payment being processed...\n
Deployment will be cancelled if payment is not successful {remaning_time}
"""
            bot.md_show_update(deploying_message, md=True)
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
                self.show_escrow_qr(bot, reservation_create_resp, reservation.data_reservation.expiration_provisioning)
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

    def wait_reservation(self, bot, rid):
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
            return reservation.data_reservation.expiration_provisioning.timestamp() < j.data.time.get().timestamp

        reservation = self._explorer.reservations.get(rid)
        while True:
            remaning_time = j.data.time.get(reservation.data_reservation.expiration_provisioning).humanize()
            deploying_message = f"""
# Deploying...\n
Deployment will be cancelled if it is not successful {remaning_time}
"""
            bot.md_show_update(deploying_message, md=True)
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

    def register_reservation(
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
            deployed_reservation = self.deployed_reservations.get(f"{explorer_name}_{rid}")
            deployed_reservation.reservation_id = rid
            deployed_reservation.customer_tid = customer_tid
            deployed_reservation.save()
        return reservation_create

    def register_and_pay_reservation(
        self, reservation, expiration=None, customer_tid=None, currency=None, bot=None, wallet=None
    ):
        payment_obj = None
        if customer_tid and expiration and currency:
            reservation_create = self.register_reservation(
                reservation, expiration, customer_tid=customer_tid, currency=currency, bot=bot
            )
        else:
            reservation_create = reservation
        if not wallet:
            payment, payment_obj = self.show_payments(bot, reservation_create, currency)
        else:
            payment = {"wallet": None, "free": False}
            if not (reservation_create.escrow_information and reservation_create.escrow_information.details):
                payment["free"] = True
            else:
                payment["wallet"] = wallet

        resv_id = reservation_create.reservation_id
        if payment["wallet"]:
            j.sals.zos.billing.payout_farmers(payment["wallet"], reservation_create)
            self.wait_payment(bot, resv_id, threebot_app=False)
        elif not payment["free"]:
            self.wait_payment(bot, resv_id, threebot_app=True, reservation_create_resp=reservation_create)

        self.wait_reservation(bot, resv_id)
        if payment_obj:
            payment_obj.save()
        return resv_id

    def get_kube_network_ip(self, reservation_data):
        network_id = reservation_data["kubernetes"][0]["network_id"]
        ip = reservation_data["kubernetes"][0]["ipaddress"]
        return network_id, ip

    def list_gateways(self, bot, currency=None):
        unknowns = ["", None, "Uknown", "Unknown"]
        gateways = {}
        for g in j.sals.zos._explorer.gateway.list():
            if not j.sals.zos.nodes_finder.filter_is_up(g):
                continue
            location = []
            for area in ["continent", "country", "city"]:
                areaname = getattr(g.location, area)
                if areaname not in unknowns:
                    location.append(areaname)
            if g.free_to_use:
                reservation_currency = "FreeTFT"
            else:
                reservation_currency = "TFT"
            if currency and currency != reservation_currency:
                continue
            gtext = f"{' - '.join(location)} ({reservation_currency}) ID: {g.node_id}"
            gateways[gtext] = g
        return gateways

    def select_gateway(self, bot, currency=None):
        gateways = self.list_gateways(bot, currency)
        if not gateways:
            bot.stop("No available gateways")
        options = sorted(list(gateways.keys()))
        gateway = bot.drop_down_choice("Please choose a gateway", options, required=True)
        return gateways[gateway]

    def list_delegate_domains(self, customer_tid, currency=None):
        reservations = j.sals.zos.reservation_list(tid=customer_tid, next_action="DEPLOY")
        domains = dict()
        names = set()
        for reservation in sorted(reservations, key=lambda r: r.id, reverse=True):
            reservation_currency = self.get_currency(reservation)
            if reservation.next_action != Next_action.DEPLOY:
                continue
            rdomains = reservation.data_reservation.domain_delegates
            if currency and currency != reservation_currency:
                continue
            for dom in rdomains:
                if dom.domain in names:
                    continue
                names.add(dom.domain)
                domains[dom.domain] = dom
        return domains

    def get_network(self, bot, customer_tid, name):
        reservations = j.sals.zos.reservation_list(tid=customer_tid, next_action="DEPLOY")
        networks = self.list_networks(customer_tid, reservations)
        for key in networks.keys():
            network, expiration, currency, resv_id = networks[key]
            if network.name == name:
                return Network(network, expiration, bot, reservations, currency, resv_id)

    def list_networks(self, tid, reservations=None):
        if not reservations:
            reservations = j.sals.zos.reservation_list(tid=tid, next_action="DEPLOY")
        networks = dict()
        names = set()
        for reservation in sorted(reservations, key=lambda r: r.id, reverse=True):
            if reservation.next_action != Next_action.DEPLOY:
                continue
            rnetworks = reservation.data_reservation.networks
            expiration = reservation.data_reservation.expiration_reservation
            currency = self.get_currency(reservation)
            for network in rnetworks:
                if network.name in names:
                    continue
                names.add(network.name)
                remaining = j.data.time.get(expiration).humanize()

                network_name = network.name + f" ({currency}) - ends " + remaining
                networks[network_name] = (network, expiration, currency, reservation.id)

        return networks

    def get_currency(self, reservation):
        currencies = reservation.data_reservation.currencies
        if currencies:
            return currencies[0]
        elif reservation.data_reservation.networks and reservation.data_reservation.networks[0].network_resources:
            node_id = reservation.data_reservation.networks[0].network_resources[0].node_id
            if self._explorer.nodes.get(node_id).free_to_use:
                return "FreeTFT"

        return "TFT"

    def cancel_solution_reservation(self, solution_type, solution_name):
        for name in self.solutions.list_all():
            solution = self.solutions.get(name)
            if solution.name == solution_name and solution.solution_type == solution_type:
                j.sals.zos.reservation_cancel(str(solution.rid))
                self.solutions.delete(name)

    def get_solutions(self, solution_type):
        reservations = []
        for name in self.solutions.list_all():
            solution = self.solutions.get(name)
            if solution.solution_type != solution_type:
                continue
            if solution.explorer and solution.explorer != self._explorer.url:
                continue
            reservation = self._explorer.reservations.get(solution.rid)
            reservations.append(
                {
                    "name": solution.name,
                    "reservation": reservation._get_data,
                    "type": solution_type,
                    "form_info": json.dumps(solution.form_info),
                }
            )
        return reservations

    def add_reservation_metadata(self, reservation, metadata):
        meta_json = json.dumps(metadata)

        pk = j.core.identity.nacl.signing_key.verify_key.to_curve25519_public_key()
        sk = j.core.identity.nacl.signing_key.to_curve25519_private_key()
        box = Box(sk, pk)
        encrypted_metadata = base64.b85encode(box.encrypt(meta_json.encode())).decode()
        reservation.metadata = encrypted_metadata
        return reservation

    def get_solution_metadata(self, solution_name, solution_type, form_info=None):
        form_info = form_info or {}
        reservation = {}
        reservation["name"] = solution_name
        reservation["form_info"] = form_info
        reservation["solution_type"] = solution_type.value
        reservation["explorer"] = self._explorer.url
        return reservation

    def create_network(
        self, network_name, reservation, ip_range, customer_tid, ip_version, expiration=None, currency=None, bot=None
    ):
        """
        bot: Gedis chatbot object from chatflow
        reservation: reservation object from schema
        ip_range: ip range for network eg: "10.70.0.0/16"
        node: list of node objects from explorer

        return reservation (Object) , config of network (dict)
        """
        network = j.sals.zos.network.create(reservation, ip_range, network_name)
        node_subnets = netaddr.IPNetwork(ip_range).subnet(24)
        network_config = dict()
        access_nodes = j.sals.zos.nodes_finder.nodes_by_capacity(currency=currency)
        use_ipv4 = ip_version == "IPv4"

        if use_ipv4:
            nodefilter = j.sals.zos.nodes_finder.filter_public_ip4
        else:
            nodefilter = j.sals.zos.nodes_finder.filter_public_ip6

        for node in filter(j.sals.zos.nodes_finder.filter_is_up, filter(nodefilter, access_nodes)):
            access_node = node
            break
        else:
            raise StopChatFlow("Could not find available access node")

        j.sals.zos.network.add_node(network, access_node.node_id, str(next(node_subnets)))
        wg_quick = j.sals.zos.network.add_access(network, access_node.node_id, str(next(node_subnets)), ipv4=use_ipv4)

        network_config["wg"] = wg_quick

        j.sals.fs.mkdir(f"{j.core.dirs.CFGDIR}/wireguard/")
        j.sals.fs.write_file(f"{j.core.dirs.CFGDIR}/wireguard/{network_name}.conf", f"{wg_quick}")

        # register the reservation
        expiration = expiration or j.data.time.get().timestamp + (60 * 60 * 24)
        reservation_create = self.register_reservation(
            reservation, expiration, customer_tid, currency=currency, bot=bot
        )

        network_config["rid"] = reservation_create.reservation_id
        network_config["reservation_create"] = reservation_create

        return network_config

    def get_ip_range(self, bot):
        """
        bot: Gedis chatbot object from chatflow
        return ip_range from user or generated one
        """
        ip_range_choose = ["Configure IP range myself", "Choose IP range for me"]
        iprange_user_choice = bot.single_choice(
            "To have access to the threebot, the network must be configured", ip_range_choose
        )
        if iprange_user_choice == "Configure IP range myself":
            ip_range = bot.string_ask("Please add private IP Range of the network")
        else:
            first_digit = random.choice([172, 10])
            if first_digit == 10:
                second_digit = random.randint(0, 255)
            else:
                second_digit = random.randint(16, 31)
            ip_range = str(first_digit) + "." + str(second_digit) + ".0.0/16"
        return ip_range

    def select_farms(self, bot, message=None, currency=None, retry=False):
        message = message or "Select 1 or more farms to distribute nodes on"
        farms = self._explorer.farms.list()
        farm_names = []
        for f in farms:
            if j.sals.zos.nodes_finder.filter_farm_currency(f, currency):
                farm_names.append(f.name)
        farms_selected = bot.multi_list_choice(message, farm_names, retry=retry, auto_complete=True)
        return farms_selected

    def select_network(self, bot, customer_tid):
        reservations = j.sals.zos.reservation_list(tid=customer_tid, next_action="DEPLOY")
        networks = self.list_networks(customer_tid, reservations)
        names = []
        for n in networks.keys():
            names.append(n)
        if not names:
            res = "You don't have any networks, please use the network chatflow to create one"
            res = j.tools.jinja2.template_render(text=res)
            bot.stop(res)
        while True:
            result = bot.single_choice("Choose a network", names, required=True)
            if result not in networks:
                continue
            network, expiration, currency, resv_id = networks[result]
            return Network(network, expiration, bot, reservations, currency, resv_id)

    def validate_node(self, nodeid, query=None, currency=None):
        try:
            node = self._explorer.nodes.get(nodeid)
        except requests.exceptions.HTTPError:
            raise j.exceptions.NotFound(f"Node {nodeid} doesn't exists please enter a valid nodeid")
        if not j.sals.zos.nodes_finder.filter_is_up(node):
            raise j.exceptions.NotFound(f"Node {nodeid} doesn't seem to be up please choose another nodeid")

        if currency:
            if currency == "FreeTFT" and not node.free_to_use:
                raise j.exceptions.Value(
                    f"The specified node ({nodeid}) should support the same type of currency as the network you are using ({currency})"
                )
        if query:
            for unit, value in query.items():
                if unit == "currency":
                    continue
                freevalue = getattr(node.total_resources, unit) - getattr(node.used_resources, unit)
                if freevalue < value:
                    raise j.exceptions.Value(
                        f"Node {nodeid} does not have enough available {unit} resources for this request {value} required {freevalue} available, please choose another one"
                    )
        return node

    def get_nodes(
        self, number_of_nodes, farm_id=None, farm_names=None, cru=None, sru=None, mru=None, hru=None, currency="TFT"
    ):
        nodes_distribution = self._distribute_nodes(number_of_nodes, farm_names)
        # to avoid using the same node with different networks
        nodes_selected = []
        for farm_name in nodes_distribution:
            nodes_number = nodes_distribution[farm_name]
            if not farm_names:
                farm_name = None
            nodes = j.sals.zos.nodes_finder.nodes_by_capacity(
                farm_name=farm_name, cru=cru, sru=sru, mru=mru, hru=hru, currency=currency
            )
            nodes = self.filter_nodes(nodes, currency == "FreeTFT")
            for i in range(nodes_number):
                try:
                    node = random.choice(nodes)
                    while node in nodes_selected:
                        node = random.choice(nodes)
                except IndexError:
                    raise StopChatFlow("Failed to find resources for this reservation")
                nodes.remove(node)
                nodes_selected.append(node)
        return nodes_selected

    def filter_nodes(self, nodes, free_to_use):
        nodes = filter(j.sals.zos.nodes_finder.filter_is_up, nodes)
        nodes = list(nodes)
        if free_to_use:
            nodes = list(nodes)
            nodes = filter(j.sals.zos.nodes_finder.filter_is_free_to_use, nodes)
        elif not free_to_use:
            nodes = list(nodes)
        return list(nodes)

    def _distribute_nodes(self, number_of_nodes, farm_names):
        nodes_distribution = {}
        nodes_left = number_of_nodes
        names = list(farm_names) if farm_names else []
        if not farm_names:
            farms = self._explorer.farms.list()
            names = []
            for f in farms:
                names.append(f.name)
        random.shuffle(names)
        names_pointer = 0
        while nodes_left:
            farm_name = names[names_pointer]
            if farm_name not in nodes_distribution:
                nodes_distribution[farm_name] = 0
            nodes_distribution[farm_name] += 1
            nodes_left -= 1
            names_pointer += 1
            if names_pointer == len(names):
                names_pointer = 0
        return nodes_distribution

    def get_farm_names(self, number_of_nodes, bot, cru=None, sru=None, mru=None, hru=None, currency="TFT", message=""):
        farms_message = f"Select 1 or more farms to distribute the {message} nodes on. If no selectiosn is made, the farms will be chosen randomly"
        empty_farms = set()
        all_farms = self._explorer.farms.list()
        retry = False
        while True:
            farms = self.select_farms(bot, farms_message, currency=currency, retry=retry)
            farms_with_no_resources = self.check_farms(
                1, farm_names=farms, cru=cru, sru=sru, mru=mru, hru=hru, currency=currency
            )
            if not farms_with_no_resources:
                return farms
            for farm_name in farms_with_no_resources:
                empty_farms.add(farm_name)
            if len(all_farms) == len(empty_farms):
                raise StopChatFlow("No Farms available containing nodes that match the required resources")
            if message:
                message = f"for {message}"
            retry = True
            resources_of_farm = ""
            if cru:
                resources_of_farm += f" cru={cru}/"
            if sru:
                resources_of_farm += f" sru={sru}/"
            if mru:
                resources_of_farm += f" mru={mru}/"
            if hru:
                resources_of_farm += f" hru={hru}/"
            if currency:
                resources_of_farm += f" and the currency={currency}"
            farms_message = (
                f"""The following farms don't meet the criteria of having {resources_of_farm} {message}: """
                + ", ".join(farms_with_no_resources)
                + """.
                Please reselect farms to check for resources or leave it empty
                """
            )

    def check_farms(
        self, number_of_nodes, farm_id=None, farm_names=None, cru=None, sru=None, mru=None, hru=None, currency="TFT"
    ):
        if not farm_names:
            return []
        farms_with_no_resources = []
        nodes_distribution = self._distribute_nodes(number_of_nodes, farm_names)
        for farm_name in nodes_distribution:
            nodes_number = nodes_distribution[farm_name]
            nodes = j.sals.zos.nodes_finder.nodes_by_capacity(
                farm_name=farm_name, cru=cru, sru=sru, mru=mru, hru=hru, currency=currency
            )
            nodes = self.filter_nodes(nodes, currency == "FreeTFT")
            if nodes_number > len(nodes):
                farms_with_no_resources.append(farm_name)
        return list(farms_with_no_resources)

    def validate_user(self, user_info):
        # TODO: email field of testnet users is empty. is this really used?
        if not j.core.config.get_config().get("threebot", {}).get("threebot_connect"):
            error_msg = """
            This chatflow is not supported when Threebot is in dev mode.
            To enable Threebot connect : `j.me.encryptor.tools.threebotconnect_enable()`
            """
            raise j.exceptions.Runtime(error_msg)
        if not user_info["email"]:
            raise j.exceptions.Value("Email shouldn't be empty")
        if not user_info["username"]:
            raise j.exceptions.Value("Name of logged in user shouldn't be empty")
        return self._explorer.users.get(name=user_info["username"], email=user_info["email"])

    ##############

    # TODO: Remaining methods
    """
    solution_name_add   # not needed anymore as factory instance_name is unique
    network_name_add  # not needed anymore as factory instance_name is unique
    """
    # TODO: Missing configuration sections (DEPLOYER)

    # Verified
    """
    list_networks   (unsaved factory instance raises error. it is fixed on development https://github.com/js-next/js-ng/issues/268)
    get_nodes
    list_wallets
    validate_user   (email field of testnet users is empty. is it really used?)
    check_farms
    _distribute_nodes
    filter_nodes
    validate_node
    list_delegate_domains
    check_solution_type
    decrypt_reservation_metadata
    get_solution_domain_delegates_info
    get_solutions_explorer
    get_solutions
    save_reservation
    get_solution_ubuntu_info
    get_solution_exposed_info
    get_solution_flist_info
    ###################
    get_kube_network_ip
    get_currency
    create_payment
    get_payment_details
    add_reservation_metadata
    get_solution_model
    cancel_solution_reservation
    """

    # TODO: Verify
    """
    register_and_pay_reservation    (needs bot)
    register_reservation    (needs bot)
    get_ip_range    (needs bot)
    create_network  (needs bot)
    show_escrow_qr  (needs bot)
    get_network     (needs bot)
    show_payments   (needs bot)
    wait_payment    (needs bot)
    _reservation_failed     (needs bot)
    wait_reservation    (needs bot)
    list_gateways   (needs bot)
    select_gateway  (needs bot)
    select_farms    (needs bot)
    select_network   (needs bot)
    get_farm_names   (needs bot)
    """
