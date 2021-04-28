import inspect
import json
import sys
import os
from redis import Redis
from enum import Enum
from functools import partial
from io import BytesIO
from signal import SIGKILL, SIGTERM
import json
import gevent
from gevent.pool import Pool
from gevent import time
from gevent.server import StreamServer
from jumpscale.core.base import Base, fields
from jumpscale.loader import j
from redis.connection import DefaultParser, Encoder
from redis.exceptions import ConnectionError
from .baseactor import BaseActor
from .systemactor import CoreActor, SystemActor


def serialize(obj):
    if not isinstance(obj, (str, int, float, list, tuple, dict, bool)):
        module = inspect.getmodule(obj).__file__[:-3]
        return dict(__serialized__=True, module=module, type=obj.__class__.__name__, data=obj.to_dict())
    return obj


def deserialize(obj):
    if isinstance(obj, dict) and obj.get("__serialized__"):
        module = sys.modules[obj["module"]]
        object_instance = getattr(module, obj["type"])()
        object_instance.from_dict(obj["data"])
        return object_instance
    return obj


class GedisErrorTypes(Enum):
    NOT_FOUND = 0
    BAD_REQUEST = 1
    ACTOR_ERROR = 3
    INTERNAL_SERVER_ERROR = 4
    PERMISSION_ERROR = 5


EXCEPTIONS_MAP = {
    j.exceptions.Value: GedisErrorTypes.BAD_REQUEST.value,
    j.exceptions.NotFound: GedisErrorTypes.NOT_FOUND.value,
    j.exceptions.Permission: GedisErrorTypes.PERMISSION_ERROR.value,
}


class RedisConnectionAdapter:
    def __init__(self, sock):
        self.socket = sock
        self._sock = sock
        self.socket_timeout = 600
        self.socket_connect_timeout = 600
        self.socket_keepalive = True
        self.retry_on_timeout = True
        self.socket_keepalive_options = {}
        self.encoder = Encoder("utf", "strict", False)


class ResponseEncoder:
    def __init__(self, socket):
        self.socket = socket
        self.buffer = BytesIO()

    def encode(self, value):
        """Respond with data."""
        if value is None:
            self._write_buffer("$-1\r\n")
        elif isinstance(value, int):
            self._write_buffer(":{}\r\n".format(value))
        elif isinstance(value, bool):
            self._write_buffer(":{}\r\n".format(1 if value else 0))
        elif isinstance(value, str):
            if "\n" in value:
                self._bulk(value)
            else:
                self._write_buffer("+{}\r\n".format(value))
        elif isinstance(value, bytes):
            self._bulkbytes(value)
        elif isinstance(value, list):
            if value and value[0] == "*REDIS*":
                value = value[1:]
            self._array(value)
        elif hasattr(value, "__repr__"):
            self._bulk(value.__repr__())
        else:
            value = j.data.serializers.json.dumps(value, encoding="utf-8")
            self.encode(value)

        self._send()

    def status(self, msg="OK"):
        """Send a status."""
        self._write_buffer("+{}\r\n".format(msg))
        self._send()

    def error(self, msg):
        """Send an error."""
        # print("###:%s" % msg)
        self._write_buffer("-ERR {}\r\n".format(msg))
        self._send()

    def _bulk(self, value):
        """Send part of a multiline reply."""
        data = ["$", str(len(value)), "\r\n", value, "\r\n"]
        self._write_buffer("".join(data))

    def _array(self, value):
        """send an array."""
        self._write_buffer("*{}\r\n".format(len(value)))
        for item in value:
            self.encode(item)

    def _bulkbytes(self, value):
        data = [b"$", str(len(value)).encode(), b"\r\n", value, b"\r\n"]
        self._write_buffer(b"".join(data))

    def _write_buffer(self, data):
        if isinstance(data, str):
            data = data.encode()

        self.buffer.write(data)

    def _send(self):
        self.socket.sendall(self.buffer.getvalue())
        self.buffer = BytesIO()  # seems faster then truncating


SERIALIZABLE_TYPES = (str, int, float, list, tuple, dict, bool)
RESERVED_ACTOR_NAMES = ("core", "system")


class GedisServer(Base):
    host = fields.String(default="127.0.0.1")
    port = fields.Integer(default=16000)
    enable_system_actor = fields.Boolean(default=True)
    run_async = fields.Boolean(default=True)
    _actors = fields.Typed(dict, default={})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._core_actor = CoreActor()
        self._system_actor = SystemActor()
        self._loaded_actors = {"core": self._core_actor}

    @property
    def actors(self):
        """Lists saved actors

        Returns:
            list -- List of saved actors
        """
        return self._actors

    def actor_add(self, actor_name: str, actor_path: str):
        """Adds an actor to the server

        Arguments:
            actor_name {str} -- Actor name
            actor_path {str} -- Actor absolute path

        Raises:
            j.exceptions.Value: raises if actor name is matched one of the reserved actor names
            j.exceptions.Value: raises if actor name is not a valid identifier
        """
        if actor_name in RESERVED_ACTOR_NAMES:
            raise j.exceptions.Value("Invalid actor name")

        if not actor_name.isidentifier():
            raise j.exceptions.Value(f"Actor name should be a valid identifier")

        self._actors[actor_name] = actor_path

    def actor_delete(self, actor_name: str):
        """Removes an actor from the server

        Arguments:
            actor_name {str} -- Actor name
        """
        self._actors.pop(actor_name, None)

    def start(self):
        """Starts the server
        """
        # register system actor if enabled
        if self.enable_system_actor:
            self._register_actor("system", self._system_actor)

        self._core_actor.set_server(self)
        self._system_actor.set_server(self)

        # register saved actors
        for actor_name, actor_path in self._actors.items():
            self._system_actor.register_actor(actor_name, actor_path)

        # start the server
        self._server = StreamServer((self.host, self.port), self._on_connection, spawn=Pool())
        self._server.reuse_addr = True
        self._server.start()

        j.logger.info(f"Gedis server is started at {self.host}:{self.port}...")

    def stop(self):
        """Stops the server
        """
        j.logger.info("Shutting down...")
        self._server.stop()

    def _register_actor(self, actor_name: str, actor_module: BaseActor):
        self._loaded_actors[actor_name] = actor_module

    def _unregister_actor(self, actor_name: str):
        self._loaded_actors.pop(actor_name, None)

    def _execute(self, method, args, kwargs):
        response = {}
        try:
            response["result"] = method(*args, **kwargs)

        except Exception as e:
            j.logger.exception(f"error while executing {method}", exception=e)

            response["error"] = str(e)
            response["error_type"] = EXCEPTIONS_MAP.get(e.__class__, GedisErrorTypes.ACTOR_ERROR.value)

        return response

    def _on_connection(self, socket, address):
        j.logger.debug(f"New connection from {address}")
        parser = DefaultParser(65536)
        connection = RedisConnectionAdapter(socket)
        try:
            encoder = ResponseEncoder(socket)
            parser.on_connect(connection)

            while True:
                response = dict(success=True, result=None, error=None, error_type=None, is_async=False, task_id=None)
                try:
                    request = parser.read_response()

                    if len(request) < 2:
                        response["error"] = "invalid request"
                        response["error_type"] = GedisErrorTypes.BAD_REQUEST.value

                    else:
                        actor_name = request.pop(0).decode()
                        method_name = request.pop(0).decode()
                        actor_object = self._loaded_actors.get(actor_name)

                        if not actor_object:
                            response["error"] = "actor not found"
                            response["error_type"] = GedisErrorTypes.NOT_FOUND.value

                        elif not hasattr(actor_object, method_name):
                            response["error"] = "method not found"
                            response["error_type"] = GedisErrorTypes.NOT_FOUND.value

                        else:
                            j.logger.debug(
                                f"Executing method {method_name} from actor {actor_name} to client {address}"
                            )

                            if request:
                                args, kwargs = json.loads(request.pop(0), object_hook=deserialize)
                            else:
                                args, kwargs = (), {}

                            method = getattr(actor_object, method_name)
                            result = self._execute(method, args, kwargs)
                            response.update(result)

                except ConnectionError:
                    j.logger.debug(f"Client {address} closed the connection", address)

                except Exception as exception:
                    j.logger.exception("internal error", exception=exception)
                    response["error"] = "internal server error"
                    response["error_type"] = GedisErrorTypes.INTERNAL_SERVER_ERROR.value

                response["success"] = response["error"] is None
                encoder.encode(json.dumps(response, default=serialize))

            parser.on_disconnect()

        except BrokenPipeError:
            pass
