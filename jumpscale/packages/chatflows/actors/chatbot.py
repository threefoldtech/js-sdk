from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.sals.chatflows.decorators import CreateSessionDecorator, DeleteSessionDecorator, UpdateSessionDecorator
from jumpscale.loader import j
import base64
import sys
import uuid
import importlib
import os


class ChatFlows(BaseActor):
    def __init__(self):
        super().__init__()
        self.chats = {}
        self.sessions = {}
        self.username = None

    @actor_method
    def new(self, package: str, chat: str, username: str, client_ip: str, query_params: dict = None) -> dict:
        package_object = self.chats.get(package)
        if not package_object:
            raise j.exceptions.Value(f"Package {package} not found")

        chatflow = package_object.get(chat)
        if not chatflow:
            raise j.exceptions.Value(f"Chat {chat} not found")

        if query_params is None:
            query_params = {}
        obj = chatflow(**query_params)
        key = f"{username}_{package}_{chat}"
        with CreateSessionDecorator(key):
            self.sessions[key] = obj
            return {"sessionId": obj.session_id, "title": obj.title}

    @actor_method
    def fetch(self, session_id: str, package: str, chat: str, username: str, restore: bool = False) -> dict:
        key = f"{username}_{package}_{chat}"
        chatflow = self.sessions.get(key)
        if not chatflow:
            return {"payload": {"category": "end"}}

        result = chatflow.get_work(restore)
        j.logger.debug(result)
        if result["payload"].get("category") == "end":
            with DeleteSessionDecorator(key):
                self.sessions.pop(key)
        else:
            with UpdateSessionDecorator(f"{key}/status", result, False):
                return result
        return result

    @actor_method
    def validate(self, session_id: str, username: str, package: str, chat: str) -> dict:
        self.username = username
        key = f"{self.username}_{package}_{chat}"
        # check the fs
        path = f"{j.core.dirs.CFGDIR}/chatflows/{key}"
        if j.sals.fs.is_dir(path):
            # TODO:
            # load from fs
            # self.sessions[key] = chatflow.load_from_path(path)
            # return {"valid": True}
            j.logger.debug("dir exists")
        return {"valid": key in self.sessions}

    @actor_method
    def end(self, session_id: str, username: str, package: str, chat: str) -> dict:
        key = f"{username}_{package}_{chat}"
        with DeleteSessionDecorator(key):
            return {"ended": True}

    @actor_method
    def report(self, session_id: str, package: str, chat: str, result: str = None):
        key = f"{self.username}_{package}_{chat}"
        chatflow = self.sessions.get(key)
        chatflow.set_work(key, result)

    @actor_method
    def back(self, session_id: str, package: str, chat: str):
        key = f"{self.username}_{package}_{chat}"
        chatflow = self.sessions.get(key)
        chatflow.go_back()

    @actor_method
    def chatflows_list(self) -> list:
        return list(self.chats.keys())

    def _scan_chats(self, path):
        package = j.sals.fs.basename(j.sals.fs.parent(path))
        for path in j.sals.fs.walk_files(path, recursive=False):
            if path.endswith(".py"):
                name = j.sals.fs.stem(path)
                yield path, package, name

    def _import_path(self, filepath):
        absolute_path = os.path.abspath(filepath)
        paths = sys.path[:]
        paths.sort(key=lambda p: len(p), reverse=True)
        for syspath in paths:
            absolute_sys_path = os.path.abspath(syspath)
            if absolute_path.startswith(absolute_sys_path):
                parts = absolute_path[len(absolute_sys_path) + 1 : -3].split(os.path.sep)
                if "__init__" in parts:
                    parts.remove("__init__")
                module_name = ".".join(parts)
                break
        else:
            module_name = absolute_path

        spec = importlib.util.spec_from_file_location(module_name, absolute_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    @actor_method
    def load(self, path: str):
        for path, package, chat in self._scan_chats(path):
            module = self._import_path(path)
            if package not in self.chats:
                self.chats[package] = {}

            self.chats[package][chat] = module.chat

    @actor_method
    def unload(self, path: str):
        for _, package, chat in self._scan_chats(path):
            self.chats[package].pop(chat)


Actor = ChatFlows
