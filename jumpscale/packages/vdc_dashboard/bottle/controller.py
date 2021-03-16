from beaker.middleware import SessionMiddleware
from bottle import Bottle, request, HTTPResponse, abort
import random

from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import SESSION_OPTS, controller_autherized
from jumpscale.packages.vdc_dashboard.bottle.vdc_helpers import get_vdc, threebot_vdc_helper
from jumpscale.sals.vdc.size import VDC_SIZE, ZDB_FARMS, ZDB_STARTING_SIZE
from jumpscale.sals.vdc.scheduler import GlobalScheduler


app = Bottle()


def _get_vdc_dict(username=None):
    if not username:
        abort(400, "Error: Not all required params were passed.")

    vdc = get_vdc(username=username)
    vdc_dict = threebot_vdc_helper(vdc=vdc)
    return vdc_dict


@app.route("/api/controller/vdc", method="POST")
@controller_autherized()
def threebot_vdc():
    """
    request body:
        password
        username

    Returns:
        vdc: string
    """
    # get username
    data = j.data.serializers.json.loads(request.body.read())
    username = data.get("username")

    vdc_dict = _get_vdc_dict(username=username)

    return HTTPResponse(
        j.data.serializers.json.dumps(vdc_dict), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/controller/node/list", method="POST")
@controller_autherized()
def list_nodes():
    """
    request body:
        password
        username

    Returns:
        vdc: string
    """
    # get username
    data = j.data.serializers.json.loads(request.body.read())
    username = data.get("username")
    vdc_dict = _get_vdc_dict(username=username)

    return HTTPResponse(
        j.data.serializers.json.dumps(vdc_dict["kubernetes"]), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/controller/node/add", method="POST")
@controller_autherized()
def add_node():
    # TODO To be tested
    data = j.data.serializers.json.loads(request.body.read())
    vdc_password = data.get("password")
    username = data.get("username")
    node_flavor = data.get("flavor")
    if not all([username, node_flavor]):
        abort(400, "Error: Not all required params were passed.")

    # check stellar service
    if not j.clients.stellar.check_stellar_service():
        abort(400, "Stellar service currently down")

    if node_flavor.upper() not in VDC_SIZE.K8SNodeFlavor.__members__:
        abort(400, "Error: Flavor passed is not supported")
    node_flavor = node_flavor.upper()

    vdc = get_vdc(username=username)
    vdc.load_info()
    deployer = vdc.get_deployer(password=vdc_password)
    capacity_check, farm_name = vdc.check_capacity_available(node_flavor)
    if not capacity_check:
        abort(400, f"There's no enough capacity in farm {farm_name} for kubernetes node of flavor {node_flavor}")

    # Payment
    success, _, _ = vdc.show_external_node_payment(bot=None, size=node_flavor, public_ip=False)
    if not success:
        abort(400, "Not enough funds in prepaid wallet to add node")

    old_wallet = deployer._set_wallet(vdc.prepaid_wallet.instance_name)
    try:
        wids = deployer.add_k8s_nodes(node_flavor, public_ip=False)
        deployer._set_wallet(old_wallet)
        return HTTPResponse(
            j.data.serializers.json.dumps(wids), status=201, headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        abort(400, f"failed to add nodes to your cluster. due to error {str(e)}")


@app.route("/api/controller/node/delete", method="POST")
@controller_autherized()
def delete_node():
    # TODO To be tested
    data = j.data.serializers.json.loads(request.body.read())
    vdc_password = data.get("password")
    username = data.get("username")
    wid = data.get("wid")
    if not all([username, wid]):
        abort(400, "Error: Not all required params were passed.")

    vdc = get_vdc(username=username)
    vdc.load_info()
    deployer = vdc.get_deployer(password=vdc_password)

    try:
        deployer.delete_k8s_node(wid)
    except j.exceptions.Input:
        abort(400, "Error: Failed to delete workload")

    return HTTPResponse(
        j.data.serializers.json.dumps({"result": True}), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/controller/zdb/list", method="POST")
@controller_autherized()
def list_zdbs():
    data = j.data.serializers.json.loads(request.body.read())
    username = data.get("username")
    vdc_dict = _get_vdc_dict(username=username)

    return HTTPResponse(
        j.data.serializers.json.dumps(vdc_dict["s3"]["zdbs"]), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/controller/zdb/add", method="POST")
@controller_autherized()
def add_zdb():
    data = j.data.serializers.json.loads(request.body.read())
    username = data.get("username")
    capacity = data.get("capacity")
    farm = data.get("farm")

    if not all([username, capacity]):
        abort(400, "Error: Not all required params were passed.")

    vdc = get_vdc(username=username)
    vdc.load_info()

    zdb_monitor = vdc.get_zdb_monitor()
    if not farm:
        zdb_farms = zdb_monitor.get_zdb_farm_names()
        farm = random.choice(zdb_farms)
    try:
        zdb_monitor.extend(required_capacity=capacity, farm_names=[farm], wallet_name="prepaid_wallet")
        return HTTPResponse(
            j.data.serializers.json.dumps({"success": True}), status=201, headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        abort(500, f"Error: Failed to deploy zdb due to the following {str(e)}")


@app.route("/api/controller/wallet", method="POST")
@controller_autherized()
def get_wallet_info():
    # Get prepaid wallet info
    data = j.data.serializers.json.loads(request.body.read())
    username = data.get("username")
    vdc_dict = _get_vdc_dict(username=username)

    return HTTPResponse(
        j.data.serializers.json.dumps(vdc_dict["wallet"]), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/controller/pools", method="POST")
@controller_autherized()
def list_pools():
    data = j.data.serializers.json.loads(request.body.read())
    username = data.get("username")

    if not all([username]):
        abort(400, "Error: Not all required params were passed.")

    vdc = get_vdc(username=username)
    vdc.load_info()

    pools = [pool.to_dict() for pool in vdc.active_pools]
    return HTTPResponse(j.data.serializers.json.dumps(pools), status=200, headers={"Content-Type": "application/json"})


@app.route("/api/controller/alerts", method="POST")
@controller_autherized()
def list_alerts():
    data = j.data.serializers.json.loads(request.body.read())
    username = data.get("username")
    app_name = data.get("application")
    if not all([username]):
        abort(400, "Error: Not all required params were passed.")

    if not app_name:
        alerts = [alert.json for alert in j.tools.alerthandler.find()]
    else:
        alerts = [alert.json for alert in j.tools.alerthandler.find() if alert.app_name == app_name]

    return HTTPResponse(j.data.serializers.json.dumps(alerts), status=200, headers={"Content-Type": "application/json"})


app = SessionMiddleware(app, SESSION_OPTS)
