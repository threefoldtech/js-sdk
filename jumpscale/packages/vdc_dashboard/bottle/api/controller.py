import random

from beaker.middleware import SessionMiddleware
from bottle import Bottle, HTTPResponse, abort, parse_auth, request

from jumpscale.loader import j
from jumpscale.packages.vdc_dashboard.bottle.api.exceptions import (
    AdddingNodeFailed,
    CannotDeleteMasterNode,
    FlavorNotSupported,
    InvalidKubeConfig,
    InvalidZStorConfig,
    KubeConfigNotFound,
    MissingArgument,
    NoEnoughCapacity,
    NoEnoughFunds,
    StellarServiceDown,
    ZDBDeletionFailed,
    ZDBDeploymentFailed,
    ZStorConfigNotFound,
)
from jumpscale.packages.vdc_dashboard.bottle.api.helpers import get_full_vdc_info, vdc_route
from jumpscale.packages.vdc_dashboard.bottle.vdc_helpers import _list_alerts, get_vdc, threebot_vdc_helper
from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_kubeconfig_file, get_zstor_config_file
from jumpscale.sals.vdc.size import VDC_SIZE


app = Bottle()


@app.route("/api/controller/vdc", method="GET")
@vdc_route()
def threebot_vdc(vdc):
    """
    Returns:
        dict: full vfc info
    """
    return get_full_vdc_info(vdc)


@app.route("/api/controller/node", method="GET")
@vdc_route()
def list_nodes(vdc):
    """
    Returns:
        dict: kubernates info
    """
    return get_full_vdc_info(vdc)["kubernetes"]


@app.route("/api/controller/node", method="POST")
@vdc_route()
def add_node(vdc):
    """
    request body:
        flavor
        farm(optional)
        nodes_ids(optional)

    Returns:
        wids: list of wids
    """
    data = request.json or {}
    node_flavor = data.get("flavor")
    farm = data.get("farm")
    nodes_ids = data.get("nodes_ids")
    if nodes_ids and not farm:
        raise MissingArgument(400, "Must specify farm with nodes_ids.")

    if not all([node_flavor, farm, node_ids]):
        raise MissingArgument(400, "MustNot all required arguments were passed.")

    # check stellar service
    if not j.clients.stellar.check_stellar_service():
        raise StellarServiceDown(400, "Stellar service currently down")

    if node_flavor.upper() not in VDC_SIZE.K8SNodeFlavor.__members__:
        raise FlavorNotSupported(400, "Flavor passed is not supported")

    node_flavor = node_flavor.upper()
    deployer = vdc.get_deployer()
    farm_name, capacity_check = deployer.find_worker_farm(node_flavor)
    if not capacity_check:
        raise NoEnoughCapacity(
            400, f"There's no enough capacity in farm {farm_name} for kubernetes node of flavor {node_flavor}"
        )

    # Payment
    success, _, _ = vdc.show_external_node_payment(bot=None, farm_name=farm_name, size=node_flavor, public_ip=False)
    if not success:
        raise NoEnoughFunds(400, "No enough funds in prepaid wallet to add node")

    old_wallet = deployer._set_wallet(vdc.prepaid_wallet.instance_name)
    duration = vdc.get_pools_expiration() - j.data.time.utcnow().timestamp
    two_weeks = 2 * 7 * 24 * 60 * 60
    if duration > two_weeks:
        duration = two_weeks

    try:
        wids = deployer.add_k8s_nodes(node_flavor, public_ip=False)
        deployer.extend_k8s_workloads(duration, *wids)
        deployer._set_wallet(old_wallet)
        return wids
    except Exception as e:
        raise AdddingNodeFailed(400, f"failed to add nodes to your cluster. due to error {e}")


@app.route("/api/controller/node", method="DELETE")
@vdc_route()
def delete_node(vdc):
    """
    Returns:
        dict: status
    """
    data = request.json or {}
    wid = data.get("wid")
    if not wid:
        raise MissingArgument(400, "Not all required params were passed.")

    deployer = vdc.get_deployer()
    if vdc.kubernetes[0].wid == wid:
        raise CannotDeleteMasterNode(400, "Can not delete master node")

    try:
        deployer.delete_k8s_node(wid)
    except Exception as e:
        j.logger.error(f"Error: Failed to delete workload due to the following {str(e)}")
        raise CannotDeleteMasterNode(500, "Error: Failed to delete workload")

    return {"success": True}


@app.route("/api/controller/zdb", method="GET")
@vdc_route()
def list_zdbs(vdc):
    """
    Returns:
        zdbs: string
    """
    vdc_dict = get_full_vdc_info(vdc)
    zdb_monitor = vdc.get_zdb_monitor()
    zdbs_usage = zdb_monitor.get_zdbs_usage()
    zdbs_info = vdc_dict["s3"]["zdbs"]
    for zdb in zdbs_info:
        zdb_wid = zdb["wid"]
        zdb["usage"] = zdbs_usage.get(zdb_wid)

    return zdbs_info


@app.route("/api/controller/zdb", method="POST")
@vdc_route()
def add_zdb(vdc):
    """
    request body:
        capacity
        farm(optional)
        nodes_ids(optional)

    Returns:
        wids: list of wids
    """
    data = request.json or {}
    capacity = data.get("capacity")
    farm = data.get("farm")
    nodes_ids = data.get("nodes_ids")

    if not capacity:
        raise MissingArgument(400, "'capacity' is required")

    if nodes_ids and not farm:
        raise MissingArgument(400, "Must specify farm with nodes_ids.")

    if not farm:
        zdb_config = j.config.get("S3_AUTO_TOP_SOLUTIONS")
        zdb_farms = zdb_config.get("farm_names")
        farm = random.choice(zdb_farms)

    zdb_monitor = vdc.get_zdb_monitor()
    wids = zdb_monitor.extend(
        required_capacity=capacity, farm_names=[farm], wallet_name="prepaid_wallet", nodes_ids=nodes_ids
    )
    return wids


@app.route("/api/controller/zdb", method="DELETE")
@vdc_route()
def delete_zdb(vdc):
    """
    request body:
        wid

    Returns:
        dict: status
    """
    data = request.json or {}

    wid = data.get("wid")
    if not all([wid]):
        raise MissingArgument(400, "Not all required params were passed.")

    deployer = vdc.get_deployer()

    try:
        deployer.delete_s3_zdb(wid)
    except Exception as e:
        j.logger.error(f"Error: Failed to delete workload due to the following {str(e)}")
        raise ZDBDeletionFailed(500, "Error: Failed to delete workload")

    return {"success": True}


@app.route("/api/controller/wallet", method="GET")
@vdc_route()
def get_wallet_info(vdc):
    """
    Returns:
        dict: wallet (prepaid)
    """
    # Get prepaid wallet info
    return get_full_vdc_info(vdc)["wallet"]


@app.route("/api/controller/pools", method="GET")
@vdc_route()
def list_pools(vdc):
    """
    Returns:
        list: pools
    """
    return [pool.to_dict() for pool in vdc.active_pools]


@app.route("/api/controller/alerts/<app_name>", method="GET")
@vdc_route()
def list_alerts(vdc, app_name):
    """
    request body:
        application (optional, if not given all alerts returned)

    Returns:
        list: alerts
    """
    return _list_alerts(app_name)


@app.route("/api/controller/kubeconfig", method="GET")
@vdc_route(serialize=False)
def get_kubeconfig(vdc):
    """
    Returns:
        str: config file content
    """
    try:
        return get_kubeconfig_file()
    except j.exceptions.NotFound as e:
        raise KubeConfigNotFound(404, str(e))
    except j.exceptions.Value as e:
        raise InvalidKubeConfig(400, str(e))


@app.route("/api/controller/zstor_config", method="GET")
@vdc_route(serialize=False)
def get_zstor_config(vdc):
    """
    request body:
        ip_version

    Returns:
        str: config file content
    """
    data = request.json or {}
    ip_version = data.get("ip_version", 6)

    try:
        return get_zstor_config_file(ip_version)
    except j.exceptions.NotFound as e:
        raise ZStorConfigNotFound(404, str(e))
    except j.exceptions.Value as e:
        raise InvalidZStorConfig(400)


@app.route("/api/controller/status", method="GET")
def is_running():
    """Make sure the controller is running

    Returns:
        object: will only reply if the controller is alive
    """
    return HTTPResponse(
        j.data.serializers.json.dumps({"running": True}), status=200, headers={"Content-Type": "application/json"},
    )
