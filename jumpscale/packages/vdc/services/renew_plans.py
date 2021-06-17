import gevent
from jumpscale.loader import j
from enum import Enum

from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.sals.vdc.size import INITIAL_RESERVATION_DURATION
from jumpscale.sals.vdc.vdc import VDCSTATE
from jumpscale.clients.stellar import TRANSACTION_FEES

RENEW_PLANS_QUEUE = "vdc:plan_renewals"
UNHANDLED_RENEWS = "vdc:plan_renewals:unhandled"
VCD_DEPLOYING_INSTANCES = "VCD_DEPLOYING_INSTANCES"
ONE_HOUR = 60 * 60
VDC_INIT_WALLET_NAME = j.config.get("VDC_INITIALIZATION_WALLET", "vdc_init")


class PAYMENTSTATE(Enum):
    NEW = "NEW"
    FUND_PROVISION = "FUND_PROVISION"
    INIT_FEE = "INIT_FEE"
    FUND_DIFF = "FUND_DIFF"
    PAID = "PAID"


class RenewPlans(BackgroundService):
    def __init__(self, interval=5 * 60, *args, **kwargs):
        """Service to renew plans in the background
        """
        self.payment_info = None
        super().__init__(interval, *args, **kwargs)

    @property
    def payment_phase(self):
        return self.payment_info.get("payment_phase")

    def job(self):
        j.logger.info("Starting Renew Plans Service")
        queues_length = j.core.db.llen(RENEW_PLANS_QUEUE) + j.core.db.llen(UNHANDLED_RENEWS)
        for _ in range(queues_length):
            payment_data = j.core.db.rpop(RENEW_PLANS_QUEUE) or j.core.db.rpop(UNHANDLED_RENEWS)

            if payment_data:
                self.payment_info = j.data.serializers.json.loads(payment_data)
                vdc_name = self.payment_info.get("vdc_instance_name")
                vdc_created_at = self.payment_info.get("created_at")

                if j.data.time.now().timestamp - vdc_created_at > ONE_HOUR:
                    j.logger.debug(f"Refund VDC {vdc_name}")
                    try:
                        self.refund_rollback()
                    except Exception as e:  # Push back element in case the refund fail
                        payment_data = j.data.serializers.json.dumps(self.payment_info)  # To get latest payment info
                        j.core.db.lpush(UNHANDLED_RENEWS, payment_data)
                        j.logger.error(f"Failed to refund {vdc_name}, will try again.\nFor details:{str(e)}")
                else:
                    j.logger.info(f"renewing plan for {vdc_name}")
                    try:
                        self.init_payment()
                    except Exception as e:  # Push back element in case the refund fail
                        payment_data = j.data.serializers.json.dumps(self.payment_info)  # To get latest payment info
                        j.core.db.lpush(UNHANDLED_RENEWS, payment_data)
                        j.logger.error(
                            f"Failed to complete payment for {vdc_name}, last successful step: {self.payment_info.get('payment_phase')}\nFor details:{str(e)}"
                        )

            gevent.sleep(1)

        j.logger.info("End Renew Plans Service")

    def init_payment(self):
        vdc_name = self.payment_info.get("vdc_instance_name")

        j.logger.info(f"START INIT_PAYMENT for {vdc_name}")
        vdc = j.sals.vdc.find(vdc_name, load_info=True)
        deployer = vdc.get_deployer()
        amount = vdc.prepaid_wallet.get_balance_by_asset(asset="TFT")

        initial_transaction_hashes = vdc.transaction_hashes
        j.logger.debug(f"Transaction hashes:: {initial_transaction_hashes}")

        if self.payment_phase == PAYMENTSTATE.NEW.value:
            j.logger.debug("Adding funds to provisioning wallet...")
            vdc.transfer_to_provisioning_wallet(amount / 2)
            self._change_payment_phase(PAYMENTSTATE.FUND_PROVISION.value)

        if self.payment_phase == PAYMENTSTATE.FUND_PROVISION.value:
            j.logger.debug("Paying initialization fee from provisioning wallet")
            vdc.pay_initialization_fee(initial_transaction_hashes, VDC_INIT_WALLET_NAME)
            self._change_payment_phase(PAYMENTSTATE.INIT_FEE.value)

        j.logger.debug("Funding difference from init wallet...")
        if self.payment_phase == PAYMENTSTATE.INIT_FEE.value:
            vdc.fund_difference(VDC_INIT_WALLET_NAME)
            self._change_payment_phase(PAYMENTSTATE.FUND_DIFF.value)

        if self.payment_phase == PAYMENTSTATE.FUND_DIFF.value:
            j.logger.debug("Updating expiration...")
            deployer._set_wallet(vdc.provision_wallet.instance_name)
            deployer.renew_plan(14 - INITIAL_RESERVATION_DURATION / 24)
            self._change_payment_phase(PAYMENTSTATE.PAID.value)
            vdc.state = VDCSTATE.VERIFIED
            vdc.save()
            j.logger.info(f"END INIT_PAYMENT for {vdc_name}")

    def refund_rollback(self):
        vdc_name = self.payment_info.get("vdc_instance_name")
        payment_id = self.payment_info.get("payment_id")

        vdc = j.sals.vdc.get(vdc_name)
        provision_wallet_amount = vdc.provision_wallet.get_balance_by_asset(asset="TFT") - TRANSACTION_FEES
        prepaid_wallet_amount = vdc.prepaid_wallet.get_balance_by_asset(asset="TFT")
        asset = vdc.prepaid_wallet._get_asset(code="TFT")
        vdc_init_wallet = j.clients.stellar.get(VDC_INIT_WALLET_NAME)

        if self.payment_phase == PAYMENTSTATE.FUND_DIFF.value:
            diff = provision_wallet_amount - prepaid_wallet_amount
            if diff > 0:
                vdc.provision_wallet.transfer(vdc_init_wallet.address, diff, asset=f"{asset.code}:{asset.issuer}")
                provision_wallet_amount = vdc.provision_wallet.get_balance_by_asset(asset="TFT") - TRANSACTION_FEES
                self._change_payment_phase(PAYMENTSTATE.FUND_PROVISION.value)  # Update to required state

        if self.payment_phase == PAYMENTSTATE.INIT_FEE.value:
            init_fee_amount = vdc._calculate_initialization_fee(vdc.transaction_hashes, vdc_init_wallet)
            vdc_init_wallet.transfer(vdc.prepaid_wallet.address, init_fee_amount, asset=f"{asset.code}:{asset.issuer}")
            self._change_payment_phase(PAYMENTSTATE.FUND_PROVISION.value)  # Update to required state

        if self.payment_phase in [
            PAYMENTSTATE.FUND_PROVISION.value,
            PAYMENTSTATE.INIT_FEE.value,
            PAYMENTSTATE.FUND_DIFF.value,
        ]:
            vdc.provision_wallet.transfer(
                vdc.prepaid_wallet.address, provision_wallet_amount, asset=f"{asset.code}:{asset.issuer}"
            )
            vdc_init_wallet.transfer(
                vdc.prepaid_wallet.address, 2 * TRANSACTION_FEES, asset=f"{asset.code}:{asset.issuer}"
            )
            self._change_payment_phase(PAYMENTSTATE.NEW.value)  # Update to required state

        j.sals.billing.issue_refund(payment_id)
        j.sals.vdc.cleanup_vdc(vdc)
        j.core.db.hdel(VCD_DEPLOYING_INSTANCES, vdc_name)
        vdc.state = VDCSTATE.EMPTY
        vdc.save()

    def _change_payment_phase(self, phase):
        self.payment_info["payment_phase"] = phase


service = RenewPlans()
