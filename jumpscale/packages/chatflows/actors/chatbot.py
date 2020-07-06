from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.loader import j
import base64
import sys
import uuid
import imp


class ChatFlows(BaseActor):
    def __init__(self):
        super().__init__()
        self.chats = {}
        self.sessions = {}

    @actor_method
    def new(self, package: str, chat: str, client_ip: str, query_params: dict = None) -> dict:
        package = self.chats.get(package)
        if not package:
            raise j.exceptions.Value(f"Package {package} not found")

        chatflow = package.get(chat)
        if not chatflow:
            raise j.exceptions.Value(f"Chat {chat} not found")

        obj = chatflow()
        self.sessions[obj.session_id] = obj
        return {"sessionId": obj.session_id, "title": obj.title}

    @actor_method
    def fetch(self, session_id: str, restore: bool = False) -> dict:
        chatflow = self.sessions.get(session_id)
        if not chatflow:
            return {"payload": {"category": "end"}}

        result = chatflow.get_work(restore)

        if result.get("category") == "end":
            self.sessions.pop(session_id)

        return result

    @actor_method
    def report(self, session_id: str, result: str = None):
        chatflow = self.sessions.get(session_id)
        chatflow.set_work(result)

    @actor_method
    def back(self, session_id: str):
        chatflow = self.sessions.get(session_id)
        chatflow.go_back()

    @actor_method
    def chatflows_list(self) -> list:
        return list(self.chats.keys())

    def _scan_chats(self, path):
        package = j.sals.fs.basename(j.sals.fs.parent(path))
        for path in j.sals.fs.walk_files(path, recursive=False):
            if path.endswith(".py"):
                name = j.sals.fs.basename(path)[:-3]
                yield path, package, name

    @actor_method
    def load(self, path: str):
        for path, package, chat in self._scan_chats(path):
            module = imp.load_source(name=chat, pathname=path)
            if package not in self.chats:
                self.chats[package] = {}

            self.chats[package][chat] = module.chat

    @actor_method
    def unload(self, path: str):
        for _, package, chat in self._scan_chats(path):
            self.chats[package].pop(chat)


Actor = ChatFlows
