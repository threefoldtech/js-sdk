from beaker.middleware import SessionMiddleware
from bottle import Bottle, request, HTTPResponse, abort

from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import SESSION_OPTS, controller_autherized
from jumpscale.packages.vdc_dashboard.bottle.vdc_helpers import get_vdc, threebot_vdc_helper


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
    # TODO
    pass


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
    # TODO
    pass


@app.route("/api/controller/wallet", method="POST")
@controller_autherized()
def get_wallet_info():
    data = j.data.serializers.json.loads(request.body.read())
    username = data.get("username")
    vdc_dict = _get_vdc_dict(username=username)

    return HTTPResponse(
        j.data.serializers.json.dumps(vdc_dict["wallet"]), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/controller/pools", method="POST")
@controller_autherized()
def list_pools():
    # TODO
    pass


@app.route("/api/controller/alerts", method="POST")
@controller_autherized()
def list_alerts():
    # TODO
    pass


app = SessionMiddleware(app, SESSION_OPTS)
