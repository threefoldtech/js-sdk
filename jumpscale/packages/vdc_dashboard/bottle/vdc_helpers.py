from bottle import HTTPResponse, abort
import math
from jumpscale.loader import j

from jumpscale.sals.vdc.size import VDC_SIZE
from jumpscale.sals.vdc.models import KubernetesRole


def _get_addons(flavor, kubernetes_addons):
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


def _total_capacity(vdc):
    addons = _get_addons(vdc.flavor, vdc.kubernetes)
    plan = VDC_SIZE.VDC_FLAVORS.get(vdc.flavor)
    plan_nodes_count = plan.get("k8s").get("no_nodes")
    return plan_nodes_count + len(addons) + 1


def get_vdc():
    if not j.sals.vdc.list_all():
        abort(500, "Couldn't find any vdcs on this machine, Please make sure to have it configured properly")
    vdc_full_name = list(j.sals.vdc.list_all())[0]
    return j.sals.vdc.find(vdc_full_name, load_info=True)


def threebot_vdc_helper(vdc=None):
    if not vdc:
        return HTTPResponse(status=404, headers={"Content-Type": "application/json"})
    vdc_dict = vdc.to_dict()
    vdc_dict["expiration_days"] = (vdc.expiration_date - j.data.time.now()).days
    vdc_dict["expiration_date"] = vdc.calculate_expiration_value(False)
    # Add wallet address
    wallet = vdc.prepaid_wallet
    balances = wallet.get_balance()
    balances_data = []
    for item in balances.balances:
        # Add only TFT balance
        if item.asset_code == "TFT":
            balances_data.append(
                {"balance": item.balance, "asset_code": item.asset_code, "asset_issuer": item.asset_issuer}
            )
    vdc_dict["total_capacity"] = _total_capacity(vdc)
    vdc_dict["wallet"] = {
        "address": wallet.address,
        "network": wallet.network.value,
        "secret": wallet.secret,
        "balances": balances_data,
    }
    vdc_dict["price"] = math.ceil(vdc.calculate_spec_price())

    return vdc_dict


def _list_alerts(app_name: str = ""):

    if app_name:
        alerts = [alert.json for alert in j.tools.alerthandler.find() if alert.app_name == app_name]
    else:
        alerts = [alert.json for alert in j.tools.alerthandler.find()]

    return alerts
