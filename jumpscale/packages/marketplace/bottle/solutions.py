from beaker.middleware import SessionMiddleware
from bottle import Bottle, abort, request

from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import SESSION_OPTS, login_required, get_user_info
from jumpscale.sals.reservation_chatflow.models import SolutionType

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


app = SessionMiddleware(app, SESSION_OPTS)
