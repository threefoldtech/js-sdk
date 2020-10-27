import inspect
import json
import os
import sys
from functools import partial

from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from jumpscale.loader import j
from jumpscale.servers.gedis.server import GedisErrorTypes, deserialize, serialize
from jumpscale.tools.codeloader import load_python_module


class ActorResult:
    def __init__(self, **kwargs):
        self.success = kwargs.get("success", True)
        self.result = kwargs.get("result", None)
        self.error = kwargs.get("error", None)
        self.error_type = kwargs.get("error_type", None)
        self.is_async = kwargs.get("is_async", False)
        self.task_id = kwargs.get("task_id", None)

    def __dir__(self):
        return list(self.__dict__.keys())

    def __repr__(self):
        return str(self.__dict__)


class ActorProxy:
    def __init__(self, actor_name, actor_info, client):
        """ActorProxy to remote actor on the server side

        Arguments:
            actor_name {str} -- [description]
            actor_info {dict} -- actor information dict e.g { method_name: { args: [], 'doc':...} }
            gedis_client {GedisClient} -- gedis client reference
        """
        self.actor_name = actor_name
        self.actor_info = actor_info
        self.client = client

    def __dir__(self):
        """Delegate the available functions on the ActorProxy to `actor_info` keys

        Returns:
            list -- methods available on the ActorProxy
        """
        return list(self.actor_info["methods"].keys())

    def __getattr__(self, method):
        """Return a function representing the remote function on the actual actor

        Arguments:
            attr {str} -- method name

        Returns:
            function -- function waiting on the arguments
        """

        def function(*args, **kwargs):
            return self.client.execute(self.actor_name, method, *args, **kwargs)

        func = partial(function)
        func.__doc__ = self.actor_info["methods"][method]["doc"]
        return func


class ActorsCollection:
    def __init__(self, actors):
        self._actors = actors

    def __dir__(self):
        return list(self._actors.keys())

    def __getattr__(self, actor_name):
        if actor_name in self._actors:
            return self._actors[actor_name]


class GedisClient(Client):
    name = fields.String(default="local")
    hostname = fields.String(default="localhost")
    port = fields.Integer(default=16000)
    raise_on_error = fields.Boolean(default=False)
    disable_deserialization = fields.Boolean(default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._redisclient = None
        self._loaded_actors = {}
        self._loaded_modules = []
        self.actors = None
        self._load_actors()

    @property
    def redis_client(self):
        if self._redisclient is None:
            self._redisclient = j.clients.redis.get(name=f"gedis_{self.name}", hostname=self.hostname, port=self.port)
        return self._redisclient

    def _load_module(self, path, force_reload=False):
        load_python_module(path, force_reload=force_reload)
        if path not in self._loaded_modules:
            self._loaded_modules.append(path)

    def _load_actors(self, force_reload=False):
        self._loaded_actors = {}
        for actor_name in self.list_actors():
            actor_info = self._get_actor_info(actor_name)
            self._load_module(actor_info["path"], force_reload=force_reload)
            self._loaded_actors[actor_name] = ActorProxy(actor_name, actor_info, self)

        self.actors = ActorsCollection(self._loaded_actors)

    def _get_actor_info(self, actor_name):
        return self.execute(actor_name, "info", die=True).result

    def list_actors(self) -> list:
        """List actors

        Returns:
            list -- List of loaded actors
        """
        return self.execute("core", "list_actors", die=True).result

    def reload(self):
        """Reload actors
        """
        self._load_actors(force_reload=True)

    def execute(self, actor_name: str, actor_method: str, *args, die: bool = False, **kwargs) -> ActorResult:
        """Execute actor's method

        Arguments:
            actor_name {str} -- actor name
            actor_method {str} -- actor method

        Keyword Arguments:
            die {bool} --  flag to raise an error when request fails (default: {False})

        Raises:
            RemoteException: Raises if the request failed and raise_on_error flag is set

        Returns:
            ActorResult -- request result
        """
        payload = json.dumps((args, kwargs), default=serialize)
        response = self.redis_client.execute_command(actor_name, actor_method, payload)

        deserializer = deserialize if not self.disable_deserialization else None
        response = json.loads(response, object_hook=deserializer)

        if not response["success"]:
            if die or self.raise_on_error:
                raise RemoteException(response["error"])

            response["error_type"] = GedisErrorTypes(response["error_type"])

        return ActorResult(**response)


class RemoteException(Exception):
    pass
