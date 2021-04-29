from bottle import Bottle, request, HTTPResponse, static_file

from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import login_required, get_user_info
from jumpscale.packages.admin.bottle.models import UserEntry
from jumpscale.core.base import StoredFactory

app = Bottle()


@app.route("/api/allowed", method="GET")
@login_required
def allowed():
    user_factory = StoredFactory(UserEntry)
    user_info = j.data.serializers.json.loads(get_user_info())
    tname = user_info["username"]
    instances = user_factory.list_all()
    for name in instances:
        user_entry = user_factory.get(name)
        if user_entry.tname == tname and user_entry.has_agreed:
            return j.data.serializers.json.dumps({"allowed": True})
    return j.data.serializers.json.dumps({"allowed": False})


@app.route("/api/accept", method="GET")
@login_required
def accept():
    user_factory = StoredFactory(UserEntry)

    user_info = j.data.serializers.json.loads(get_user_info())
    tname = user_info["username"]

    user_entry = user_factory.get(f"{tname.replace('.3bot', '')}")
    if user_entry.has_agreed:
        return HTTPResponse(
            j.data.serializers.json.dumps({"allowed": True}), status=200, headers={"Content-Type": "application/json"}
        )
    else:
        user_entry.has_agreed = True
        user_entry.tname = tname
        user_entry.save()
        return HTTPResponse(
            j.data.serializers.json.dumps({"allowed": True}), status=201, headers={"Content-Type": "application/json"}
        )


@app.route("/api/announced", method="GET")
@login_required
def announced():
    result = bool(j.config.get("ANNOUNCED"))

    return HTTPResponse(
        j.data.serializers.json.dumps({"announced": result}), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/announce", method="GET")
@login_required
def announce():
    j.config.set("ANNOUNCED", True)
    return HTTPResponse(
        j.data.serializers.json.dumps({"announced": True}), status=200, headers={"Content-Type": "application/json"}
    )


@app.route("/api/heartbeat", method="GET")
def heartbeat():
    return HTTPResponse(status=200)


@app.route("/api/export")
@login_required
def export():
    filename = j.tools.export.export_threebot_state()
    exporttime = j.data.time.now().format("YYYY-MM-DDTHH-mm-ssZZ")
    return static_file(
        j.sals.fs.basename(filename),
        root=j.sals.fs.dirname(filename),
        download=f"export-{exporttime}.tar.gz",
        mimetype="application/gzip",
    )
