import base64
import copy
import json
import random
import time
from textwrap import dedent

import netaddr
import requests
from jumpscale.clients.explorer.models import DeployedReservation, NextAction
from jumpscale.clients.stellar import TRANSACTION_FEES
from jumpscale.clients.stellar.stellar import Network as StellarNetwork
from jumpscale.core.base import StoredFactory
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import StopChatFlow
from jumpscale.sals.reservation_chatflow.models import SolutionType, TfgridSolution1, TfgridSolutionsPayment1
from nacl.public import Box

NODES_DISALLOW_PREFIX = "ZOS:NODES:DISALLOWED"
NODES_DISALLOW_EXPIRATION = 60 * 60 * 4  # 4 hours
NODES_COUNT_KEY = "ZOS:NODES:FAILURE_COUNT"


class Network:
    def __init__(self, network, expiration, bot, reservations, currency, resv_id):
        """Network class is responsible for creation and management of networks
            you can add, update, list, get, filter nodes
        Args:
            network (jumpscale.clients.explorer.models.TfgridWorkloadsReservationNetwork1): network object
            expiration (datetime): timestamp of the date for network expiration
            bot (GedisChatBot):Instance from the bot that uses network
            reservations (list of TfgridWorkloadsReservationData1): list of reservations
            currency (str): currency used "TFT", "FreeTFT"
            resv_id (int): reservation ID
        """
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
        self.solutions = StoredFactory(TfgridSolution1)

    def _fill_used_ips(self, reservations):
        for reservation in reservations:
            if reservation.next_action != NextAction.DEPLOY:
                continue
            for kubernetes in reservation.data_reservation.kubernetes:
                if kubernetes.network_id == self._network.name:
                    self._used_ips.append(kubernetes.ipaddress)
            for container in reservation.data_reservation.containers:
                for nc in container.network_connection:
                    if nc.network_id == self._network.name:
                        self._used_ips.append(nc.ipaddress)

    def add_node(self, node):
        """add node to the network

        Args:
            node (jumpscale.clients.explorer.models.TfgridDirectoryNode2): node object
        """
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
            subnet = None
            for _, subnet in enumerate(network_range.subnet(24)):
                if str(subnet) not in used_ip_ranges:
                    break
            else:
                self._bot.stop("Failed to find free network")
            j.sals.zos.get().network.add_node(self._network, node.node_id, str(subnet))
            self._is_dirty = True

    def get_node_range(self, node):
        """get ip range from specified node

        Args:
            node (jumpscale.client.explorer.models.TfgridDirectoryNode2): node object

        Returns:
            (IPRange): ip range field
        """
        for network_resource in self._network.network_resources:
            if network_resource.node_id == node.node_id:
                return network_resource.iprange
        self._bot.stop(f"Node {node.node_id} is not part of network")

    def update(self, tid, currency=None, bot=None):
        """create reservations and update status and show payments stuff
        Args:
            tid (int): customer tid (j.core.identity.me.tid)
            currency (str, optional): "TFT" or "FreeTFT". Defaults to None.
            bot (GedisChatBot, optional): bot instance. Defaults to None.

        Returns:
            bool: True if successful
        """
        if self._is_dirty:
            reservation = j.sals.zos.get().reservation_create()
            reservation.data_reservation.networks.append(self._network)
            form_info = {
                "chatflow": "network",
                "Currency": self.currency,
                "Solution expiration": self._expiration.timestamp(),
            }
            metadata = j.sals.reservation_chatflow.get_solution_metadata(
                self.name, SolutionType.Network, form_info=form_info
            )

            metadata["parent_network"] = self.resv_id
            self._sal.add_reservation_metadata(reservation, metadata)

            reservation_create = self._sal.register_reservation(
                reservation, self._expiration.timestamp(), tid, currency=currency, bot=bot
            )
            rid = reservation_create.reservation_id
            payment, _ = j.sals.reservation_chatflow.show_payments(self._bot, reservation_create, currency)
            if payment["free"]:
                pass
            elif payment["wallet"]:
                j.sals.zos.get().billing.payout_farmers(payment["wallet"], reservation_create)
                j.sals.reservation_chatflow.wait_payment(bot, rid, threebot_app=False)
            else:
                j.sals.reservation_chatflow.wait_payment(
                    bot, rid, threebot_app=True, reservation_create_resp=reservation_create
                )
            wait_reservation_results = self._sal.wait_reservation(self._bot, rid)
            # Update solution saved locally
            explorer_name = self._sal._explorer.url.split(".")[1]
            old_solution = self.solutions.get(f"{explorer_name}_{self.resv_id}")
            solution = self.solutions.get(
                f"{explorer_name}_{rid}",
                explorer=old_solution.explorer,
                form_info=old_solution.form_info,
                rid=rid,
                solution_type=old_solution.solution_type,
            )
            solution.name = self.name
            solution.save()
            self.solutions.delete(f"{explorer_name}_{self.resv_id}")
            return wait_reservation_results
        return True

    def copy(self, customer_tid):
        """create a copy of network object

        Args:
            customer_tid (int): customet tid (j.core.identity.me.tid)

        Returns:
            (Network): copy of the network
        """
        network_copy = None
        explorer = j.core.identity.me.explorer
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
        """ask for free ip from a specific node and mark it as used in chatbot

        Args:
            node (jumpscale.client.explorer.models.TfgridDirectoryNode2): reqired node to ask ip from
            message (str): message to the chatflow slide

        Returns:
            [str]: free ip
        """
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
        """return free ip

        Args:
            node (jumpscale.client.explorer.models.TfgridDirectoryNode2): reqired node to get free ip from

        Returns:
            [str]: free ip to use
        """
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
        """This class is responsible for managing, creating, cancelling reservations"""
        self.solutions = StoredFactory(TfgridSolution1)
        self.payments = StoredFactory(TfgridSolutionsPayment1)
        self.deployed_reservations = StoredFactory(DeployedReservation)

    @property
    def me(self):
        return j.core.identity.me

    @property
    def _explorer(self):
        return j.core.identity.me.explorer

    def decrypt_reservation_metadata(self, metadata_encrypted):
        """decrypt the reservation metadata using identity nacl

        Args:
            metadata_encrypted (bytes): encrypted metadata

        Returns:
            [str]: decrypted solution metadata
        """
        pk = j.core.identity.me.nacl.signing_key.verify_key.to_curve25519_public_key()
        sk = j.core.identity.me.nacl.signing_key.to_curve25519_private_key()
        box = Box(sk, pk)
        return box.decrypt(base64.b85decode(metadata_encrypted.encode())).decode()

    def check_solution_type(self, reservation):
        """categorize the solutions by types

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): user reservation

        Returns:
            [jumpscale.clients.explorer.models.SolutionType]: type of the solution
        """
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
        return SolutionType.Unknown

    def get_solution_ubuntu_info(self, metadata, reservation):
        """get ubuntu solutions information from metadata on explorer and update local ones

        Args:
            metadata (dict): ubuntu reservation metadata
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): ubuntu reservation

        Returns:
            [dict]: updated metadata
        """
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
        """get information about solution exposed from reservation

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1)

        return dict of info
        """

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
        """get flist solutions information from metadata on explorer and update local ones

        Args:
            metadata (dict): flist reservation metadata
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): ubuntu reservation

        Returns:
            [dict]: updated metadata
        """
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
        """get domain delegated metadata info

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation object

        Returns:
            [dict]: domain delegated metadata info
        """

        delegated_domain = reservation.data_reservation.domain_delegates[0]
        return {"Domain": delegated_domain.domain, "Gateway": delegated_domain.node_id}

    def save_reservation(self, rid, name, solution_type, form_info=None):
        """save user reservation in local config manager

        Args:
            rid (int): user identity (j.core.identity.me.tid)
            name (str): reservation name
            solution_type (SolutionType): type of the solution from types enum
            form_info (dict, optional): reservation user info. Defaults to None.
        """
        form_info = form_info or {}
        explorer_name = self._explorer.url.split(".")[1]
        reservation = self.solutions.get(f"{explorer_name}_{rid}")
        reservation.rid = rid
        reservation.name = name
        reservation.solution_type = solution_type
        reservation.form_info = form_info
        reservation.explorer = self._explorer.url
        reservation.save()

    def get_solutions_explorer(self, deployed=True):
        """get the updated reservations from explorer

        Args:
            deployed (bool, optional): set False to get all reservations. Defaults to True.

        Returns:
            list: list of reservations
        """
        customer_tid = self.me.tid
        reservations_data = []
        reservations = []
        if deployed:
            reservations = self._explorer.reservations.list(customer_tid, "DEPLOY")
        else:
            reservations = self._explorer.reservations.list(customer_tid)
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
                    solution_type = self.check_solution_type(reservation).value
                else:
                    solution_type = metadata["form_info"].pop("chatflow", SolutionType.Unknown.value)
                if solution_type == SolutionType.Unknown.value:
                    continue
                elif solution_type == SolutionType.Ubuntu.value:
                    metadata = self.get_solution_ubuntu_info(metadata, reservation)
                elif solution_type == SolutionType.Flist.value:
                    metadata = self.get_solution_flist_info(metadata, reservation)
                elif solution_type == SolutionType.Network.value:
                    if metadata["name"] in networks:
                        continue
                    networks.append(metadata["name"])
                elif solution_type == SolutionType.Gitea.value:
                    metadata["form_info"]["Public key"] = reservation.data_reservation.containers[0].environment[
                        "pub_key"
                    ]
                elif solution_type == SolutionType.Exposed.value:
                    meta = metadata
                    metadata = {"form_info": meta}
                    metadata["form_info"].update(self.get_solution_exposed_info(reservation))
                    metadata["name"] = metadata["form_info"].get("Domain")

                info = metadata["form_info"]
                name = metadata["name"]
            else:
                solution_type = self.check_solution_type(reservation)
                if type(solution_type) is not str:
                    solution_type = solution_type.value
                info = {}
                name = f"unknown_{reservation.id}"
                if solution_type == SolutionType.Unknown.value:
                    continue
                elif solution_type == SolutionType.Network.value:
                    name = reservation.data_reservation.networks[0].name
                    if name in networks:
                        continue
                    networks.append(name)
                elif solution_type == SolutionType.DelegatedDomain.value:
                    info = self.get_solution_domain_delegates_info(reservation)
                    if not info.get("Solution name"):
                        name = f"unknown_{reservation.id}"
                    else:
                        name = info["Solution name"]
                elif solution_type == SolutionType.Exposed.value:
                    info = self.get_solution_exposed_info(reservation)
                    info["Solution name"] = name
                    name = info.get("Domain")

            count = dupnames.setdefault(solution_type, {}).setdefault(name, 1)
            if count != 1:
                dupnames[solution_type][name] = count + 1
                name = f"{name}_{count}"
            # append reservation
            reservations_data.append(
                {
                    "id": reservation.id,
                    "name": name,
                    "solution_type": solution_type,
                    "form_info": info,
                    "status": reservation.next_action.name,
                    "reservation_date": reservation.epoch.ctime(),
                    "reservation": reservation._get_data(),
                }
            )
        return reservations_data

    def update_local_reservations(self):
        """update local reserfvations with new ones"""
        for obj in self.solutions.list_all():
            self.solutions.delete(obj)
        reservations = self.get_solutions_explorer()
        for reservation in reservations:
            self.save_reservation(
                reservation["id"], reservation["name"], reservation["solution_type"], form_info=reservation["form_info"]
            )

    def list_wallets(self):
        """
        List all stellar client wallets from bcdb. Based on explorer instance only either wallets with network type TEST or STD are returned
        rtype: list
        """
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
        escrow_info = j.sals.zos.get().reservation_escrow_information_with_qrcodes(reservation_create_resp)
        escrow_address = escrow_info["escrow_address"]
        escrow_asset = escrow_info["escrow_asset"]
        reservationid = escrow_info["reservationid"]
        qrcode = escrow_info["qrcode"]
        remaning_time = j.data.time.get(expiration_provisioning).humanize()
        payment_details = self.get_payment_details(escrow_info, escrow_asset.split(":")[0])

        message_text = f"""
        <h3>Make a Payment</h3>
        Scan the QR code with your wallet (do not change the message) or enter the information below manually and proceed with the payment. Make sure to add the reservationid as memo_text.
        <p>If no payment is made {remaning_time} the reservation will be canceled</p>

        <h4> Destination Wallet Address: </h4>  {escrow_address} \n
        <h4> Currency: </h4>  {escrow_asset} \n
        <h4> Reservation ID: </h4>  {reservationid} \n
        <h4> Payment Details: </h4> {payment_details} \n
        """

        bot.qrcode_show(data=qrcode, msg=message_text, scale=4, update=True, html=True)

    def create_payment(
        self, rid, currency, escrow_address, escrow_asset, total_amount, payment_source, farmer_payments
    ):
        """create payment object and save it locally

        Args:
            rid (int): customer tid
            currency (str): reservation currency "TFT" or "FreeTFT"
            escrow_address (str): escrow_address
            escrow_asset (str): escrow asset
            total_amount (str): paid amount
            payment_source (str): payment source
            farmer_payments (list): total list of farmer payments

        Returns:
            [jumpscale.clients.explorer.models.TfgridSolutionsPayment1]: payment object
        """
        explorer_name = self._explorer.url.split(".")[1]
        payment_obj = self.payments.get(f"{explorer_name}_{rid}")
        payment_obj.explorer = self._explorer.url
        payment_obj.rid = rid
        payment_obj.currency = currency
        payment_obj.escrow_address = escrow_address
        payment_obj.escrow_asset = escrow_asset
        payment_obj.total_amount = str(total_amount)
        payment_obj.transaction_fees = f"{TRANSACTION_FEES} {currency}"
        payment_obj.payment_source = payment_source
        for farmer in farmer_payments:
            farmer_name = self._explorer.farms.get(farm_id=farmer["farmer_id"]).name
            payment_obj.farmer_payments[farmer_name] = farmer["total_amount"]
        return payment_obj

    def get_payment_details(self, escrow_info, currency):
        """split payment details and get each one

        Args:
            escrow_info (str): payment info
            currency (str): currency used

        Returns:
            [str]: payment details
        """

        farmer_payments = escrow_info["farmer_payments"]
        total_amount = escrow_info["total_amount"]

        payment_details = ""
        payment_details += '<table style="width: 50%; font-family: arial, sans-serif; border-collapse: collapse;">'
        for farmer in farmer_payments:
            farmer_name = self._explorer.farms.get(farm_id=farmer["farmer_id"]).name
            payment_details += (
                f"<tr><td>Farmer {farmer_name}</td><td>{format(farmer['total_amount'],'.7f')} {currency}</td></tr>"
            )
        payment_details += f"<tr><td>Transaction Fees</td><td>{TRANSACTION_FEES} {currency}</td></tr>"
        payment_details += (
            f"<tr><td>Total amount</td><td>{format(total_amount + TRANSACTION_FEES,'.7f')} {currency}</td></tr>"
        )
        payment_details += "</table>"

        return payment_details

    def show_payments(self, bot, reservation_create_resp, currency):
        """Show valid payment options in chatflow available. All available wallets possible are shown or usage of External wallet (QR code) is shown
        where a QR code is viewed for the user to scan and continue with their payment

        Args:
            bot (GedisChatBot): instance of the used bot
            reservation_create_resp (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): result of reservation
            currency (str): currency used

        Returns:
            [jumpscale.clients.explorer.models.TfgridSolutionsPayment1]: payment object wallet in case a wallet is used
        """
        payment = {"wallet": None, "free": False}
        if not (reservation_create_resp.escrow_information and reservation_create_resp.escrow_information.details):
            payment["free"] = True
            return payment, None
        escrow_info = j.sals.zos.get().reservation_escrow_information_with_qrcodes(reservation_create_resp)

        escrow_address = escrow_info["escrow_address"]
        escrow_asset = escrow_info["escrow_asset"]
        total_amount = escrow_info["total_amount"]
        rid = reservation_create_resp.reservation_id

        wallets = self.list_wallets()
        wallet_names = []
        for w in wallets.keys():
            wallet_names.append(w)
        wallet_names.append("External Wallet (QR Code)")

        payment_details = self.get_payment_details(escrow_info, currency)

        message = f"""
        Billing details:
        <h4> Destination Wallet address: </h4>  {escrow_address} \n
        <h4> Currency: </h4>  {escrow_asset} \n
        <h4> Payment Details: </h4> {payment_details} \n
        <h4> Choose a wallet name to use for payment or proceed with the payment through an external wallet (QR Code) </h4>
        """
        retry = False
        while True:

            result = bot.single_choice(message, wallet_names, html=True, retry=retry)

            if result not in wallet_names:
                retry = True
                continue
            if result == "External Wallet (QR Code)":
                reservation = self._explorer.reservations.get(rid)
                self.show_escrow_qr(bot, reservation_create_resp, reservation.data_reservation.expiration_provisioning)
                payment_obj = self.create_payment(
                    rid=rid,
                    currency=currency,
                    escrow_address=escrow_address,
                    escrow_asset=escrow_asset,
                    total_amount=total_amount,
                    payment_source="external_wallet",
                    farmer_payments=escrow_info["farmer_payments"],
                )
                return payment, payment_obj
            else:
                payment["wallet"] = wallets[result]
                balances = payment["wallet"].get_balance().balances
                current_balance = None
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
                <h4> Choose a wallet name to use for payment or proceed with payment through External Wallet (QR Code) </h4>
                """

    def wait_payment(self, bot, rid, threebot_app=False, reservation_create_resp=None):
        """wait slide untill payment is ready

        Args:
            bot (GedisChatBot): bot instance
            rid (int): customer tid
            threebot_app (bool, optional): is using threebot app payment. Defaults to False.
            reservation_create_resp (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1, optional): reservation object response. Defaults to None.
        """

        # wait to check payment is actually done next_action changed from:PAY
        def is_expired(reservation):
            return reservation.data_reservation.expiration_provisioning.timestamp() < j.data.time.get().timestamp

        reservation = self._explorer.reservations.get(rid)
        while True:
            remaning_time = j.data.time.get(reservation.data_reservation.expiration_provisioning).humanize(
                granularity=["minute", "second"]
            )
            deploying_message = f"""\
            # Payment being processed...

            <br />Deployment will be cancelled if payment is not successful {remaning_time}
            """
            bot.md_show_update(dedent(deploying_message), md=True)
            if reservation.next_action != "PAY":
                return
            if is_expired(reservation):
                res = f"# Failed to wait for payment for reservation:```{reservation.id}```:\n"
                for x in reservation.results:
                    if x.state == "ERROR":
                        res += f"\n### {x.category}: ```{x.message}```\n"
                link = f"{self._explorer.url}/reservations/{reservation.id}"
                res += f"<h2> <a href={link}>Full reservation info</a></h2>"
                j.sals.zos.get().reservation_cancel(rid)
                bot.stop(res, md=True, html=True)
            if threebot_app and reservation_create_resp:
                self.show_escrow_qr(bot, reservation_create_resp, reservation.data_reservation.expiration_provisioning)
            time.sleep(5)
            reservation = self._explorer.reservations.get(rid)

    def _reservation_failed(self, bot, reservation):
        failed = j.sals.zos.get().reservation_failed(reservation)
        if failed:
            res = f"# Sorry your reservation ```{reservation.id}``` has failed :\n"
            for x in reservation.results:
                if x.state == "ERROR":
                    res += f"\n### {x.category}: ```{x.message}```\n"
            link = f"{self._explorer.url}/reservations/{reservation.id}"
            res += f"<h2> <a href={link}>Full reservation info</a></h2>"
            j.sals.zos.get().reservation_cancel(reservation.id)
            bot.stop(res, md=True, html=True)

    def wait_reservation(self, bot, rid):
        """
        Wait for reservation results to be complete, have errors, or expire.
        If there are errors then error message is previewed in the chatflow to the user and the chat is ended.

        Args:
            bot (GedisChatBot): bot instance
            rid (int): user tid
        """

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
            """[summary]

            Args:
                reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation object

            Returns:
                [bool]: True if the reservation is expired
            """
            return reservation.data_reservation.expiration_provisioning.timestamp() < j.data.time.get().timestamp

        reservation = self._explorer.reservations.get(rid)
        while True:
            remaning_time = j.data.time.get(reservation.data_reservation.expiration_provisioning).humanize(
                granularity=["minute", "second"]
            )
            deploying_message = f"""
            # Deploying...

            <br />Deployment will be cancelled if it is not successful in {remaning_time}
            """
            bot.md_show_update(dedent(deploying_message), md=True)
            self._reservation_failed(bot, reservation)

            if is_finished(reservation):
                if reservation.next_action != NextAction.DEPLOY:
                    res = f"# Sorry your reservation ```{reservation.id}``` failed to deploy\n"
                    for x in reservation.results:
                        if x.state == "ERROR":
                            res += f"\n### {x.category}: ```{x.message}```\n"
                    bot.stop(res, md=True, html=True)
                return reservation.results
            if is_expired(reservation):
                res = f"# Sorry your reservation ```{reservation.id}``` failed to deploy in time:\n"
                for x in reservation.results:
                    if x.state == "ERROR":
                        res += f"\n### {x.category}: ```{x.message}```\n"
                link = f"{self._explorer.url}/reservations/{reservation.id}"
                res += f"<h2> <a href={link}>Full reservation info</a></h2>"
                j.sals.zos.get().reservation_cancel(rid)
                bot.stop(res, md=True, html=True)
            time.sleep(1)
            reservation = self._explorer.reservations.get(rid)

    def register_reservation(
        self, reservation, expiration, customer_tid, expiration_provisioning=1000, currency=None, bot=None
    ):
        """Register any reservation through the chatflow.
        This reservation could include anything such as a new network, container, kubernetes cluster, or zdb.
        It returns the reservation id of the registered reservation.

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation object
            expiration (int): epoch time when the reservation should be canceled automaticly
            customer_tid (int): Id of the customer making the reservation
            expiration_provisioning (int): timeout on the deployment of the provisioning in seconds
            currency (str): "TFT" of "FreeTFT"
            bot (GedisChatBot): bot instance

        Return:
            [jumpscale.clients.explorer.models.TfgridWorkloadsReservation1]: reservation create object

        """
        expiration_provisioning += j.data.time.get().timestamp
        try:
            reservation_create = j.sals.zos.get().reservation_register(
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
        """register the reservation, pay and deploy

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation object
            expiration (int): epoch time when the reservation should be canceled automaticly
            customer_tid (int): Id of the customer making the reservation
            currency (str): "TFT" of "FreeTFT"
            bot (GedisChatBot): bot instance
            wallet (TfgridDirectoryWallet_address1): wallet object. Defaults to None.

        Returns:
            [int]: reservation id
        """

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
            j.sals.zos.get().billing.payout_farmers(payment["wallet"], reservation_create)
            self.wait_payment(bot, resv_id, threebot_app=False)
        elif not payment["free"]:
            self.wait_payment(bot, resv_id, threebot_app=True, reservation_create_resp=reservation_create)

        self.wait_reservation(bot, resv_id)
        if payment_obj:
            payment_obj.save()
        return resv_id

    def get_kube_network_ip(self, reservation_data):
        """get kubernetes reservation network id

        Args:
            reservation_data (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1.reservation_data): reservation data object

        Returns:
            [str, str]: network_id, ip
        """
        network_id = reservation_data["kubernetes"][0]["network_id"]
        ip = reservation_data["kubernetes"][0]["ipaddress"]
        return network_id, ip

    def list_gateways(self, bot, currency=None):
        """list available gateways that supports passed currency

        Args:
            bot (GedisChatBot): bot instance
            currency (str, optional): "TFT" or "FreeTFT". Defaults to None.

        Returns:
            [dict]
        """
        unknowns = ["", None, "Uknown", "Unknown"]
        gateways = {}
        farms = {}
        for g in j.sals.zos.get()._explorer.gateway.list():
            if not j.sals.zos.get().nodes_finder.filter_is_up(g):
                continue
            location = []
            for area in ["continent", "country", "city"]:
                areaname = getattr(g.location, area)
                if areaname not in unknowns:
                    location.append(areaname)
            currencies = list()

            farm_id = g.farm_id
            if farm_id not in farms:
                farms[farm_id] = j.sals.zos.get()._explorer.farms.get(farm_id)

            addresses = farms[farm_id].wallet_addresses
            for address in addresses:
                if address.asset not in currencies:
                    if address.asset == "FreeTFT" and not g.free_to_use:
                        continue
                    currencies.append(address.asset)

            reservation_currency = ", ".join(currencies)

            if currency and currency not in currencies:
                continue
            gtext = f"{' - '.join(location)} ({reservation_currency}) ID: {g.node_id}"
            gateways[gtext] = g
        return gateways

    def select_gateway(self, bot, currency=None):
        """prompt user about available gateways that supports passed currency

        Args:
            bot (GedisChatBot): bot instance
            currency (str, optional): "TFT" or "FreeTFT". Defaults to None.

        Returns:
            [TfgridDirectoryGateway1]
        """
        gateways = self.list_gateways(bot, currency)
        if not gateways:
            bot.stop("No available gateways")
        options = sorted(list(gateways.keys()))
        gateway = bot.drop_down_choice("Please choose a gateway", options, required=True)
        return gateways[gateway]

    def list_delegate_domains(self, customer_tid, currency=None):
        """list delegated domains with passed currency

        Args:
            customer_tid (int): user tid
            currency (str, optional): currency to search with. Defaults to None.

        Returns:
            [dict]: [domains names]
        """
        reservations = j.sals.zos.get().reservation_list(tid=customer_tid, next_action="DEPLOY")
        domains = dict()
        names = set()
        for reservation in sorted(reservations, key=lambda r: r.id, reverse=True):
            reservation_currency = self.get_currency(reservation)
            if reservation.next_action != NextAction.DEPLOY:
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
        """get the network object

        Args:
            bot (GedisChatBot): bot instance
            customer_tid (int): user tid
            name (str): [network name]

        Returns:
            [jumpscale.clients.explorer.models.TfgridWorkloadsReservationNetwork1]: nework object
        """
        reservations = j.sals.zos.get().reservation_list(tid=customer_tid, next_action="DEPLOY")
        networks = self.list_networks(customer_tid, reservations)
        for key in networks.keys():
            network, expiration, currency, resv_id = networks[key]
            if network.name == name:
                return Network(network, expiration, bot, reservations, currency, resv_id)

    def list_networks(self, tid, reservations=None):
        """list all available networks from reservations

        Args:
            tid (int): user tid
            reservation (list of jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): list of reservation objects

        Returns:
            [type]: [description]
        """
        if not reservations:
            reservations = j.sals.zos.get().reservation_list(tid=tid, next_action="DEPLOY")
        networks = dict()
        names = set()
        for reservation in sorted(reservations, key=lambda r: r.id, reverse=True):
            if reservation.next_action != NextAction.DEPLOY:
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
        """get reservation currency

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation object

        Returns:
            [str]
        """
        currencies = reservation.data_reservation.currencies
        if currencies:
            return currencies[0]
        elif reservation.data_reservation.networks and reservation.data_reservation.networks[0].network_resources:
            node_id = reservation.data_reservation.networks[0].network_resources[0].node_id
            if self._explorer.nodes.get(node_id).free_to_use:
                return "FreeTFT"

        return "TFT"

    def cancel_solution_reservation(self, solution_type, solution_name):
        """cancel solution reservation

        Args:
            solution_type (str): solution_type
            solution_name (str): solution name
        """
        for name in self.solutions.list_all():
            solution = self.solutions.get(name)
            if solution.name == solution_name and solution.solution_type == solution_type:
                # Cancel all parent networks if solution type is network
                if solution.solution_type == SolutionType.Network:  ## TODO change to SolutionType.Network.value
                    curr_network_resv = self._explorer.reservations.get(solution.rid)
                    while curr_network_resv:
                        if curr_network_resv.metadata:
                            try:
                                network_metadata = self.decrypt_reservation_metadata(curr_network_resv.metadata)
                                network_metadata = json.loads(network_metadata)
                            except Exception:
                                break
                            if "parent_network" in network_metadata:
                                parent_resv = self._explorer.reservations.get(network_metadata["parent_network"])
                                j.sals.zos.get().reservation_cancel(parent_resv.id)
                                curr_network_resv = parent_resv
                                continue
                        curr_network_resv = None

                j.sals.zos.get().reservation_cancel(solution.rid)
                self.solutions.delete(name)

    def get_solutions(self, solution_type):
        """get deployed solutions from specified type

        Args:
            solution_type (str): solution type

        Returns:
            [list]: list of reservations objects
        """
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
                    "reservation": reservation._get_data(),
                    "type": solution_type.value,
                    "form_info": json.dumps(solution.form_info),
                }
            )
        return reservations

    def add_reservation_metadata(self, reservation, metadata):
        """add the encrypted metadata to reservation object

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation object
            metadata (dict): reservation metadata

        Returns:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation with metadata
        """
        meta_json = json.dumps(metadata)

        pk = j.core.identity.me.nacl.signing_key.verify_key.to_curve25519_public_key()
        sk = j.core.identity.me.nacl.signing_key.to_curve25519_private_key()
        box = Box(sk, pk)
        encrypted_metadata = base64.b85encode(box.encrypt(meta_json.encode())).decode()
        reservation.metadata = encrypted_metadata
        return reservation

    def get_solution_metadata(self, solution_name, solution_type, form_info=None):
        """get metadata from a solution

        Args:
            solution_name (str): solution name
            solution_type (str): solution type
            form_info (dict, optional): info from user slide. Defaults to None.

        Returns:
            dict: metadata
        """
        form_info = form_info or {}
        reservation = {}
        reservation["name"] = solution_name
        reservation["form_info"] = form_info
        reservation["solution_type"] = solution_type.value
        reservation["explorer"] = self._explorer.url
        return reservation

    def create_network(
        self,
        network_name,
        reservation,
        ip_range,
        customer_tid,
        ip_version,
        access_node,
        expiration=None,
        currency=None,
        bot=None,
    ):
        """create network to deploy reservation on

        Args:
            network_name (str): network name
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation object
            ip_range (IPRange): selected ip range eg: "10.70.0.0/16"
            customer_tid (int): user tid
            ip_version (str): "IPv4" or "IPv6"
            expiration (int, optional): epoch for expiration time. Defaults to None.
            currency (str, optional): wanted currency . Defaults to None.
            bot (GedisChatBot, optional): bot instance. Defaults to None.

        Raises:
            StopChatFlow: when no available node

        Returns:
            [dict]: network config
        """

        network = j.sals.zos.get().network.create(reservation, ip_range, network_name)
        node_subnets = netaddr.IPNetwork(ip_range).subnet(24)
        network_config = dict()
        use_ipv4 = ip_version == "IPv4"

        j.sals.zos.get().network.add_node(network, access_node.node_id, str(next(node_subnets)))
        wg_quick = j.sals.zos.get().network.add_access(
            network, access_node.node_id, str(next(node_subnets)), ipv4=use_ipv4
        )

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

    def get_ip_range(self, bot=None):
        """prompt user to select iprange

        Args:
            bot (GedisChatBot): bot instance

        Returns:
            [IPRange]: ip selected by user
        """
        iprange_choice = "Choose IP range for me"
        if bot:
            ip_range_choose = ["Configure IP range myself", "Choose IP range for me"]
            iprange_choice = bot.single_choice(
                "How would you like to configure the network IP range",
                ip_range_choose,
                required=True,
                default=ip_range_choose[1],
            )
        if iprange_choice == "Configure IP range myself":
            ip_range = bot.string_ask("Please add private IP Range of the network")
        else:
            first_digit = random.choice([172, 10])
            if first_digit == 10:
                second_digit = random.randint(0, 255)
            else:
                second_digit = random.randint(16, 31)
            ip_range = str(first_digit) + "." + str(second_digit) + ".0.0/16"
        return ip_range

    def select_farms(self, bot, message=None, currency=None, retry=False, sru=None, cru=None, hru=None, mru=None):
        """prompt user to select farm to deploy on

        Args:
            bot (GedisChatBot): bot instance
            message (str, optional): bot screen message. Defaults to None.
            currency (str, optional): wanted currency to deal with. Defaults to None.
            retry (bool, optional): retry if failed. Defaults to False.

        Returns:
            farm object
        """
        message = message or "Select 1 or more farms to distribute nodes on"
        farms = self._explorer.farms.list()
        farm_names = []
        for f in farms:
            if j.sals.zos.get().nodes_finder.filter_farm_currency(f, currency) and self.check_farm_resources(
                farm_id=f.id, sru=sru, cru=cru, hru=hru, mru=mru, currency=currency
            ):
                farm_names.append(f.name)
        if not farm_names:
            bot.stop("No farms with available resources that match the specified.")
        farms_selected = bot.multi_list_choice(message, farm_names, retry=retry, auto_complete=True)
        return farms_selected

    def check_farm_resources(self, farm_id, sru=None, mru=None, hru=None, cru=None, currency=None):
        farm_nodes = self._explorer.nodes.list(farm_id=farm_id)
        nodes = []
        for node in farm_nodes:
            if not j.sals.zos.get().nodes_finder.filter_is_up(node):
                continue
            if currency == "FreeTFT" and not node.free_to_use:
                continue
            if sru:
                available_sru = node.total_resources.sru - node.reserved_resources.sru
                if sru > available_sru:
                    continue
            if cru:
                available_cru = node.total_resources.cru - node.reserved_resources.cru
                if cru > available_cru:
                    continue
            if hru:
                available_hru = node.total_resources.hru - node.reserved_resources.hru
                if hru > available_hru:
                    continue
            if mru:
                available_mru = node.total_resources.mru - node.reserved_resources.mru
                if mru > available_mru:
                    continue
            nodes.append(node)
        return nodes

    def select_network(self, bot, customer_tid):
        """prompt user to select a specific network

        Args:
            bot (GedisChatBot): bot instance
            customer_tid (int): user tid

        Returns:
            Network object
        """
        reservations = j.sals.zos.get().reservation_list(tid=customer_tid, next_action="DEPLOY")
        networks = self.list_networks(customer_tid, reservations)
        names = []
        for n in networks.keys():
            names.append(n)
        if not names:
            res = "You don't have any networks, please use the network chatflow to create one"
            res = j.tools.jinja2.render_template(template_text=res)
            bot.stop(res)
        while True:
            result = bot.single_choice("Choose a network", names, required=True)
            if result not in networks:
                continue
            network, expiration, currency, resv_id = networks[result]
            return Network(network, expiration, bot, reservations, currency, resv_id)

    def validate_node(self, nodeid, query=None, currency=None):
        """validate the node if it's ok to use and have enough resources

        Args:
            nodeid (str): node id
            query (dict, optional): search paramas. Defaults to None.
            currency (str, optional): wanted currency. Defaults to None.

        Returns:
            Node object
        """
        try:
            node = self._explorer.nodes.get(nodeid)
        except requests.exceptions.HTTPError:
            raise j.exceptions.NotFound(f"Node {nodeid} doesn't exists please enter a valid nodeid")
        if not j.sals.zos.get().nodes_finder.filter_is_up(node):
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
                freevalue = getattr(node.total_resources, unit) - getattr(node.reserved_resources, unit)
                if freevalue < value:
                    raise j.exceptions.Value(
                        f"Node {nodeid} does not have enough available {unit} resources for this request {value} required {freevalue} available, please choose another one"
                    )
        return node

    def get_nodes(
        self,
        number_of_nodes,
        cru=None,
        sru=None,
        mru=None,
        hru=None,
        ipv4u=None,
        currency="TFT",
        ip_version=None,
        pool_ids=None,
        filter_blocked=True,
        identity_name=None,
        sort_by_disk_space=False,
    ):
        """get available nodes to deploy solutions on

        Args:
            number_of_nodes (int): required nodes count
            farm_id (int, optional): id for farm to search with. Defaults to None.
            farm_names (list, optional): farms to search in. Defaults to None.
            cru (int, optional): cpu resource. Defaults to None.
            sru (int, optional): ssd resource. Defaults to None.
            mru (int, optional): memory resource. Defaults to None.
            hru (int, optional): hdd resources. Defaults to None.
            currency (str, optional): wanted currency. Defaults to "TFT".
            sort_by_disk_space (bool, optional): return nodes with highest free disk space (sru). If set to False, can be overriden by SORT_NODES_BY_SRU in config
        Raises:
            StopChatFlow: if no nodes found

        Returns:
            list of available nodes
        """
        sort_by_disk_space = sort_by_disk_space or j.core.config.get("SORT_NODES_BY_SRU", False)

        def filter_disallowed_nodes(disallowed_node_ids, nodes):
            result = []
            for node in nodes:
                if node.node_id not in disallowed_node_ids:
                    result.append(node)
            return result

        disallowed_node_ids = []
        if filter_blocked:
            disallowed_node_ids = self.list_blocked_nodes().keys()
        if j.config.get("OVER_PROVISIONING"):
            cru = 0
        nodes_distribution = self._distribute_nodes(number_of_nodes, pool_ids=pool_ids)
        # to avoid using the same node with different networks
        nodes_selected = []
        selected_ids = []
        zos = j.sals.zos.get()
        for pool_id in nodes_distribution:
            nodes_number = nodes_distribution[pool_id]
            if not pool_ids:
                pool_id = None
            nodes = j.sals.zos.get(identity_name).nodes_finder.nodes_by_capacity(
                cru=cru, sru=sru, mru=mru, hru=hru, currency=currency, pool_id=pool_id
            )
            nodes = filter_disallowed_nodes(disallowed_node_ids, nodes)
            nodes = self.filter_nodes(nodes, currency == "FreeTFT", ip_version=ip_version)
            farm_name = j.sals.marketplace.deployer.get_pool_farm_name(pool_id)
            err_msg = f"""Failed to find resources (cru={cru}, sru={sru}, mru={mru}, hru={hru} and ip_version={ip_version} in pool with id={pool_id} in farm {farm_name}) for this reservation.
                        If you are using a low resources environment like testnet,
                        please make sure to allow over provisioning from the settings tab in dashboard.
                        For more info visit <a href='https://manual2.threefold.io/#/3bot_settings?id=developers-options'>our manual</a>
                    """
            if sort_by_disk_space:
                nodes = sorted(nodes, key=lambda x: x.total_resources.sru - x.reserved_resources.sru, reverse=True)
            for _ in range(nodes_number):
                try:
                    if sort_by_disk_space:
                        if not nodes:
                            raise StopChatFlow(err_msg, htmlAlert=True)
                        for node in nodes:
                            if node.node_id not in selected_ids:
                                break
                    else:
                        node = random.choice(nodes)
                        while node.node_id in selected_ids:
                            node = random.choice(nodes)
                except IndexError:
                    raise StopChatFlow(err_msg, htmlAlert=True)
                # Validate if the selected node has public ip or not
                if ipv4u:
                    if zos.nodes_finder.filter_public_ip_bridge(node):
                        nodes.remove(node)
                        nodes_selected.append(node)
                        selected_ids.append(node.node_id)

                else:
                    nodes.remove(node)
                    nodes_selected.append(node)
                    selected_ids.append(node.node_id)
        return nodes_selected

    def filter_nodes(self, nodes, free_to_use, ip_version=None):
        """filter nodes by free to use flag

        Args:
            nodes (list of nodes objects)
            free_to_use (bool)

        Returns:
            list of filtered nodes
        """
        nodes = filter(j.sals.zos.get().nodes_finder.filter_is_up, nodes)
        nodes = list(nodes)
        if free_to_use:
            nodes = list(nodes)
            nodes = filter(j.sals.zos.get().nodes_finder.filter_is_free_to_use, nodes)
        elif not free_to_use:
            nodes = list(nodes)

        if ip_version:
            use_ipv4 = ip_version == "IPv4"

            if use_ipv4:
                nodefilter = j.sals.zos.get().nodes_finder.filter_public_ip4
            else:
                nodefilter = j.sals.zos.get().nodes_finder.filter_public_ip6

            nodes = filter(j.sals.zos.get().nodes_finder.filter_is_up, filter(nodefilter, nodes))
            if not nodes:
                raise StopChatFlow("Could not find available access node")
        return list(nodes)

    def _distribute_nodes(self, number_of_nodes, pool_ids):
        nodes_distribution = {}
        nodes_left = number_of_nodes
        result_ids = list(pool_ids) if pool_ids else []
        if not pool_ids:
            pools = self._explorer.pools.list()
            result_ids = []
            for p in pools:
                result_ids.append(p.pool_id)
        random.shuffle(result_ids)
        id_pointer = 0
        while nodes_left:
            pool_id = result_ids[id_pointer]
            if pool_id not in nodes_distribution:
                nodes_distribution[pool_id] = 0
            nodes_distribution[pool_id] += 1
            nodes_left -= 1
            id_pointer += 1
            if id_pointer == len(result_ids):
                id_pointer = 0
        return nodes_distribution

    def get_farm_names(self, number_of_nodes, bot, cru=None, sru=None, mru=None, hru=None, currency="TFT", message=""):
        """get list with available farm names and prompt user to choose one

        Args:
            number_of_nodes (int): required nodes count
            farm_id (int, optional): id for farm to search with. Defaults to None.
            farm_names (list, optional): farms to search in. Defaults to None.
            cru (int, optional): cpu resource. Defaults to None.
            sru (int, optional): ssd resource. Defaults to None.
            mru (int, optional): memory resource. Defaults to None.
            hru (int, optional): hdd resources. Defaults to None.
            currency (str, optional): wanted currency. Defaults to "TFT".
            message (str): message to user. Defaults to ""

        """
        farms_message = f"Select 1 or more farms to distribute the {message} nodes on. If no selection is made, the farms will be chosen randomly"
        empty_farms = set()
        all_farms = self._explorer.farms.list()
        retry = False
        while True:
            farms = self.select_farms(
                bot, farms_message, currency=currency, retry=retry, cru=cru, sru=sru, hru=hru, mru=mru
            )
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
        """get list with available farm and make sure it has resources

        Args:
            number_of_nodes (int): required nodes count
            farm_id (int, optional): id for farm to search with. Defaults to None.
            farm_names (list, optional): farms to search in. Defaults to None.
            cru (int, optional): cpu resource. Defaults to None.
            sru (int, optional): ssd resource. Defaults to None.
            mru (int, optional): memory resource. Defaults to None.
            hru (int, optional): hdd resources. Defaults to None.
            currency (str, optional): wanted currency. Defaults to "TFT".
            message (str): message to user. Defaults to ""

        Returns:
            list of available farm objects
        """
        if not farm_names:
            return []
        farms_with_no_resources = []
        nodes_distribution = self._distribute_nodes(number_of_nodes, farm_names)
        for farm_name in nodes_distribution:
            nodes_number = nodes_distribution[farm_name]
            nodes = j.sals.zos.get().nodes_finder.nodes_by_capacity(
                farm_name=farm_name, cru=cru, sru=sru, mru=mru, hru=hru, currency=currency
            )
            nodes = self.filter_nodes(nodes, currency == "FreeTFT")
            if nodes_number > len(nodes):
                farms_with_no_resources.append(farm_name)
        return list(farms_with_no_resources)

    def validate_user(self, user_info):
        """validate user information data to authentication

        Args:
            user_info (dict): user information
        """
        if not j.core.config.get_config().get("threebot_connect", True):
            error_msg = """
            This chatflow is not supported when 3Bot is in dev mode.
            To enable ThreeFold Connect : `j.core.config.set('threebot_connect', True)`
            """
            raise j.exceptions.Runtime(error_msg)
        if not user_info["email"]:
            raise j.exceptions.Value("Email shouldn't be empty")
        if not user_info["username"]:
            raise j.exceptions.Value("Name of logged in user shouldn't be empty")
        return self._explorer.users.get(name=user_info["username"], email=user_info["email"])

    def block_node(self, node_id):
        count = j.core.db.hincrby(NODES_COUNT_KEY, node_id)
        expiration = count * NODES_DISALLOW_EXPIRATION
        node_key = f"{NODES_DISALLOW_PREFIX}:{node_id}"
        j.core.db.set(node_key, j.data.time.utcnow().timestamp + expiration, ex=expiration)

    def unblock_node(self, node_id, reset=True):
        node_key = f"{NODES_DISALLOW_PREFIX}:{node_id}"
        j.core.db.delete(node_key)
        if reset:
            j.core.db.hdel(NODES_COUNT_KEY, node_id)

    def list_blocked_nodes(self):
        """
        each blocked node is stored in a key with a prefix ZOS:NODES:DISALLOWED:{node_id} and its value is the expiration period for it.
        number of failure count is defined in hash with key ZOS:NODES:FAILURE_COUNT. the hash keys are node_ids and values are count of how many times the node has been blocked

        returns
            dict: {node_id: {expiration: .., failure_count: ...}}
        """
        blocked_node_keys = j.core.db.keys(f"{NODES_DISALLOW_PREFIX}:*")
        failure_count_dict = j.core.db.hgetall(NODES_COUNT_KEY)
        blocked_node_values = j.core.db.mget(blocked_node_keys)
        result = {}
        for idx, key in enumerate(blocked_node_keys):
            key = key[len(NODES_DISALLOW_PREFIX) + 1 :]
            node_id = key.decode()
            expiration = int(blocked_node_values[idx])
            failure_count = int(failure_count_dict[key])
            result[node_id] = {"expiration": expiration, "failure_count": failure_count}
        return result

    def clear_blocked_nodes(self):
        blocked_node_keys = j.core.db.keys(f"{NODES_DISALLOW_PREFIX}:*")
        if blocked_node_keys:
            j.core.db.delete(*blocked_node_keys)
        j.core.db.delete(NODES_COUNT_KEY)


reservation_chatflow = ReservationChatflow()
