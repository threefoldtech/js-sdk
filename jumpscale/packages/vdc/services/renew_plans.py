import gevent
from jumpscale.loader import j

from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.sals.vdc.size import INITIAL_RESERVATION_DURATION

RENEW_PLANS_QUEUE = "vdc:plan_renewals"
UNHANDLED_RENEWS = "vdc:plan_renewals:unhandled"


class RenewPlans(BackgroundService):
    def __init__(self, interval=5 * 60, *args, **kwargs):
        """Service to renew plans in the background
        """
        super().__init__(interval, *args, **kwargs)

    def job(self):
        j.logger.info(" ############## Starting Renew Plans Service ############## ")
        while True:
            vdc_name = None
            if j.core.db.llen(UNHANDLED_RENEWS) > 0:
                vdc_name = j.core.db.rpop(UNHANDLED_RENEWS)
            else:
                vdc_name = j.core.db.rpop(RENEW_PLANS_QUEUE)

            if vdc_name:
                vdc_name = vdc_name.decode("utf-8")
                j.logger.info(f"renewing plan for {vdc_name}")
                try:
                    j.core.db.lpush(UNHANDLED_RENEWS, vdc_name)
                    self.init_payment(vdc_name)
                    j.core.db.lrem(UNHANDLED_RENEWS, 0, vdc_name)
                except Exception as e:
                    raise e
            else:
                j.logger.info("Empty Renew plan queue")
                j.logger.info(" ############## End Renew Plans Service ############## ")
                break

            gevent.sleep(1)

    def init_payment(self, vdc_name):
        j.logger.info(f"############################ START INIT_PAYMENT for {vdc_name} ############################")
        vdc = j.sals.vdc.find(vdc_name, load_info=True)
        deployer = vdc.get_deployer()
        amount = vdc.prepaid_wallet.get_balance_by_asset(asset="TFT")

        VDC_INIT_WALLET_NAME = j.config.get("VDC_INITIALIZATION_WALLET", "vdc_init")

        initial_transaction_hashes = deployer.transaction_hashes
        j.logger.debug(f"Transaction hashes:: {initial_transaction_hashes}")

        j.logger.debug("Adding funds to provisioning wallet...")
        try:
            vdc.transfer_to_provisioning_wallet(amount / 2)
        except Exception as e:
            j.logger.error(f"Failed to fund provisioning wallet due to error {str(e)} for vdc: {vdc_name}.")

        j.logger.debug("Paying initialization fee from provisioning wallet")
        try:
            vdc.pay_initialization_fee(initial_transaction_hashes, VDC_INIT_WALLET_NAME)
        except Exception as e:
            j.logger.critical(f"Failed to pay initialization fee due to error {str(e)} for vdc: {vdc_name} ")

        deployer._set_wallet(vdc.provision_wallet.instance_name)

        j.logger.debug("Funding difference from init wallet...")
        vdc.fund_difference(VDC_INIT_WALLET_NAME)

        j.logger.debug("Updating expiration...")
        deployer.renew_plan(14 - INITIAL_RESERVATION_DURATION / 24)
        j.logger.info(f"############################ END INIT_PAYMENT for {vdc_name} ############################")


service = RenewPlans()
