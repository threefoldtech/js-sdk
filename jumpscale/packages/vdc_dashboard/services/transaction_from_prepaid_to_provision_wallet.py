from jumpscale.loader import j
from jumpscale.packages.vdc.billing import transfer_prepaid_to_provision_wallet
from jumpscale.tools.servicemanager.servicemanager import BackgroundService


class TransferPrepaidToProvisionWallet(BackgroundService):
    def __init__(self, interval=60 * 60, *args, **kwargs):
        """Provisioning wallet service that will run every hour to transfer
        funds from prepaid to provision wallet
        """
        super().__init__(interval, *args, **kwargs)

    def job(self):
        transfer_prepaid_to_provision_wallet()
        j.logger.info("Auto transfer funds from prepad to provision wallet")


service = TransferPrepaidToProvisionWallet()
