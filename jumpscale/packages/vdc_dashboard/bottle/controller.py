from beaker.middleware import SessionMiddleware
from bottle import Bottle, request, abort

from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import SESSION_OPTS, controller_autherized
from jumpscale.packages.vdc_dashboard.bottle.vdc_helpers import get_vdc, threebot_vdc_helper


app = Bottle()


@app.route("/api/controller/threebot_vdc", method="POST")
@controller_autherized()
def controller_threebot_vdc():
    # get username
    data = j.data.serializers.json.loads(request.body.read())
    username = data.get("username")
    if not username:
        abort(400, "Error: Not all required params was passed.")
    vdc = get_vdc(username=username)
    return threebot_vdc_helper(vdc=vdc)


app = SessionMiddleware(app, SESSION_OPTS)
