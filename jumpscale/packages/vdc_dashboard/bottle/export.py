from beaker.middleware import SessionMiddleware
from bottle import Bottle, static_file
from jumpscale.loader import j

from jumpscale.packages.auth.bottle.auth import SESSION_OPTS, package_authorized


app = Bottle()


@app.route("/api/threebot/export")
@package_authorized("vdc_dashboard")
def export():
    filename = j.tools.export.export_threebot_state()
    return static_file(
        j.sals.fs.basename(filename),
        root=j.sals.fs.dirname(filename),
        download="export.tar.gz",
        mimetype="application/gzip",
    )


app = SessionMiddleware(app, SESSION_OPTS)
