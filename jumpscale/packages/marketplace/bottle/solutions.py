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
    tid = j.data.serializers.json.loads(get_user_info()).get("tid")
    if not tid:
        return abort(400, "User must be registered by explorer, If you register logout aand login again")
    solutions = j.sals.marketplace.deployer.list_solutions(tid, SolutionType[solution_type.capitalize()], reload=True)
    for solution in solutions:
        solution["reservation"] = solution.pop("reservation_obj").json
    return j.data.serializers.json.dumps({"data": solutions})


@app.route("/api/solutions/count")
@login_required
def count_solutions():
    tid = j.data.serializers.json.loads(get_user_info()).get("tid")
    if not tid:
        return abort(400, "User must be registered by explorer, If you register logout aand login again")
    res = {}
    j.sals.marketplace.deployer.load_user_reservations(tid)
    for sol_type in j.sals.marketplace.deployer.reservations[tid]:
        res[sol_type] = len(j.sals.marketplace.deployer.reservations[tid][sol_type])
    return j.data.serializers.json.dumps({"data": res})


@app.route("/api/solutions/<solution_type>/<reservation_id>", method="DELETE")
@login_required
def cancel_solution(solution_type, reservation_id):
    tid = j.data.serializers.json.loads(get_user_info()).get("tid")
    if not tid:
        return abort(400, "User must be registered by explorer, If you register logout aand login again")
    j.sals.marketplace.deployer.cancel_reservation(tid, reservation_id)


app = SessionMiddleware(app, SESSION_OPTS)
