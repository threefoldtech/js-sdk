from bottle import Bottle, static_file
from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import package_authorized

from .root import app


@app.route("/api/threebot/export")
@package_authorized("vdc_dashboard")
def export():
    filename = j.tools.export.export_threebot_state()
    exporttime = j.data.time.now().format("YYYY-MM-DDTHH-mm-ssZZ")
    return static_file(
        j.sals.fs.basename(filename),
        root=j.sals.fs.dirname(filename),
        download=f"export-{exporttime}.tar.gz",
        mimetype="application/gzip",
    )
