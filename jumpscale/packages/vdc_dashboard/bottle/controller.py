from beaker.middleware import SessionMiddleware
from bottle import Bottle, request, HTTPResponse, abort

from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import SESSION_OPTS, controller_autherized
from jumpscale.packages.vdc_dashboard.bottle.vdc_helpers import get_vdc, threebot_vdc_helper


app = Bottle()


@app.route("/api/controller/threebot_vdc", method="POST")
@controller_autherized()
def controller_threebot_vdc():
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
    if not username:
        abort(400, "Error: Not all required params was passed.")

    vdc = get_vdc(username=username)
    vdc_dict = threebot_vdc_helper(vdc=vdc)

    return HTTPResponse(
        j.data.serializers.json.dumps(vdc_dict), status=200, headers={"Content-Type": "application/json"}
    )


app = SessionMiddleware(app, SESSION_OPTS)
