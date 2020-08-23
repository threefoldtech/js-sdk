import binascii

from jumpscale.clients.explorer.conversion import AlreadyConvertedError
from jumpscale.clients.explorer.models import Reservation
from jumpscale.clients.explorer.workloads import Decoder
from jumpscale.core import identity
from jumpscale.loader import j

from .billing import Billing
from .container import ContainerGenerator
from .gateway import GatewayGenerator
from .gateway_finder import GatewayFinder
from .kubernetes import KubernetesGenerator
from .network import NetworkGenerator
from .node_finder import NodeFinder
from .pools import Pools
from .reservation import Reservation
from .signature import sign_workload
from .volumes import VolumesGenerator
from .workloads import Workloads
from .zdb import ZDBGenerator


class Zosv2:
    """ """

    @property
    def _explorer(self):
        return j.core.identity.me.explorer

    @property
    def network(self):
        return NetworkGenerator(self._explorer)

    @property
    def container(self):
        return ContainerGenerator()

    @property
    def volume(self):
        return VolumesGenerator()

    @property
    def zdb(self):
        return ZDBGenerator(self._explorer)

    @property
    def kubernetes(self):
        return KubernetesGenerator(self._explorer)

    @property
    def nodes_finder(self):
        return NodeFinder(self._explorer)

    @property
    def gateways_finder(self):
        return GatewayFinder(self._explorer)

    @property
    def billing(self):
        return Billing()

    @property
    def pools(self):
        return Pools(self._explorer)

    @property
    def workloads(self):
        return Workloads(self._explorer)

    @property
    def gateway(self):
        return GatewayGenerator(self._explorer)

    def conversion(self):
        me = j.core.identity.me

        try:
            raw = self._explorer.conversion.initialize()
        except AlreadyConvertedError as err:
            j.logger.info(str(err))
            return

        if raw:
            for i, data in enumerate(raw):
                w = Decoder.from_dict(datadict=data)
                signature = sign_workload(w, me.nacl.signing_key)
                raw[i]["customer_signature"] = binascii.hexlify(signature).decode()

            self._explorer.conversion.finalize(raw)

    def reservation_create(self):
        """creates a new empty reservation schema

        Args:

        Returns:
          BCDBModel: reservation (tfgrid.workloads.reservation.1)

        """
        return Reservation()

    def reservation_register(self, reservation):
        """provision all the workloads contained in the reservation

        Args:
          reservation(tfgrid.workloads.reservation.1): reservation object

        Returns:
          list[int]: list of workload ID provisionned

        """
        reservation.customer_tid = j.core.identity.me.tid

        ids = []
        for workload in reservation.sorted:
            ids.append(self.workloads.deploy(workload))
        return ids

    def reservation_get(self, reservation_id):
        """fetch a specific reservation

        Args:
          reservation_id(int): reservation ID

        Returns:
          jumpscale.clients.explorer.models.TfgridWorkloadsReservation1: reservation object

        """
        return self._explorer.reservations.get(reservation_id)

    def reservation_list(self, tid=None, next_action=None):
        """List reservation of a threebot

        Args:
          tid(int, optional): Threebot id. Defaults to None.
          next_action(str, optional): next action. Defaults to None.

        Returns:
          list: list of reservations

        """
        tid = tid or identity.get_identity().tid
        return self._explorer.reservations.list(customer_tid=tid, next_action=next_action)

    def _escrow_to_qrcode(self, escrow_address, escrow_asset, total_amount, message="Grid resources fees"):
        """Converts escrow info to qrcode

        Args:
          escrow_address(str): escrow address
          total_amount(float): total amount of the escrow
          message(str, optional): message encoded in the qr code. Defaults to "Grid resources fees".
          escrow_asset:

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
          reservation_create_resp([type]): reservation create object, returned from reservation_register

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
