import os

from jumpscale.clients.stellar import TRANSACTION_FEES
from jumpscale.loader import j

BASE_CAPACITY = int(os.getenv("BASE_CAPACITY", 14))


def get_vdc_instance():
    if not j.sals.vdc.list_all():
        raise j.exceptions.Value(
            "Billing service couldn't find any vdcs on this machine, Please make sure to have it configured properly"
        )
    vdc_instance_name = list(j.sals.vdc.list_all())[0]
    vdc_instance = j.sals.vdc.find(name=vdc_instance_name, load_info=True)
    if not vdc_instance:
        j.logger.info(f"We couldn't find the VDC instance {vdc_instance}")
        j.tools.alerthandler.alert_raise(
            app_name="get_vdc_instance",
            category="internal_errors",
            message=f"threebot_vdc: couldn't get instance of VDC with name {vdc_instance}",
            alert_type="exception",
        )
    return vdc_instance


def transfer_prepaid_to_provision_wallet():
    """Used to transfer the funds from prepaid wallet to provisioning wallet on an hourly basis"""
    vdc_instance = get_vdc_instance()
    prepaid_wallet = vdc_instance.prepaid_wallet
    provision_wallet = vdc_instance.provision_wallet
    tft = prepaid_wallet._get_asset("TFT")
    hourly_amount = vdc_instance.calculate_spec_price() / (24 * 30)
    j.logger.info(
        f"starting the hourly transaction from prepaid wallet to provision wallet with total hourly amount {hourly_amount}"
    )
    hourly_amount = round(hourly_amount, 6)
    prepaid_wallet.transfer(provision_wallet.address, hourly_amount, asset=f"{tft.code}:{tft.issuer}")


def auto_extend_billing():
    """Is used to get the pool in the VDC and extend them when the remaining time is less than
    half of the BASE_CAPACITY
    """
    # Get the VDC and deployer instances

    vdc_instance = get_vdc_instance()
    deployer = vdc_instance.get_deployer()
    vdc_instance.load_info()

    # Calculating the duration to extend the pool
    remaining_days = (j.data.time.get(vdc_instance.get_pools_expiration()).datetime - j.data.time.now()).days
    days_to_extend = BASE_CAPACITY - remaining_days
    j.logger.info(f"The days to extend {days_to_extend} compared to the base capacity{BASE_CAPACITY}")
    if days_to_extend >= BASE_CAPACITY / 2:
        j.logger.info("starting extending the VDC pools")
        # check if provisioning has enough balance to renew plane
        provision_wallet_balance = vdc_instance._get_wallet_balance(vdc_instance.provision_wallet) - TRANSACTION_FEES
        if provision_wallet_balance <= 0:
            j.logger.critical(f"AUTO_EXTEND_BILLING: VDC {vdc_instance.instance_name}, provisioning wallet is empty")
            return
        days_provisioning_can_fund = provision_wallet_balance / (
            vdc_instance.calculate_active_units_price() * 60 * 60 * 24
        )
        if days_provisioning_can_fund > days_to_extend:
            deployer.renew_plan(duration=days_to_extend)
            j.logger.info(
                f"AUTO_EXTEND_BILLING: VDC {vdc_instance.instance_name} renewed the plan with {days_to_extend} days"
            )
        else:
            deployer.renew_plan(duration=days_provisioning_can_fund)
            j.logger.info(
                f"AUTO_EXTEND_BILLING: VDC {vdc_instance.instance_name} renewed the plan with {days_provisioning_can_fund} days"
            )
