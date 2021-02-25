import os
import requests
from jumpscale.loader import j
from jumpscale.sals.vdc.size import VDC_SIZE, FARM_DISCOUNT
from jumpscale.sals.vdc.models import KubernetesRole


BASE_CAPACITY = int(os.getenv("BASE_CAPACITY", 14))


def get_vdc_instance():
    vdc_instance_name = list(j.sals.vdc.list_all())[0]
    vdc_instance = j.sals.vdc.find(name=vdc_instance_name, load_info=True)
    if not vdc_instance:
        j.logger.info(f"We couldn't find the VDC instance {vdc_instance}")
        j.tools.alerthandler.alert_raise(
            app_name="get_vdc_instance",
            category="internal_errors",
            message=f"threebot_vdc: couldn't get instance of VDC with name {vdc_instance} due to error: {str(e)}",
            alert_type="exception",
        )
    return vdc_instance


def get_addons(flavor, kubernetes_addons):
    """Get all the addons on the basic user plan

    Args:
        flavor(str): user flavor for the plan
        kubernetes_addons(list): all kubernetes nodes

    Returns:
        addons(list): list of addons used by the user over the basic chosen plan

    """
    plan = VDC_SIZE.VDC_FLAVORS.get(flavor)
    plan_nodes_count = plan.get("k8s").get("no_nodes")
    plan_nodes_size = plan.get("k8s").get("size")
    addons = list()
    for addon in kubernetes_addons:
        if addon.role != KubernetesRole.MASTER:
            if addon.size == plan_nodes_size:
                plan_nodes_count -= 1
                if plan_nodes_count < 0:
                    addons.append(addon)
            else:
                addons.append(addon)
    return addons


def get_prices():
    """Get the prices of the addons and plans from github
    Returns:
        VDC_PRICES(dict): return VDC_prices dictionary form out config
    """
    # Store prices from github
    if not j.config.get("VDC_PRICES"):
        prices = requests.get(
            "https://raw.githubusercontent.com/threefoldfoundation/vdc_pricing/master/prices.json"
        ).json()
        j.config.set("VDC_PRICES", prices)
    return j.config.get("VDC_PRICES")


def calculate_addon_price(addon):
    """Calculate the price of a single addon
    Args:
        addon(obj): addon object
    Returns:
       price(float): addon price
    """
    prices = get_prices()
    size = addon.size.name.lower()
    return prices["nodes"][size]


def calculate_plan_base_price():
    """Get user plan price
    Returns:
       price(float): the price of user plan
    """
    vdc_instance = get_vdc_instance()
    prices = get_prices()
    return prices["plans"][vdc_instance.flavor.value]


def calculate_addons_hourly_rate():
    """Calcutlate the addons on hourly rate for all the addons by the user

    Returns:
        total_price (float): the total price for all addons
    """

    vdc_instance = get_vdc_instance()
    total_price = 0
    # Calculate all the hourly late for all addons
    addons = []
    addons = get_addons(vdc_instance.flavor, vdc_instance.kubernetes)
    for addon in addons:
        addon_price = calculate_addon_price(addon)
        j.logger.info(f"addon size {addon.size} with price {addon_price}")
        total_price += addon_price / (24 * 30)
    return total_price


def calculate_hourly_rate():
    """Calculate the total hourly rate of the user used plan and the addons.

    Returns
        hourly_amount(float): the total price for each hour,
                              including the price of the user plan and addons
    """
    discount = FARM_DISCOUNT.get()
    user_plan_price = calculate_plan_base_price()
    hourly_amount = user_plan_price / (24 * 30)
    j.logger.info(f"base plan price {user_plan_price} with hourly amount {hourly_amount}")
    hourly_amount += calculate_addons_hourly_rate()
    return hourly_amount * (1 - discount)


def tranfer_prepaid_to_provision_wallet():
    """Used to transfer the funds from prepaid wallet to provisioning wallet on an hourly basis
    """
    vdc_instance = get_vdc_instance()
    prepaid_wallet = vdc_instance.prepaid_wallet
    provision_wallet = vdc_instance.provision_wallet
    tft = prepaid_wallet._get_asset("TFT")
    hourly_amount = calculate_hourly_rate()
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
    remaining_days = (vdc_instance.expiration_date - j.data.time.now()).days
    days_to_extend = BASE_CAPACITY - remaining_days
    j.logger.info(f"The days to extend {days_to_extend} compared to the base capacity{BASE_CAPACITY}")
    if days_to_extend >= BASE_CAPACITY / 2:
        j.logger.info("starting extending the VDC pools")
        deployer.renew_plan(duration=days_to_extend)
