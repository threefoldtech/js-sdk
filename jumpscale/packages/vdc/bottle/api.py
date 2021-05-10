import math

from beaker.middleware import SessionMiddleware
from bottle import Bottle, HTTPResponse, abort, redirect, request
import gevent
from jumpscale.core.base import StoredFactory
from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import get_user_info, login_required, package_authorized
from jumpscale.packages.vdc_dashboard.bottle.models import UserEntry
from jumpscale.sals.vdc import VDCFACTORY
from jumpscale.sals.vdc.vdc import VDCSTATE

app = Bottle()


def _list_vdcs():
    user_info = j.data.serializers.json.loads(get_user_info())
    username = user_info["username"]
    result = []

    def get_vdc(vdc):
        if vdc.state == VDCSTATE.EMPTY:
            return

        if vdc.is_empty():
            j.logger.warning(f"vdc {vdc.solution_uuid} is empty")
            vdc.state = VDCSTATE.EMPTY
            vdc.save()
            return

        vdc_dict = vdc.to_dict()
        vdc_dict.pop("s3")
        vdc_dict.pop("kubernetes")
        vdc_dict.pop("etcd")
        result.append(vdc_dict)

    threads = []
    vdcs = VDCFACTORY.list(username)
    for vdc in vdcs:
        thread = gevent.spawn(get_vdc, vdc)
        threads.append(thread)
    gevent.joinall(threads)
    return result


@app.route("/api/vdcs", method="GET")
@package_authorized("vdc")
def list_vdcs():
    return HTTPResponse(
        j.data.serializers.json.dumps(_list_vdcs()), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/vdc_refer/<solution>", method="GET")
@package_authorized("vdc")
def redirect_refer(solution):
    vdcs = _list_vdcs()
    if not vdcs:
        return redirect(f"/vdc/?sol={solution}#/chats/new_vdc/create")
    else:
        return redirect(f"https://{vdcs[0]['threebot']['domain']}/vdc_dashboard/api/refer/{solution}")


@app.route("/api/vdcs/<name>", method="GET")
@package_authorized("vdc")
def get_vdc_info(name):
    user_info = j.data.serializers.json.loads(get_user_info())
    username = user_info["username"]
    vdc = VDCFACTORY.find(vdc_name=name, owner_tname=username, load_info=True)
    if not vdc:
        return HTTPResponse(status=404, headers={"Content-Type": "application/json"})
    vdc_dict = vdc.to_dict()
    vdc_dict.pop("s3")
    vdc_dict.pop("kubernetes")
    vdc_dict.pop("etcd")
    vdc_dict["price"] = math.ceil(vdc.calculate_spec_price(False))
    wallet = vdc.prepaid_wallet
    balances = wallet.get_balance()
    balances_data = []
    for item in balances.balances:
        # Add only TFT balance
        if item.asset_code == "TFT":
            balances_data.append(
                {"balance": item.balance, "asset_code": item.asset_code, "asset_issuer": item.asset_issuer}
            )

    vdc_dict["wallet"] = {
        "address": wallet.address,
        "network": wallet.network.value,
        "secret": wallet.secret,
        "balances": balances_data,
    }
    return HTTPResponse(
        j.data.serializers.json.dumps(vdc_dict), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/vdcs/delete", method="POST")
@package_authorized("vdc")
def delete_vdc():
    data = j.data.serializers.json.loads(request.body.read())
    name = data.get("name")
    if not name:
        abort(400, "Error: Not all required params was passed.")
    user_info = j.data.serializers.json.loads(get_user_info())
    username = user_info["username"]
    vdc = VDCFACTORY.find(vdc_name=name, owner_tname=username, load_info=True)
    if not vdc:
        return HTTPResponse(status=404, headers={"Content-Type": "application/json"})

    try:
        j.logger.info(f"Attemting deleting vdc: {name}")
        vdc = VDCFACTORY.find(f"vdc_{vdc.vdc_name}_{vdc.owner_tname}")
        VDCFACTORY.cleanup_vdc(vdc)
        vdc.state = VDCSTATE.EMPTY
        vdc.save()
    except Exception as e:
        j.logger.error(f"Error deleting VDC {name} due to {str(e)}")
        return HTTPResponse(f"Error deleteing VDC {name}", status=400, headers={"Content-Type": "application/json"})

    return HTTPResponse("Sucess", status=200, headers={"Content-Type": "application/json"})


@app.route("/api/allowed", method="GET")
@package_authorized("vdc")
def allowed():
    user_factory = StoredFactory(UserEntry)
    user_info = j.data.serializers.json.loads(get_user_info())
    tname = user_info["username"]
    explorer_url = j.core.identity.me.explorer.url
    instances = user_factory.list_all()
    for name in instances:
        user_entry = user_factory.get(name)
        if user_entry.tname == tname and user_entry.explorer_url == explorer_url and user_entry.has_agreed:
            return j.data.serializers.json.dumps({"allowed": True})
    return j.data.serializers.json.dumps({"allowed": False})


@app.route("/api/accept", method="GET")
@package_authorized("vdc")
def accept():
    user_factory = StoredFactory(UserEntry)

    user_info = j.data.serializers.json.loads(get_user_info())
    tname = user_info["username"]
    explorer_url = j.core.identity.me.explorer.url

    if "testnet" in explorer_url:
        explorer_name = "testnet"
    elif "devnet" in explorer_url:
        explorer_name = "devnet"
    elif "explorer.grid.tf" in explorer_url:
        explorer_name = "mainnet"
    else:
        return HTTPResponse(
            j.data.serializers.json.dumps({"error": f"explorer {explorer_url} is not supported"}),
            status=500,
            headers={"Content-Type": "application/json"},
        )

    user_entry = user_factory.get(f"{explorer_name}_{tname.replace('.3bot', '')}")
    if user_entry.has_agreed:
        return HTTPResponse(
            j.data.serializers.json.dumps({"allowed": True}), status=200, headers={"Content-Type": "application/json"}
        )
    else:
        user_entry.has_agreed = True
        user_entry.explorer_url = explorer_url
        user_entry.tname = tname
        user_entry.save()
        return HTTPResponse(
            j.data.serializers.json.dumps({"allowed": True}), status=201, headers={"Content-Type": "application/json"}
        )


@app.route("/api/wallet/qrcode/get", method="POST")
@login_required
def get_wallet_qrcode_image():
    request_data = j.data.serializers.json.loads(request.body.read())
    address = request_data.get("address")
    amount = request_data.get("amount")
    scale = request_data.get("scale", 5)
    if not all([address, amount, scale]):
        return HTTPResponse("Not all parameters satisfied", status=400, headers={"Content-Type": "application/json"})

    data = f"TFT:{address}?amount={amount}&message=topup&sender=me"
    qrcode_image = j.tools.qrcode.base64_get(data, scale=scale)
    return j.data.serializers.json.dumps({"data": qrcode_image})
