from bottle import Bottle, abort, request

from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import login_required

app = Bottle()

templates_path = j.sals.fs.join_paths(j.sals.fs.dirname(__file__), "..", "frontend")
env = j.tools.jinja2.get_env(templates_path)


@app.route("/<package_name>")
@login_required
def chats(package_name):
    threebot = j.servers.threebot.get()
    package = threebot.packages.get(package_name)
    if not package:
        abort(404, f"package {package_name} does not exist")
    chatflows = package.get_chats()
    return j.data.serializers.json.dumps(list(chatflows.keys()))


@app.route("/<package_name>/chats/<chat_name>")
@login_required
def chat(package_name, chat_name):
    session = request.environ.get("beaker.session", {})
    return env.get_template("index.html").render(
        package=package_name, chat=chat_name, username=session.get("username", ""), email=session.get("email", "")
    )
