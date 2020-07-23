from beaker.middleware import SessionMiddleware
from bottle import Bottle, abort, request, HTTPResponse

from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import SESSION_OPTS, login_required, get_user_info
from jumpscale.sals.reservation_chatflow.models import SolutionType
from jumpscale.packages.marketplace.bottle.models import UserEntry
from jumpscale.core.base import StoredFactory

app = Bottle()


@app.route("/api/solutions/<solution_type>")
@login_required
def list_solutions(solution_type: str) -> str:
    solutions = []
    user_info = j.data.serializers.json.loads(get_user_info())
    solutions = j.sals.marketplace.deployer.list_solutions(
        user_info["username"], SolutionType(solution_type.lower()), reload=True
    )
    for solution in solutions:
        solution["reservation"] = solution.pop("reservation_obj").json
    return j.data.serializers.json.dumps({"data": solutions})


@app.route("/api/solutions/count")
@login_required
def count_solutions():
    res = {}
    user_info = j.data.serializers.json.loads(get_user_info())
    j.sals.marketplace.deployer.load_user_reservations(user_info["username"])
    for sol_type in j.sals.marketplace.deployer.reservations[user_info["username"]]:
        res[sol_type] = len(j.sals.marketplace.deployer.reservations[user_info["username"]][sol_type])
    return j.data.serializers.json.dumps({"data": res})


@app.route("/api/solutions/<solution_type>/<reservation_id>", method="DELETE")
@login_required
def cancel_solution(solution_type, reservation_id):
    user_info = j.data.serializers.json.loads(get_user_info())
    j.sals.marketplace.deployer.cancel_reservation(user_info["username"], reservation_id)


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


app = SessionMiddleware(app, SESSION_OPTS)
