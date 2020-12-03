import os
from decimal import Decimal
from jumpscale.loader import j


PROVISION_WALLET_NAME = os.getenv("PROVISION_WALLET")
ORIGINAL_USER_PLAN_TFT = os.getenv("ORIGINAL_USER_PLAN_TFT")
BASE_CAPACITY = os.getenv("BASE_CAPACITY")
PREPAID_WALLET = os.getenv("PREPAID_WALLET")


def get_addon_price(addon):
    # TODO: Get the addon_price
    return 0


def calculate_addons_hourly_rate():
    vdc_instance_name = os.getenv("VDC_INSTANCE_NAME")
    vdc_instance = j.sals.vdc.get(vdc_instance_name)
    addons = vdc_instance.addons
    total_price = 0
    # Calculate all the hourly late for all addons
    for addon_name, addon_amount in addons:
        addon_price = get_addon_price(addon_name)
        total_price += (addon_price / (24 * 30)) * addon_amount
    return total_price


def calculate_hourly_rate():
    hourly_amount = ORIGINAL_USER_PLAN_TFT / (24 * 30)
    hourly_amount += calculate_addons_hourly_rate()
    return hourly_amount


def tranfer_prepaid_to_provision_wallet():
    prepaid_wallet = j.clients.stellar.get(PREPAID_WALLET)
    provision_wallet = j.clients.stellar.get(PROVISION_WALLET_NAME)
    tft = prepaid_wallet.get_asset("TFT")
    hourly_amount = calculate_hourly_rate()
    prepaid_wallet.transfer(provision_wallet.address, hourly_amount, asset=f"{tft.code}:{tft.issuer}")


def auto_extend_billing():
    # TODO: get the VDC pool
    vdc_instance_name = os.getenv("VDC_INSTANCE_NAME")
    vdc_password = os.getenv("VDC_PASSWORD")
    vdc_instance = j.sals.vdc.get(vdc_instance_name)
    deployer = vdc_instance.get_deployer(vdc_password)

    # Calculating the duration to extend the pool
    remaining_days = (vdc_instance.expiration - j.data.time.now()).days
    days_to_extend = BASE_CAPACITY - remaining_days
    if days_to_extend >= BASE_CAPACITY / 2:
        deployer.renew_plan(duration=days_to_extend)
