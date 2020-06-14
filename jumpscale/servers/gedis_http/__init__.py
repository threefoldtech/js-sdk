from jumpscale.core.base import Base, fields
from jumpscale.god import j
from gevent.pool import Pool
from bottle import Bottle, abort, request
from gevent.pywsgi import WSGIServer
from jumpscale.core.base import StoredFactory
import json


class GedisHTTPServer(Base):
    host = fields.String(default="127.0.0.1")
    port = fields.Integer(default=8000)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app = Bottle()
        self._client = None
        self._app.route("/<package>/<actor>/<method>", ["GET", "POST"], self.handler)

    @property
    def client(self):
        if self._client is None:
            self._client = j.clients.gedis.get(self.instance_name)
            self._client.disable_deserialization = True
        return self._client

    def handler(self, package, actor, method):
        actors = self.client.actors

        actor = getattr(actors, f"{package}_{actor}", None)
        if not actor:
            return abort(400, "actor not found")

        method = getattr(actor, method, None)
        if not method:
            return abort(400, "method not found")

        kwargs = request.json or dict()
        response = method(**kwargs)

        return json.dumps(response.result)

    @property
    def gevent_server(self):
        return WSGIServer((self.host, self.port), self._app, spawn=Pool())


def export_module_as():
    return StoredFactory(GedisHTTPServer)
