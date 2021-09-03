from bottle import Bottle, request, HTTPResponse
from jumpscale.packages.threebot_deployer.bottle.utils import (
    list_threebot_solutions,
    stop_threebot_solution,
    delete_threebot_solution,
)

from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import login_required, get_user_info
from jumpscale.packages.marketplace.bottle.models import UserEntry
from jumpscale.core.base import StoredFactory
from jumpscale.core.exceptions import exceptions

app = Bottle()


@app.route("/api/threebots/list")
@login_required
def list_threebots() -> str:
    user_info = j.data.serializers.json.loads(get_user_info())
    threebots = list_threebot_solutions(user_info["username"])
    return j.data.serializers.json.dumps({"data": threebots})


@app.route("/api/threebots/stop", method="POST")
@login_required
def stop_threebot() -> str:
    data = j.data.serializers.json.loads(request.body.read())
    user_info = j.data.serializers.json.loads(get_user_info())
    if "password" not in data or "uuid" not in data:
        return HTTPResponse(
            j.data.serializers.json.dumps({"error": "invalid body. missing keys"}),
            status=400,
            headers={"Content-Type": "application/json"},
        )
    try:
        stop_threebot_solution(owner=user_info["username"], solution_uuid=data["uuid"], password=data["password"])
    except (exceptions.Permission, exceptions.Validation):
        return HTTPResponse(
            j.data.serializers.json.dumps({"error": "invalid secret"}),
            status=401,
            headers={"Content-Type": "application/json"},
        )
    return j.data.serializers.json.dumps({"data": True})


@app.route("/api/threebots/destroy", method="POST")
@login_required
def destroy_threebot() -> str:
    data = j.data.serializers.json.loads(request.body.read())
    user_info = j.data.serializers.json.loads(get_user_info())
    if "password" not in data or "uuid" not in data:
        return HTTPResponse(
            j.data.serializers.json.dumps({"error": "invalid body. missing keys"}),
            status=400,
            headers={"Content-Type": "application/json"},
        )
    try:
        delete_threebot_solution(owner=user_info["username"], solution_uuid=data["uuid"], password=data["password"])
    except (exceptions.Permission, exceptions.Validation):
        return HTTPResponse(
            j.data.serializers.json.dumps({"error": "invalid secret"}),
            status=401,
            headers={"Content-Type": "application/json"},
        )
    return j.data.serializers.json.dumps({"data": True})


@app.route("/api/allowed", method="GET")
@login_required
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
@login_required
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
