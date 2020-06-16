from jinja2 import Environment, FileSystemLoader
from bottle import Bottle, request
from jumpscale.god import j
from jumpscale.packages.auth.bottle.auth import login_required, _session_opts
from beaker.middleware import SessionMiddleware


app = Bottle()

templates_path = j.sals.fs.join_paths(j.sals.fs.dirname(__file__), "..", "frontend")
env = Environment(loader=FileSystemLoader(templates_path))

threebot = j.servers.threebot.get("default")


@app.route("/<package_name>")
@login_required
def chats(package_name):
    package = threebot.packages.get(package_name)
    chatflows = package.get_chats()
    return j.data.serializers.json.dumps(list(chatflows.keys()))


@app.route("/<package_name>/chats/<chat_name>")
@login_required
def chat(package_name, chat_name):
    session = request.environ.get("beaker.session")
    return env.get_template("index.html").render(
        topic=chat_name, username=session.get("username", ""), email=session.get("email", "")
    )


app = SessionMiddleware(app, _session_opts)
