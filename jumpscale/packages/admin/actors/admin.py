from jumpscale.servers.gedis.baseactor import BaseActor, actor_method
from jumpscale.god import j

explorers = {"main": "explorer.grid.tf", "testnet": "explorer.testnet.grid.tf"}

class Admin(BaseActor):

    @actor_method
    def admin_list(self) -> str:
        return "hello from admin_list actor"

    @actor_method
    def admin_add(self, name: str) -> str:
        return "hello from admin_add actor"

    @actor_method
    def admin_delete(self, name: str) -> str:
        return "hello from admin_delete actor"

    @actor_method
    def get_explorer(self) -> str:
        """
        Get current explorer (testnet/main)
        """

        config = j.core.config.get_config()
        # TODO: Check for explorer in config. default_addr_set() is not yet implemented
        # if "explorer_url" not in config['threebot']:
        #     j.clients.explorer.default_addr_set(explorers["testnet"])
        #     return self.explorer_to_json("testnet")

        current_address = config['threebot']["explorer_url"].strip().lower().split("/")[2]
        if current_address == explorers["testnet"]:
            explorer_type = "testnet"
        elif current_address == explorers["main"]:
            explorer_type = "main"
        else:
            return j.data.serializers.json.dumps(
                {"type": "custom", "url": current_address})
        return j.data.serializers.json.dumps(
            {"type": explorer_type, "url": explorers[explorer_type]})

    @actor_method
    def set_explorer(self, explorer_type: str) -> str:
        return "hello from set_explorer actor"

Actor = Admin
