import copy
import time
import json
import datetime
from collections import defaultdict

from jumpscale.clients.explorer.models import NextAction
from jumpscale.loader import j
from jumpscale.sals.chatflows.chatflows import StopChatFlow
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.sals.reservation_chatflow.reservation_chatflow import Network as BaseNetwork
import uuid

MARKET_WALLET_NAME = "TFMarketWallet"


class Network(BaseNetwork):
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
            reservation = self._sal.add_reservation_metadata(reservation, metadata)

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
            return wait_reservation_results
        return True

    def copy(self):
        """create a copy of network object
        Returns:
            (Network): copy of the network
        """
        network_copy = None
        explorer = j.core.identity.me.explorer
        reservation = explorer.reservations.get(self.resv_id)
        networks = self._sal.list_networks(j.core.identity.me.tid)
        for key in networks.keys():
            network, expiration, currency, resv_id = networks[key]
            if network.name == self.name:
                network_copy = Network(network, expiration, self._bot, [reservation], currency, resv_id)
                break
        if network_copy:
            network_copy._used_ips = copy.copy(self._used_ips)
        print("return copy: ", network_copy)
        return network_copy


class MarketPlaceDeployer:
    def __init__(self):
        """This class is responsible for deploying reservations on behalf of the logged-in user for marketplace package
        """
        self.reservations = defaultdict(lambda: defaultdict(list))  # "tid" {"solution_type": []}
        self.wallet = j.clients.stellar.find(MARKET_WALLET_NAME)

    @property
    def _explorer(self):
        return j.core.identity.me.explorer

    def get_solution_metadata(self, solution_name, solution_type, tid, form_info=None, solution_uuid=None):
        """builds the metadata for the reservation

        Args:
            solution_name (str): name choosen by the user. it will be prefixed by {tid}_{solution_name}
            solution_type (SolutionType)
            tid: the id of the user (deploying on his behalf) in explorer
            form_info (dict)

        Returns:
            dict: metadata dict
        """

        form_info = form_info or {}
        metadata = {}
        if not solution_uuid:
            solution_uuid = uuid.uuid4().hex
        metadata["solution_uuid"] = solution_uuid
        metadata["name"] = f"{tid}_{solution_name}"
        metadata["form_info"] = form_info
        metadata["solution_type"] = solution_type.value
        metadata["explorer"] = self._explorer.url
        metadata["tid"] = tid
        return metadata

    def load_user_reservations(self, tid, next_action=NextAction.DEPLOY.value):
        """Loads the reservations made on behalf of the specified user and saves it in-memory in self.reservations[tid]

        Args:
            tid: the id of the user (deploying on his behalf) in explorer
            next_action (int): to be used in filtering the requested reservations. default 3

        Returns:
            list
        """

        reservations = self._explorer.reservations.list(j.core.identity.me.tid, next_action)
        reservations_data = []
        networks = []
        dupnames = {}
        self.reservations.pop(tid, None)
        for reservation in sorted(reservations, key=lambda res: res.id, reverse=True):
            if reservation.metadata:
                try:
                    metadata = j.sals.reservation_chatflow.decrypt_reservation_metadata(reservation.metadata)
                    metadata = j.data.serializers.json.loads(metadata)
                except Exception:
                    continue
                if metadata.get("tid") != tid:
                    continue
                solution_type = metadata.get("solution_type", SolutionType.Unknown.value)
                solution_uuid = metadata.get("solution_uuid")
                if solution_type == SolutionType.Unknown.value:
                    continue
                elif solution_type == SolutionType.Ubuntu.value:
                    metadata = j.sals.reservation_chatflow.get_solution_ubuntu_info(metadata, reservation)
                elif solution_type == SolutionType.Flist.value:
                    metadata = j.sals.reservation_chatflow.get_solution_flist_info(metadata, reservation)
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
                    metadata["form_info"].update(j.sals.reservation_chatflow.get_solution_exposed_info(reservation))
                    metadata["name"] = f'{tid}_{metadata["form_info"]["Domain"]}'
                info = metadata["form_info"]
                name = metadata["name"]
                count = dupnames.setdefault(solution_type, {}).setdefault(name, 1)
                if count != 1:
                    dupnames[solution_type][name] = count + 1
                    name = f"{name}_{count}"
                if solution_type == "minio":
                    if len(reservation.data_reservation.containers) == 0:
                        continue
                reservation_info = {
                    "id": reservation.id,
                    "name": name.split(f"{tid}_")[1],
                    "solution_type": solution_type,
                    "form_info": info,
                    "status": reservation.next_action.name,
                    "reservation_date": reservation.epoch.ctime(),
                    "reservation_obj": reservation,
                    "solution_uuid": solution_uuid,
                }
                reservations_data.append(reservation_info)
                self.reservations[tid][solution_type].append(reservation_info)
        return reservations_data

    def deploy_network(self, tid, network_name, expiration, currency, bot, form_info=None):
        """ deploys a network on behalf of the user driven by a chatflow in one step

        Args:
            tid: the id of the user (deploying on his behalf) in explorer
            network_name (str): name specified by the user. will be prefixed by the tid
            expiration (int): timestamp for network expiration
            currency (str): currency used for the reservation
            bot (GedisChatBot): object of the chatflow
            form_info (dict): to be added to metadata
        """

        if not form_info:
            form_info = {}
        ips = ["IPv6", "IPv4"]
        ipversion = bot.single_choice(
            "How would you like to connect to your network? IPv4 or IPv6? If unsure, choose IPv4", ips, required=True
        )
        farms = j.sals.reservation_chatflow.get_farm_names(1, bot, currency=currency)
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

    def list_solutions(self, tid, solution_type, reload=False, next_action=NextAction.DEPLOY):
        """ list reservations made on behalf a user by type

        Args:
            tid: the id of the user (deploying on his behalf) in explorer
            solution_type (SolutionType): to filter the result with
            reload (bool): if True it will update in-memory reservations from explorer
            next_action (int): to be used in filtering
        """

        if reload or not self.reservations[tid][solution_type.value]:
            self.load_user_reservations(tid, next_action=next_action.value)
        return self.reservations[tid][solution_type.value]

    def get_network_object(self, reservation_obj, bot):
        """builds an object of Network class for the specified

        Args:
            reservation_obj (TfgridWorkloadsReservation1): reseravtion object of the network
            bot (GedisChatBot)

        Returns:
            Network
        """

        reservations = j.sals.zos.reservation_list(tid=j.core.identity.me.tid, next_action="DEPLOY")
        network = reservation_obj.data_reservation.networks[0]
        expiration = reservation_obj.data_reservation.expiration_reservation
        resv_id = reservation_obj.id
        currency = reservation_obj.data_reservation.currencies[0]
        return Network(network, expiration, bot, reservations, currency, resv_id)

    def show_wallet_payment_qrcode(self, resv_id, total_amount, currency, bot):
        """prompts the user for payment to the marketplace wallet

        Args:
            resv_id: id of the reservation to be paid.
            total_amount (float): cost of the reservation
            currency: currency used for the reservation
            bot (GedisChatBot)
        """

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
        """Returns True if user has paid to the marketplace wallet within the specified timeout.

        Args:
            resv_id: reservation id to be paid for
            currency (str): currency used for the reservation
            total_amount (float): cost of the reservation
            timeout (int): number of seconds to wait for the payment

        Returns:
            bool: True if payment was successful within the time limit. False if payment timedout
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

    def register_and_pay_reservation(
        self, reservation, expiration=None, customer_tid=None, currency=None, bot=None, use_wallet=False
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

        if customer_tid and expiration and currency:
            reservation_create = j.sals.reservation_chatflow.register_reservation(
                reservation, expiration, customer_tid=customer_tid, currency=currency, bot=bot
            )
        else:
            reservation_create = reservation

        payment = {"wallet": None, "free": False}
        if not (reservation_create.escrow_information and reservation_create.escrow_information.details):
            payment["free"] = True
        elif use_wallet:
            payment["wallet"] = self.wallet
        else:
            # prompt to pay with 3bot app
            j.sals.reservation_chatflow.show_escrow_qr(
                bot, reservation_create, reservation.data_reservation.expiration_provisioning
            )

        resv_id = reservation_create.reservation_id
        if payment["wallet"]:
            # use MarketPlace wallet
            total_amount = j.sals.zos.billing.get_reservation_amount(reservation_create)
            self.show_wallet_payment_qrcode(resv_id, total_amount, currency, bot)
            if not self._check_payment(resv_id, currency, float(total_amount) + 0.1):
                raise StopChatFlow(f"Payment was unsuccessful. Please make sure you entered the correct data")

            j.sals.zos.billing.payout_farmers(payment["wallet"], reservation_create)
            j.sals.reservation_chatflow.wait_payment(bot, resv_id)

        j.sals.reservation_chatflow.wait_reservation(bot, resv_id)
        return resv_id

    def cancel_solution_by_uuid(self, user_tid, uuid):
        self.load_user_reservations(user_tid)
        ids = []
        for sol_type in self.reservations:
            reservations = self.reservations[sol_type][user_tid]
            for res in reservations:
                if res.get("solution_uuid") == uuid:
                    if res.get("id"):
                        ids.append(res["id"])
        for resv_id in ids:
            j.sals.zos.reservation_cancel(resv_id)

    def cancel_reservation(self, user_tid, resv_id):
        reservation = j.sals.zos.reservation_get(resv_id)
        try:
            metadata = json.loads(j.sals.reservation_chatflow.decrypt_reservation_metadata(reservation.metadata))
        except Exception as e:
            raise j.exceptions.Input(
                "failed to decrypt the reservation metadata. this reservation is not created by marketplace"
            )

        tid = metadata.get("tid")
        if tid == user_tid:
            if metadata.get("solution_type") == SolutionType.Network.value:
                # TODO: comprehensive testing
                curr_network_resv = reservation
                while curr_network_resv:
                    if curr_network_resv.metadata:
                        try:
                            network_metadata = j.sals.reservation_chatflow.decrypt_reservation_metadata(
                                curr_network_resv.metadata
                            )
                            network_metadata = json.loads(network_metadata)
                        except Exception:
                            break
                        j.sals.zos.reservation_cancel(resv_id)
                        if "parent_network" in network_metadata:
                            parent_resv = j.sals.zos.reservation_get(network_metadata["parent_network"])
                            curr_network_resv = parent_resv
                            continue
                    curr_network_resv = None
            else:
                j.sals.zos.reservation_cancel(resv_id)
        else:
            raise j.exceptions.Input(f"this resevration is not owned by the specified user {tid}")


deployer = MarketPlaceDeployer()
