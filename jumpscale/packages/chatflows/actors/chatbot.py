from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j
import base64
import sys
import uuid
import imp


class ChatFlows(BaseActor):
    def __init__(self):
        self.chats = {}
        self.sessions = {}

    @actor_method
    def new(self, topic: str, client_ip: str, query_params: dict = None) -> dict:
        chatflow = self.chats[topic]()
        self.sessions[chatflow.session_id] = chatflow
        return {"sessionId": chatflow.session_id}

    @actor_method
    def fetch(self, session_id: str) -> dict:
        chatflow = self.sessions.get(session_id)
        return chatflow.get_work()
    
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
        for path in j.sals.fs.walk_files(path, recursive=False):
            if path.endswith(".py"):
                name = j.sals.fs.basename(path)[:-3]                
                yield path, name

    @actor_method
    def load(self, path: str):
        for path, name in self._scan_chats(path):            
            module = imp.load_source(name=name, pathname=path)
            self.chats[name] = module.chat

    @actor_method
    def unload(self, path: str):
        for path, name in self._scan_chats(path):            
            sys.modules.pop(name)
            self.chats.pop(name)


Actor = ChatFlows
