from .container import Container
from .kubernetes import Kubernetes
from .network import Network
from .node_finder import NodeFinder
from .gateway_finder import GatewayFinder
from .volumes import Volumes
from .zdb import ZDB
from .billing import Billing
from .gateway import Gateway
from jumpscale.data.time import now
from jumpscale.data.serializers.json import dump_to_file, load_from_file, dumps, loads
from jumpscale.data.nacl import payload_build
from jumpscale.loader import j
from jumpscale.clients.explorer.models import TfgridWorkloadsReservation1
from jumpscale.core import identity
import binascii


class Zosv2:
    def __init__(self):
        self._explorer = j.core.identity.me.explorer
        self._nodes_finder = NodeFinder(self._explorer)
        self._gateways_finder = GatewayFinder(self._explorer)
        self._network = Network(self._explorer)
        self._container = Container()
        self._volume = Volumes()
        self._zdb = ZDB(self._explorer)
        self._kubernetes = Kubernetes(self._explorer)
        self._billing = Billing()
        self._gateway = Gateway(self._explorer)

    @property
    def network(self):
        return self._network

    @property
    def container(self):
        return self._container

    @property
    def volume(self):
        return self._volume

    @property
    def zdb(self):
        return self._zdb

    @property
    def kubernetes(self):
        return self._kubernetes

    @property
    def nodes_finder(self):
        return self._nodes_finder

    @property
    def gateways_finder(self):
        return self._gateways_finder

    @property
    def billing(self):
        return self._billing

    def reservation_create(self):
        """Creates a new empty reservation schema

        Returns:
            jumpscale.clients.explorer.models.TfgridWorkloadsReservation1: reservation object
        """
        return self._explorer.reservations.new()

    def reservation_register(
        self, reservation, expiration_date, expiration_provisioning=None, customer_tid=None, currencies=["TFT"]
    ):
        """register a reservation.
           If expiration_provisioning is specified and the reservation is not provisioning before expiration, it will never be provionned.

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation object
            expiration_date (int): timestamp of the date when to expiration should expire
            expiration_provisioning (int, optional): timestamp of the date when to reservation should be provisionned. Defaults to None.
            customer_tid (int, optional): Customer threebot id. Defaults to None.
            currencies (list, optional): list of currency asset code you want pay the reservation with. Defaults to ["TFT"]

        Returns:
            jumpscale.clients.explorer.models.TfgridWorkloadsReservationCreate1: reservation create object
        """
        me = identity.get_identity()
        reservation.customer_tid = me.tid

        if expiration_provisioning is None:
            expiration_provisioning = now().timestamp + (15 * 60)
        dr = reservation.data_reservation
        dr.currencies = currencies

        dr.expiration_provisioning = expiration_provisioning
        dr.expiration_reservation = expiration_date
        dr.signing_request_delete.quorum_min = 0
        dr.signing_request_provision.quorum_min = 0

        # make the reservation cancellable by the user that registered it
        if me.tid not in dr.signing_request_delete.signers:
            dr.signing_request_delete.signers.append(me.tid)
        dr.signing_request_delete.quorum_min = len(dr.signing_request_delete.signers)

        reservation.json = dumps(dr.to_dict())
        reservation.customer_signature = me.nacl.sign_hex(reservation.json.encode()).decode()

        return self._explorer.reservations.create(reservation)

    def reservation_accept(self, reservation):
        """A farmer need to use this function to notify he accepts to deploy the reservation on his node

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation object

        Returns:
            bool: true if succeeded,raise an exception otherwise
        """
        me = identity.get_identity()

        reservation.json = dumps(reservation.data_reservation.to_dict())
        signature = me.nacl.sign_hex(reservation.json.encode())
        # TODO: missing sign_farm
        # return self._explorer.reservations.sign_farmer(reservation.id, me.tid, signature)

    def reservation_result(self, reservation_id):
        """returns the list of workload provisioning results of a reservation

        Args:
            reservation_id (int): reservation ID

        Returns:
            list: list of jumpscale.clients.explorer.models.TfgridWorkloadsReservationResult1
        """
        return self.reservation_get(reservation_id).results

    def reservation_get(self, reservation_id):
        """fetch a specific reservation

        Args:
            reservation_id (int): reservation ID

        Returns:
            jumpscale.clients.explorer.models.TfgridWorkloadsReservation1: reservation object
        """
        return self._explorer.reservations.get(reservation_id)

    def reservation_cancel(self, reservation_id):
        """Cancel a reservation.

           You can only cancel your own reservation
           the 0-OS node then detects it and will decomission the workloads from the reservation

        Args:
            reservation_id (int): reservation ID

        Returns:
            bool: true if the reservation has been cancelled successfully
        """
        me = j.core.identity.me

        reservation = self.reservation_get(reservation_id)
        payload = payload_build(reservation.id, reservation.json.encode())
        payload = str(reservation_id).encode() + payload
        signature = me.nacl.sign_hex(payload)

        return self._explorer.reservations.sign_delete(
            reservation_id=reservation_id, tid=me.tid, signature=signature.decode()
        )

    def reservation_list(self, tid=None, next_action=None):
        """List reservation of a threebot

        Args:
            tid (int, optional): Threebot id. Defaults to None.
            next_action (str, optional): next action. Defaults to None.

        Returns:
            list: list of reservations
        """
        tid = tid or identity.get_identity().tid
        return self._explorer.reservations.list(customer_tid=tid, next_action=next_action)

    def reservation_store(self, reservation, path):
        """Write the reservation on disk.
           Use reservation_load() to load it back

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation object
            path (str): path to write json data to
        """
        dump_to_file(path, reservation.to_dict())

    def reservation_load(self, path):
        """load a reservation stored on disk by reservation_store

        Args:
            path (str): source file

        Returns:
            jumpscale.clients.explorer.models.TfgridWorkloadsReservation1: reservation object
        """
        r = load_from_file(path)
        return TfgridWorkloadsReservation1.from_dict(r)

    def reservation_live(self, expired=False, cancelled=False, identity=None):
        me = identity.get_identity()
        rs = self._explorer.reservations.list()

        current_time = now().timestamp

        for r in rs:
            if r.customer_tid != me.tid:
                continue

            if not expired and r.data_reservation.expiration_reservation < current_time:
                continue

            if not cancelled and str(r.next_action) == "DELETE":
                continue

            print(f"reservation {r.id}")

            wid_res = {result.workload_id: result for result in r.results}

            for c in r.data_reservation.containers:
                result = wid_res.get(c.workload_id)
                if not result:
                    print("container: no result")
                    continue

                data = j.data.serializers.json.loads(result.data)
                print(f"container ip4:{data['ipv4']} ip6{data['ipv6']}")

            for zdb in r.data_reservation.zdbs:
                result = wid_res.get(zdb.workload_id)
                if not result:
                    print("zdb: no result")
                    continue

                data = loads(result.data)

            for network in r.data_reservation.networks:
                result = wid_res.get(network.workload_id)
                if not result:
                    print(f"network name:{network.name}: no result")
                    continue

                print(f"network name:{network.name} iprage:{network.iprange}")

    def reservation_failed(self, reservation):
        """checks if reservation failed

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation object

        Returns:
            bool: True if any result is in error
        """
        return any(map(lambda x: x == "ERROR", [x.state for x in reservation.results]))

    def reservation_ok(self, reservation):
        """checks if reservation succeeded

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation object

        Returns:
            bool: True if all results are ok
        """

        return all(map(lambda x: x == "OK", [x.state for x in reservation.results]))

    def _escrow_to_qrcode(self, escrow_address, escrow_asset, total_amount, message="Grid resources fees"):
        """Converts escrow info to qrcode

        Args:
            escrow_address (str): escrow address
            total_amount (float): total amount of the escrow
            message (str, optional): message encoded in the qr code. Defaults to "Grid resources fees".

        Returns:
            str: qrcode string representation
        """
        qrcode = f"{escrow_asset}:{escrow_address}?amount={total_amount}&message={message}&sender=me"
        return qrcode

    def reservation_escrow_information_with_qrcodes(self, reservation_create_resp):
        """Extracts escrow information from reservation create response as a dict and adds qrcode to it
        Sample output:
        [
        {
            'escrow_address': 'GACMBAK2IWHGNTAG5WOVELJWUTPOXA2QY2Y23PAXNRKOYFTCBWICXNDO',
            'total_amount': 0.586674,
            'farmer_id': 10,
            'qrcode': 'tft:GACMBAK2IWHGNTAG5WOVELJWUTPOXA2QY2Y23PAXNRKOYFTCBWICXNDO?amount=0.586674&message=Grid resources fees for farmer 10&sender=me'
        }
        ]

        Args:
            reservation_create_resp ([type]): reservation create object, returned from reservation_register

        Returns:
            str: escrow encoded for QR code usage
        """
        farmer_payments = []
        escrow_address = reservation_create_resp.escrow_information.address
        escrow_asset = reservation_create_resp.escrow_information.asset
        total_amount = 0
        for detail in reservation_create_resp.escrow_information.details:
            farmer_id = detail.farmer_id
            farmer_amount = detail.total_amount / 10e6

            total_amount += farmer_amount

            farmer_payments.append({"farmer_id": farmer_id, "total_amount": farmer_amount})

        qrcode = self._escrow_to_qrcode(
            escrow_address, escrow_asset.split(":")[0], total_amount, str(reservation_create_resp.reservation_id)
        )

        info = {}
        info["escrow_address"] = escrow_address
        info["escrow_asset"] = escrow_asset
        info["farmer_payments"] = farmer_payments
        info["total_amount"] = total_amount
        info["qrcode"] = qrcode
        info["reservationid"] = reservation_create_resp.reservation_id

        return info
