from jinja2 import Environment, FileSystemLoader
from bottle import Bottle
from jumpscale.god import j


app = Bottle()

templates_path = j.sals.fs.join_paths(j.sals.fs.dirname(__file__), "..", "frontend")
env = Environment(loader=FileSystemLoader(templates_path))

threebot = j.servers.threebot.get('default')

@app.route('/<package_name>')
def chats(package_name):
    package = threebot.packages.get(package_name)
    chatflows = package.get_chats()
    return j.data.serializers.json.dumps(list(chatflows.keys()))


@app.route('/<package_name>/<chat_name>')
def chat(package_name, chat_name):
    return env.get_template("index.html").render(
        topic=chat_name,
        username="",
        email=""
    )
