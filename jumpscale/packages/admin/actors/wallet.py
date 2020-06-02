from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j

class Wallet(BaseActor):

    @actor_method
    def create_wallet(self, name: str) -> str:
        return "hello from admin's actor"

    @actor_method
    def manage_wallet(self, name: str) -> str:
        return "hello from admin's actor"

    @actor_method
    def get_wallets(self) -> str:
        return "hello from admin's actor"

    @actor_method
    def update_trustlines(self, name: str) -> str:
        return "hello from admin's actor"
    
    @actor_method
    def import_wallet(self, name: str, secret: str, network: str) -> str:
        return "hello from admin's actor"

    @actor_method
    def delete_wallet(self, name: str) -> str:
        return "hello from admin's actor"

Actor = Wallet
