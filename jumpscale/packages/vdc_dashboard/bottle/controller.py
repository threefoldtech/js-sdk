from beaker.middleware import SessionMiddleware
from bottle import Bottle, request, HTTPResponse, abort
import random

from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import SESSION_OPTS, controller_authorized
from jumpscale.packages.vdc_dashboard.bottle.vdc_helpers import get_vdc, threebot_vdc_helper
from jumpscale.sals.vdc.size import VDC_SIZE
from jumpscale.packages.vdc_dashboard.sals.vdc_dashboard_sals import get_kubeconfig_file, get_zstor_config_file


app = Bottle()


def _get_vdc_dict():
    vdc = get_vdc()
    vdc_dict = threebot_vdc_helper(vdc=vdc)
    return vdc_dict


@app.route("/api/controller/vdc", method="POST")
@controller_authorized()
def threebot_vdc():
    """
    request body:
        password

    Returns:
        vdc: string
    """
    vdc_dict = _get_vdc_dict()

    return HTTPResponse(
        j.data.serializers.json.dumps(vdc_dict), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/controller/node/list", method="POST")
@controller_authorized()
def list_nodes():
    """
    request body:
        password

    Returns:
        kubernetes: string
    """
    vdc_dict = _get_vdc_dict()

    return HTTPResponse(
        j.data.serializers.json.dumps(vdc_dict["kubernetes"]), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/controller/node/add", method="POST")
@controller_authorized()
def add_node():
    """
    request body:
        password
        flavor
        farm
        nodes_ids
    Returns:
        wids: list of wids
    """
    data = j.data.serializers.json.loads(request.body.read())
    vdc_password = data.get("password")
    node_flavor = data.get("flavor")
    farm = data.get("farm")
    nodes_ids = data.get("nodes_ids")
    if nodes_ids and not farm:
        abort(400, "Error: Must specify farm with node_ids.")

    if not all([node_flavor]):
        abort(400, "Error: Not all required params were passed.")

    # check stellar service
    if not j.clients.stellar.check_stellar_service():
        abort(400, "Stellar service currently down")

    if node_flavor.upper() not in VDC_SIZE.K8SNodeFlavor.__members__:
        abort(400, "Error: Flavor passed is not supported")
    node_flavor = node_flavor.upper()

    vdc = get_vdc()
    vdc.load_info()
    deployer = vdc.get_deployer(password=vdc_password)
    capacity_check, farm_name = vdc.check_capacity_available(node_flavor, farm)
    if not capacity_check:
        abort(400, f"There's no enough capacity in farm {farm_name} for kubernetes node of flavor {node_flavor}")

    # Payment
    success, _, _ = vdc.show_external_node_payment(bot=None, size=node_flavor, public_ip=False)
    if not success:
        abort(400, "Not enough funds in prepaid wallet to add node")

    old_wallet = deployer._set_wallet(vdc.prepaid_wallet.instance_name)
    try:
        wids = deployer.add_k8s_nodes(node_flavor, farm_name=farm, public_ip=False)
        deployer._set_wallet(old_wallet)
        return HTTPResponse(
            j.data.serializers.json.dumps(wids), status=201, headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        abort(400, f"failed to add nodes to your cluster. due to error {str(e)}")


@app.route("/api/controller/node/delete", method="POST")
@controller_authorized()
def delete_node():
    """
    request body:
        password
        wid

    Returns:
        status
    """
    data = j.data.serializers.json.loads(request.body.read())
    vdc_password = data.get("password")
    wid = data.get("wid")
    if not all([wid]):
        abort(400, "Error: Not all required params were passed.")

    vdc = get_vdc()
    vdc.load_info()
    deployer = vdc.get_deployer(password=vdc_password)

    if vdc.kubernetes[0].wid == wid:
        abort(400, "Error: Can not delete master node")

    try:
        deployer.delete_k8s_node(wid)
    except Exception as e:
        j.logger.error(f"Error: Failed to delete workload due to the following {str(e)}")
        abort(500, "Error: Failed to delete workload")

    return HTTPResponse(
        j.data.serializers.json.dumps({"result": True}), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/controller/zdb/list", method="POST")
@controller_authorized()
def list_zdbs():
    """
    request body:
        password

    Returns:
        zdbs: string
    """
    data = j.data.serializers.json.loads(request.body.read())
    vdc_dict = _get_vdc_dict()

    vdc = get_vdc()
    vdc.load_info()
    zdb_monitor = vdc.get_zdb_monitor()
    zdbs_usage = zdb_monitor.get_zdbs_usage()
    zdbs_info = vdc_dict["s3"]["zdbs"]
    for zdb in zdbs_info:
        zdb_wid = zdb["wid"]
        zdb["usage"] = zdbs_usage.get(zdb_wid)

    return HTTPResponse(
        j.data.serializers.json.dumps(zdbs_info), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/controller/zdb/add", method="POST")
@controller_authorized()
def add_zdb():
    """
    request body:
        password
        capacity
        farm(optional)

    Returns:
        wids: list of wids
    """
    data = j.data.serializers.json.loads(request.body.read())
    capacity = data.get("capacity")
    farm = data.get("farm")

    if not all([capacity]):
        abort(400, "Error: Not all required params were passed.")

    vdc = get_vdc()
    vdc.load_info()

    if not farm:
        zdb_config = j.config.get("S3_AUTO_TOP_SOLUTIONS")
        zdb_farms = zdb_config.get("farm_names")
        farm = random.choice(zdb_farms)
    try:
        zdb_monitor = vdc.get_zdb_monitor()
        wids = zdb_monitor.extend(required_capacity=capacity, farm_names=[farm], wallet_name="prepaid_wallet")
        return HTTPResponse(
            j.data.serializers.json.dumps(wids), status=201, headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        j.logger.error(f"Error: Failed to deploy zdb due to the following {str(e)}")
        abort(500, f"Error: Failed to deploy zdb")


@app.route("/api/controller/zdb/delete", method="POST")
@controller_authorized()
def delete_zdb():
    """
    request body:
        password
        wid

    Returns:
        status
    """
    data = j.data.serializers.json.loads(request.body.read())
    vdc_password = data.get("password")
    wid = data.get("wid")
    if not all([wid]):
        abort(400, "Error: Not all required params were passed.")

    vdc = get_vdc()
    vdc.load_info()
    deployer = vdc.get_deployer(password=vdc_password)

    try:
        deployer.delete_s3_zdb(wid)
    except Exception as e:
        j.logger.error(f"Error: Failed to delete workload due to the following {str(e)}")
        abort(500, "Error: Failed to delete workload")

    return HTTPResponse(
        j.data.serializers.json.dumps({"result": True}), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/controller/wallet", method="POST")
@controller_authorized()
def get_wallet_info():
    """
    request body:
        password

    Returns:
        wallet (prepaid): string
    """
    # Get prepaid wallet info
    vdc_dict = _get_vdc_dict()

    return HTTPResponse(
        j.data.serializers.json.dumps(vdc_dict["wallet"]), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/controller/pools", method="POST")
@controller_authorized()
def list_pools():
    """
    request body:
        password

    Returns:
        pools: string
    """

    vdc = get_vdc()
    vdc.load_info()

    pools = [pool.to_dict() for pool in vdc.active_pools]
    return HTTPResponse(j.data.serializers.json.dumps(pools), status=200, headers={"Content-Type": "application/json"})


@app.route("/api/controller/alerts", method="POST")
@controller_authorized()
def list_alerts():
    """
    request body:
        password
        application (optional, if not given all alerts returned)

    Returns:
        alerts: string
    """
    data = j.data.serializers.json.loads(request.body.read())
    app_name = data.get("application")

    if not app_name:
        alerts = [alert.json for alert in j.tools.alerthandler.find()]
    else:
        alerts = [alert.json for alert in j.tools.alerthandler.find() if alert.app_name == app_name]

    return HTTPResponse(j.data.serializers.json.dumps(alerts), status=200, headers={"Content-Type": "application/json"})


@app.route("/api/controller/kubeconfig", method="POST")
@controller_authorized()
def get_kubeconfig():
    """
    request body:
        password

    Returns:
        kubeconfig: json
    """
    try:
        kubeconfig = get_kubeconfig_file()
        return {"data": kubeconfig}
    except j.exceptions.NotFound as e:
        return HTTPResponse(status=404, message=str(e), headers={"Content-Type": "application/json"})
    except j.exceptions.Value as e:
        return HTTPResponse(status=400, message=str(e), headers={"Content-Type": "application/json"})


@app.route("/api/controller/zstor_config", method="POST")
@controller_authorized()
def get_zstor_config():
    """
    request body:
        password
        ip_version

    Returns:
        zstor_config: json
    """
    data = dict()
    try:
        data = j.data.serializers.json.loads(request.body.read())
    except Exception as e:
        j.logger.error(f"couldn't load body due to error: {str(e)}.")
    ip_version = data.get("ip_version", 6)
    try:
        zstor_config = get_zstor_config_file(ip_version)
        return {"data": j.data.serializers.toml.dumps(zstor_config)}
    except j.exceptions.NotFound as e:
        return HTTPResponse(status=500, message=str(e), headers={"Content-Type": "application/json"})
    except j.exceptions.Value as e:
        return HTTPResponse(status=400, message=str(e), headers={"Content-Type": "application/json"})


app = SessionMiddleware(app, SESSION_OPTS)
