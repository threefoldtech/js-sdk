import base64
import copy
import math
import time
import requests
import json
import datetime
from collections import defaultdict

import netaddr
from nacl.public import Box

from jumpscale.clients.explorer.models import DiskType, NextAction, TfgridDeployed_reservation1
from jumpscale.clients.stellar.stellar import _NETWORK_KNOWN_TRUSTS
from jumpscale.core.base import StoredFactory
from jumpscale.god import j
from jumpscale.sals.chatflows.chatflows import GedisChatBot, StopChatFlow, chatflow_step
from jumpscale.sals.reservation_chatflow.models import SolutionType

# from jumpscale.sals.reservation_chatflow.reservation_chatflow import Network


MARKET_WALLET_NAME = "TFMarketWallet"


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
            j.sals.zos.network.add_node(self._network, node.node_id, str(subnet))
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
            reservation = j.sals.zos.reservation_create()
            reservation.data_reservation.networks.append(self._network)
            form_info = {
                "chatflow": "network",
                "Currency": self.currency,
                "Solution expiration": self._expiration.timestamp(),
            }
            metadata = deployer.get_solution_metadata(
                self.name.split(f"{tid}_")[1], SolutionType.Network, tid, form_info=form_info
            )

            metadata["parent_network"] = self.resv_id
            reservation = deployer.add_reservation_metadata(reservation, metadata)

            reservation_create = self._sal.register_reservation(
                reservation, self._expiration.timestamp(), j.core.identity.me.tid, currency=currency, bot=bot
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
                    bot, rid, threebot_app=True, reservation_create_resp=reservation_create
                )
            wait_reservation_results = self._sal.wait_reservation(self._bot, rid)
            # Update solution saved locally
            explorer_name = self._sal._explorer.url.split(".")[1]
            return wait_reservation_results
        return True

    def copy(self):
        """create a copy of network object


        Returns:
            (Network): copy of the network
        """
        network_copy = None
        explorer = j.clients.explorer.get_default()
        reservation = explorer.reservations.get(self.resv_id)
        networks = self._sal.list_networks(j.core.identity.me.tid, [reservation])
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


class MarketPlaceDeployer:
    def __init__(self):
        self._explorer = j.clients.explorer.get_default()
        self.reservations = defaultdict(lambda: defaultdict(list))  # "tid" {"solution_type"}
        self.wallet = j.clients.stellar.find(MARKET_WALLET_NAME)

    def add_reservation_metadata(self, reservation, metadata):
        meta_json = j.data.serializers.json.dumps(metadata)

        pk = j.core.identity.me.nacl.signing_key.verify_key.to_curve25519_public_key()
        sk = j.core.identity.me.nacl.signing_key.to_curve25519_private_key()
        box = Box(sk, pk)
        encrypted_metadata = base64.b85encode(box.encrypt(meta_json.encode())).decode()
        reservation.metadata = encrypted_metadata
        return reservation

    def get_solution_metadata(self, solution_name, solution_type, tid, form_info=None):
        form_info = form_info or {}
        metadata = {}
        metadata["name"] = f"{tid}_{solution_name}"
        metadata["form_info"] = form_info
        metadata["solution_type"] = solution_type.value
        metadata["explorer"] = self._explorer.url
        metadata["tid"] = tid
        return metadata

    def decrypt_reservation_metadata(self, metadata_encrypted):
        pk = j.core.identity.me.nacl.signing_key.verify_key.to_curve25519_public_key()
        sk = j.core.identity.me.nacl.signing_key.to_curve25519_private_key()
        box = Box(sk, pk)
        return box.decrypt(base64.b85decode(metadata_encrypted.encode())).decode()

    def load_user_reservations(self, tid, next_action=NextAction.DEPLOY.value):
        reservations = self._explorer.reservations.list(j.core.identity.me.tid, next_action)
        reservations_data = []
        networks = []
        dupnames = {}
        self.reservations.pop(tid, None)
        for reservation in sorted(reservations, key=lambda res: res.id, reverse=True):
            if reservation.metadata:
                try:
                    metadata = self.decrypt_reservation_metadata(reservation.metadata)
                    metadata = j.data.serializers.json.loads(metadata)
                except Exception:
                    continue
                if metadata.get("tid") != tid:
                    continue
                solution_type = metadata.get("solution_type", SolutionType.Unknown.value)
                if solution_type == SolutionType.Unknown.value:
                    continue
                elif solution_type == SolutionType.Ubuntu.value:
                    metadata = self.get_solution_ubuntu_info(metadata, reservation)
                elif solution_type == SolutionType.Flist.value:
                    metadata = self.get_solution_flist_info(metadata, reservation)
                elif solution_type == SolutionType.Network.value:
                    if not metadata["name"]:
                        metadata["name"] = reservation.data_reservation.networks[0].name
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
                    metadata["name"] = f'{tid}_{metadata["form_info"]["Domain"]}'
                info = metadata["form_info"]
                name = metadata["name"]
                count = dupnames.setdefault(solution_type, {}).setdefault(name, 1)
                if count != 1:
                    dupnames[solution_type][name] = count + 1
                    name = f"{name}_{count}"
                reservation_info = {
                    "id": reservation.id,
                    "name": name.split(f"{tid}_")[1],
                    "solution_type": solution_type,
                    "form_info": info,
                    "status": reservation.next_action.name,
                    "reservation_date": reservation.epoch.ctime(),
                    "reservation_obj": reservation,
                }
                reservations_data.append(reservation_info)
                self.reservations[tid][solution_type].append(reservation_info)
        return reservations_data

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

    def deploy_network(self, tid, network_name, expiration, currency, bot, form_info=None):
        if not form_info:
            form_info = {}
        ips = ["IPv6", "IPv4"]
        ipversion = bot.single_choice(
            "How would you like to connect to your network? IPv4 or IPv6? If unsure, choose IPv4", ips, required=True
        )
        farms = j.sals.reservation_chatflow.get_farm_names(1, bot)
        access_node = j.sals.reservation_chatflow.get_nodes(
            1, farm_names=farms, currency=currency, ip_version=ipversion
        )[0]
        ip_range = j.sals.reservation_chatflow.get_ip_range(bot)
        form_info["IP Range"] = ip_range
        reservation = j.sals.zos.reservation_create()
        res = self.get_solution_metadata(network_name, SolutionType.Network, tid, form_info)
        reservation = j.sals.reservation_chatflow.add_reservation_metadata(reservation, res)

        while True:
            config = j.sals.reservation_chatflow.create_network(
                f"{tid}_{network_name}",
                reservation,
                ip_range,
                j.core.identity.me.tid,
                ipversion,
                access_node,
                expiration=expiration,
                currency=currency,
                bot=bot,
            )
            try:
                j.sals.reservation_chatflow.register_and_pay_reservation(config["reservation_create"], bot=bot)
                break
            except StopChatFlow as e:
                if "wireguard listen port already in use" in e.msg:
                    j.sals.zos.reservation_cancel(config["rid"])
                    time.sleep(5)
                    continue
                raise
        message = """
### Use the following template to configure your wireguard connection. This will give you access to your network.
#### Make sure you have <a target="_blank" href="https://www.wireguard.com/install/">wireguard</a> installed
Click next
to download your configuration
        """

        bot.md_show(message, md=True, html=True)

        filename = "wg-{}.conf".format(config["rid"])
        bot.download_file(msg=f'<pre>{config["wg"]}</pre>', data=config["wg"], filename=filename, html=True)

        message = f"""
### In order to have the network active and accessible from your local/container machine. To do this, execute this command:
#### ```wg-quick up /etc/wireguard/{filename}```
# Click next
        """

        bot.md_show(message, md=True)

    def validate_user(self, user_info):
        if not user_info["email"]:
            raise j.exceptions.Value("Email shouldn't be empty")
        if not user_info["username"]:
            raise j.exceptions.Value("Name of logged in user shouldn't be empty")
        return self._explorer.users.get(name=user_info["username"], email=user_info["email"])

    def list_solutions(self, tid, solution_type, reload=False, next_action=NextAction.DEPLOY):
        if reload or not self.reservations[tid][solution_type.value]:
            self.load_user_reservations(tid, next_action=next_action.value)
        return self.reservations[tid][solution_type.value]

    def get_network_object(self, reservation_obj, bot):
        reservations = j.sals.zos.reservation_list(tid=j.core.identity.me.tid, next_action="DEPLOY")
        network = reservation_obj.data_reservation.networks[0]
        expiration = reservation_obj.data_reservation.expiration_reservation
        resv_id = reservation_obj.id
        currency = reservation_obj.data_reservation.currencies[0]
        return Network(network, expiration, bot, reservations, currency, resv_id)

    def show_payment_qrcode(self, resv_id, total_amount, currency, bot):
        qr_code_content = j.sals.zos._escrow_to_qrcode(
            escrow_address=self.wallet.address, escrow_asset=currency, total_amount=total_amount, message=f"{resv_id}"
        )
        message_text = f"""
            <h3> Please make your payment </h3>
            Scan the QR code with your application (do not change the message) or enter the information below manually and proceed with the payment.
            Make sure to add the message (reservation id) as memo_text
            Please make the transaction and press Next
            <h4> Wallet address: </h4>  {self.wallet.address} \n
            <h4> Currency: </h4>  {currency} \n
            <h4> Amount: </h4>  {total_amount} \n
            <h4> Message (Reservation ID): </h4>  {resv_id} \n
        """
        bot.qrcode_show(data=qr_code_content, msg=message_text, scale=4, update=True, html=True)

    def _check_payment(self, resv_id, currency, total_amount, timeout=300):
        """Returns True if user has paied alaready, False if not
        """
        now = datetime.datetime.now()
        effects_sum = 0
        while now + datetime.timedelta(seconds=timeout) > datetime.datetime.now():
            transactions = self.wallet.list_transactions()
            for transaction in transactions:
                if transaction.memo_text == f"{resv_id}":
                    effects = self.wallet.get_transaction_effects(transaction.hash)
                    for e in effects:
                        if e.asset_code == currency:
                            effects_sum += e.amount
            if effects_sum >= total_amount:
                return True
        return False

    def register_reservation(
        self, reservation, expiration, customer_tid, expiration_provisioning=1000, currency=None, bot=None
    ):
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
        return reservation_create

    def register_and_pay_reservation(self, reservation, expiration=None, customer_tid=None, currency=None, bot=None):
        if customer_tid and expiration and currency:
            reservation_create = self.register_reservation(
                reservation, expiration, customer_tid=customer_tid, currency=currency, bot=bot
            )
        else:
            reservation_create = reservation

        payment = {"wallet": None, "free": False}
        if not (reservation_create.escrow_information and reservation_create.escrow_information.details):
            payment["free"] = True
        else:
            payment["wallet"] = self.wallet

        resv_id = reservation_create.reservation_id
        if payment["wallet"]:
            total_amount = j.sals.zos.billing.get_reservation_amount(reservation_create)
            self.show_payment_qrcode(resv_id, total_amount, currency, bot)
            if not self._check_payment(resv_id, currency, float(total_amount) + 0.1):
                raise StopChatFlow(f"Payment was unsuccessful. Please make sure you entered the correct data")

            j.sals.zos.billing.payout_farmers(payment["wallet"], reservation_create)
            self.wait_payment(bot, resv_id)

        self.wait_reservation(bot, resv_id)
        return resv_id

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
# Deploying...\n
Deployment will be cancelled if it is not successful {remaning_time}
"""
            bot.md_show_update(deploying_message, md=True)
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
                j.sals.zos.reservation_cancel(rid)
                bot.stop(res, md=True, html=True)
            time.sleep(1)
            reservation = self._explorer.reservations.get(rid)

    def wait_payment(self, bot, rid, reservation_create_resp=None):
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


deployer = MarketPlaceDeployer()


class MarketPlaceChatflow(GedisChatBot):
    SOLUTION_TYPE = None

    def get_tid(self):
        user = deployer.validate_user(self.user_info())
        return user.id

    @chatflow_step(title="Welcome")
    def welcome(self):
        self.user_form_data = dict()
        self.metadata = dict()
        self.query = dict()
        self.env = dict()
        self.secret_env = dict()
        self.md_show(f"### Welcome to {self.SOLUTION_TYPE.value} chatflow. click next to proceed to the deployment")

    @chatflow_step(title="Solution name")
    def solution_name(self):
        self.name = self.string_ask("Please enter a name for your solution", required=True)
        self.user_form_data["Solution name"] = self.name

    @chatflow_step(title="Expiration time")
    def expiration_time(self):
        self.expiration = self.datetime_picker(
            "Please enter solution expiration time.",
            required=True,
            min_time=[3600, "Date/time should be at least 1 hour from now"],
            default=j.data.time.get().timestamp + 3900,
        )
        self.user_form_data["Solution expiration"] = j.data.time.get(self.expiration).humanize()
        self.metadata["Solution expiration"] = self.user_form_data["Solution expiration"]

    @chatflow_step(title="Currency")
    def choose_currency(self):
        self.currency = self.single_choice(
            "Please choose a currency that will be used for the payment",
            ["FreeTFT", "TFTA", "TFT"],
            default="TFT",
            required=True,
        )
        self.user_form_data["currency"] = self.currency

    @chatflow_step(title="Container Resources")
    def container_resources(self):
        form = self.new_form()
        cpu = form.int_ask("Please add how many CPU cores are needed", default=1, required=True)
        memory = form.int_ask("Please add the amount of memory in MB", default=1024, required=True)

        self.rootfs_size = form.int_ask("Choose the amount of storage for your root filesystem in MiB", default=256)
        form.ask()
        self.user_form_data["CPU"] = cpu.value
        self.user_form_data["Memory"] = memory.value
        self.user_form_data["Root filesystem Type"] = DiskType.SSD.name
        self.user_form_data["Root filesystem Size"] = self.rootfs_size.value
        self.query["mru"] = math.ceil(self.user_form_data["Memory"] / 1024)
        self.query["cru"] = self.user_form_data["CPU"]
        storage_units = math.ceil(self.rootfs_size.value / 1024)
        self.query["sru"] = storage_units
        self.query["currency"] = self.currency

    @chatflow_step(title="Access keys")
    def public_key_get(self):
        self.user_form_data["Public key"] = self.upload_file(
            """Please add your public ssh key, this will allow you to access the deployed container using ssh.
                    Just upload the file with the key""",
            required=True,
        ).split("\n")[0]
        self.env["pub_key"] = self.user_form_data["Public key"]

    @chatflow_step(title="Container node id")
    def container_node_id(self):
        # create new reservation
        self.nodeid = self.string_ask(
            "Please enter the nodeid you would like to deploy on if left empty a node will be chosen for you"
        )
        while self.nodeid:
            try:
                self.node_selected = j.sals.reservation_chatflow.validate_node(
                    self.nodeid, self.query, self.network.currency
                )
                break
            except (j.exceptions.Value, j.exceptions.NotFound) as e:
                message = "<br> Please enter a different nodeid to deploy on or leave it empty"
                self.nodeid = self.string_ask(str(e) + message, html=True, retry=True)
        self.query["currency"] = self.currency

    @chatflow_step(title="Container farm")
    def container_farm(self):
        if not hasattr(self, "nodeid"):
            self.nodeid = None
        if not self.nodeid:
            if not self.query:
                self.query["mru"] = math.ceil(self.user_form_data["Memory"] / 1024)
                self.query["cru"] = self.user_form_data["CPU"]

                storage_units = math.ceil(self.rootfs_size.value / 1024)
                self.query["sru"] = storage_units
            farms = j.sals.reservation_chatflow.get_farm_names(1, self, **self.query)
            self.node_selected = j.sals.reservation_chatflow.get_nodes(1, farm_names=farms, **self.query)[0]

    @chatflow_step(title="Container IP")
    def container_ip(self):
        self.network_copy = self.network.copy()
        self.network_copy.add_node(self.node_selected)
        self.ip_address = self.network_copy.ask_ip_from_node(
            self.node_selected, "Please choose IP Address for your solution"
        )
        self.user_form_data["IP Address"] = self.ip_address

    @chatflow_step(title="Confirmation")
    def overview(self):
        self.md_show_confirm(self.user_form_data)

    @chatflow_step(title="Container logs")
    def container_logs(self):
        self.container_logs_option = self.single_choice(
            "Do you want to push the container logs (stdout and stderr) onto an external redis channel",
            ["YES", "NO"],
            default="NO",
        )
        if self.container_logs_option == "YES":
            form = self.new_form()
            self.channel_type = form.string_ask("Please add the channel type", default="redis", required=True)
            self.channel_host = form.string_ask(
                "Please add the IP address where the logs will be output to", required=True
            )
            self.channel_port = form.int_ask(
                "Please add the port available where the logs will be output to", required=True
            )
            self.channel_name = form.string_ask(
                "Please add the channel name to be used. The channels will be in the form NAME-stdout and NAME-stderr",
                default=self.user_form_data["Solution name"],
                required=True,
            )
            form.ask()
            self.user_form_data["Logs Channel type"] = self.channel_type.value
            self.user_form_data["Logs Channel host"] = self.channel_host.value
            self.user_form_data["Logs Channel port"] = self.channel_port.value
            self.user_form_data["Logs Channel name"] = self.channel_name.value

    @chatflow_step(title="Choose Network")
    def choose_network(self):
        self.tid = self.get_tid()
        networks_data = deployer.list_solutions(self.tid, SolutionType.Network, reload=True)
        if not networks_data:
            StopChatFlow("You don't have any available networks yet. please create a newtork first")
        network_names = []
        networks_dict = {}
        for net in networks_data:
            network_names.append(net["name"])
            networks_dict[net["name"]] = net
        network_name = self.single_choice(
            "Please choose the network you want to connect your container to", network_names, required=True
        )
        self.user_form_data["Network Name"] = network_name
        network_reservation = networks_dict[network_name]
        self.network = deployer.get_network_object(network_reservation["reservation_obj"], self)
        self.currency = self.network.currency

    @chatflow_step(title="Payment", disable_previous=True)
    def container_pay(self):
        self.reservation = j.sals.zos.reservation_create()
        if not hasattr(self, "container_volume_attach"):
            self.container_volume_attach = False
        if not hasattr(self, "interactive"):
            self.interactive = False
        if not hasattr(self, "entry_point"):
            self.entry_point = None

        self.network = self.network_copy
        self.network.update(self.get_tid(), currency=self.currency, bot=self)
        storage_url = "zdb://hub.grid.tf:9900"

        # create container
        cont = j.sals.zos.container.create(
            reservation=self.reservation,
            node_id=self.node_selected.node_id,
            network_name=self.network.name,
            ip_address=self.ip_address,
            flist=self.flist_url,
            storage_url=storage_url,
            disk_type=DiskType.SSD.value,
            disk_size=self.rootfs_size.value,
            env=self.env,
            secret_env=self.secret_env,
            interactive=self.interactive,
            entrypoint=self.entry_point,
            cpu=self.user_form_data["CPU"],
            memory=self.user_form_data["Memory"],
        )
        if self.container_logs_option == "YES":
            j.sals.zos.container.add_logs(
                cont,
                channel_type=self.user_form_data["Logs Channel type"],
                channel_host=self.user_form_data["Logs Channel host"],
                channel_port=self.user_form_data["Logs Channel port"],
                channel_name=self.user_form_data["Logs Channel name"],
            )
        if self.container_volume_attach:
            self.volume = j.sals.zos.volume.create(
                self.reservation,
                self.node.node_id,
                size=self.user_form_data["Volume Size"],
                type=self.vol_disk_type.value,
            )
            j.sals.zos.volume.attach(
                container=cont, volume=self.volume, mount_point=self.user_form_data["Volume mount point"]
            )

        res = deployer.get_solution_metadata(
            self.user_form_data["Solution name"], self.SOLUTION_TYPE, self.tid, self.metadata
        )
        reservation = deployer.add_reservation_metadata(self.reservation, res)
        self.resv_id = deployer.register_and_pay_reservation(
            reservation, self.expiration, customer_tid=j.core.identity.me.tid, currency=self.currency, bot=self
        )

    @chatflow_step(title="Attach Volume")
    def container_volume(self):
        volume_attach = self.drop_down_choice(
            "Would you like to attach an extra volume to the container", ["YES", "NO"], required=True, default="NO"
        )
        self.container_volume_attach = volume_attach == "YES" or False

    @chatflow_step(title="Volume details")
    def container_volume_details(self):
        if self.container_volume_attach:
            form = self.new_form()
            vol_disk_size = form.int_ask("Please specify the volume size", required=True, default=10)
            vol_mount_point = form.string_ask("Please enter the mount point", required=True, default="/data")
            form.ask()
            self.vol_disk_size = vol_disk_size
            self.vol_disk_type = DiskType.SSD
            self.user_form_data["Volume Disk type"] = DiskType.SSD.name
            self.user_form_data["Volume Size"] = vol_disk_size.value
            self.user_form_data["Volume mount point"] = vol_mount_point.value

    @chatflow_step(title="Environment variables")
    def container_env(self):
        self.user_form_data["Env variables"] = self.multi_values_ask("Set Environment Variables")
        self.env.update(self.user_form_data["Env variables"])

    @chatflow_step(title="Container ineractive & EntryPoint")
    def container_interactive(self):
        self.user_form_data["Interactive"] = self.single_choice(
            "Would you like access to your container through the web browser (coreX)?", ["YES", "NO"], required=True
        )
        if self.user_form_data["Interactive"] == "NO":
            self.interactive = False
            self.user_form_data["Entry point"] = self.string_ask("Please add your entrypoint for your flist") or ""
        else:
            self.interactive = True
            self.user_form_data["Port"] = "7681"
            self.user_form_data["Entry point"] = ""
