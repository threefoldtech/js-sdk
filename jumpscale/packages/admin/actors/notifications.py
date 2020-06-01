from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j


class Notifications(BaseActor):

    @actor_method
    def check_new_release(self) -> str:
        return "hello from admin's actor"

Actor = Notifications