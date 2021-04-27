import os
import sys
import json
import inspect
from jumpscale.loader import j
from jumpscale.servers.gedis.baseactor import BaseActor, actor_method


class CoreActor(BaseActor):
    def __init__(self):
        super().__init__()
        self._server = None
        self.path = __file__

    def set_server(self, server):
        self._server = server

    @actor_method
    def list_actors(self) -> list:
        """List available actors

        Returns:
            list -- list of available actors
        """
        return list(self._server._loaded_actors.keys())


class SystemActor(BaseActor):
    def __init__(self):
        super().__init__()
        self._server = None
        self.path = __file__

    def set_server(self, server):
        self._server = server

    @actor_method
    def register_actor(self, actor_name: str, actor_path: str, force_reload: bool = False) -> bool:
        """
        Register new actor

        Args:
            actor_name (str): actor name within gedis server.
            actor_path (str): actor path on gedis server machine.
            force_reload (bool, optional): reload the module if set. Defaults to False.

        Raises:
            j.exceptions.Validation: in case the actor is not valid

        Returns:
            bool: True if registered
        """
        module = j.tools.codeloader.load_python_module(actor_path, force_reload=force_reload)
        actor = module.Actor()
        actor.path = actor_path
        result = actor.__validate_actor__()

        if not result["valid"]:
            raise j.exceptions.Validation(
                "Actor {} is not valid, check the following errors {}".format(actor_name, result["errors"])
            )

        self._server._register_actor(actor_name, actor)
        return True

    @actor_method
    def unregister_actor(self, actor_name: str) -> bool:
        """Register actor

        Arguments:
            actor_name {str} -- actor name

        Returns:
            bool -- True if actors is unregistered
        """
        self._server._unregister_actor(actor_name)
        return True
